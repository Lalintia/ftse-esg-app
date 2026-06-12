"""Analysis API endpoints."""

import asyncio
import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from supabase import Client

from app.dependencies import get_supabase
from app.limiter import limiter
from app.models.schemas import AnalysisCreateResponse, AnalysisRequest
from app.services.analyzer import run_analysis
from app.services.crawler import is_safe_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("", status_code=201, response_model=AnalysisCreateResponse)
@limiter.limit("5/minute")
async def create_analysis(
    request: Request,
    body: AnalysisRequest,
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase),
) -> dict[str, str]:
    """Create a new analysis and start background processing.

    Args:
        body: Request body with company_url and subsector_code.
        background_tasks: FastAPI background tasks injector.
        supabase: Supabase client injected via Depends.

    Returns:
        Dict with analysis_id and status.

    Raises:
        HTTPException: If subsector code is invalid or database insert fails.
    """
    company_url = str(body.company_url)

    # SSRF protection: block private/internal IPs
    if not is_safe_url(company_url):
        raise HTTPException(
            status_code=400,
            detail="URL resolves to a private or internal address. Only public URLs are allowed.",
        )

    # Look up subsector (skip for "auto" — will be detected during analysis)
    subsector_id: str | None = None
    subsector_code_to_use: str | None = body.subsector_code

    if body.subsector_code != "auto":
        subsector_result = await asyncio.to_thread(
            lambda: supabase.table("icb_subsectors")
            .select("id")
            .eq("code", body.subsector_code)
            .limit(1)
            .execute()
        )
        if subsector_result.data:
            subsector_id = subsector_result.data[0]["id"]
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid subsector code.",
            )
    else:
        subsector_code_to_use = None

    # Create analysis record
    try:
        insert_data: dict[str, str | None] = {
            "company_url": company_url,
            "status": "pending",
            "subsector_id": subsector_id,
        }

        result = await asyncio.to_thread(
            lambda: supabase.table("analyses").insert(insert_data).execute()
        )
        analysis_id = result.data[0]["id"]
    except Exception as exc:
        logger.error("Failed to create analysis: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to create analysis record.",
        ) from exc

    # Kick off background analysis
    background_tasks.add_task(
        _run_analysis_wrapper,
        analysis_id=analysis_id,
        company_url=company_url,
        subsector_code=subsector_code_to_use,
    )

    # Keep only the latest 20 analyses — delete oldest beyond limit
    _MAX_ANALYSES = 20
    try:
        old = await asyncio.to_thread(
            lambda: supabase.table("analyses")
            .select("id")
            .order("created_at", desc=True)
            .range(_MAX_ANALYSES, _MAX_ANALYSES + 100)
            .execute()
        )
        if old.data:
            old_ids = [row["id"] for row in old.data]
            await asyncio.to_thread(
                lambda: supabase.table("analyses").delete().in_("id", old_ids).execute()
            )
            logger.info("Cleaned up %d old analyses (keeping latest %d)", len(old_ids), _MAX_ANALYSES)
    except Exception as cleanup_exc:
        logger.warning("Failed to clean up old analyses: %s", cleanup_exc)

    logger.info("Analysis %s created for %s", analysis_id, company_url)

    return {
        "analysis_id": analysis_id,
        "status": "pending",
        "message": "Analysis started. Poll GET /api/analyses/{id} for progress.",
    }


async def _run_analysis_wrapper(
    analysis_id: str,
    company_url: str,
    subsector_code: str | None,
) -> None:
    """Wrapper to run async analysis in background task.

    Args:
        analysis_id: UUID of the analysis.
        company_url: Company website URL.
        subsector_code: Optional ICB subsector code.
    """
    try:
        await run_analysis(
            analysis_id=analysis_id,
            company_url=company_url,
            subsector_code=subsector_code,
        )
    except Exception as exc:
        logger.error(
            "Background analysis %s failed unexpectedly: %s",
            analysis_id,
            exc,
            exc_info=True,
        )


@router.get("")
async def list_analyses(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    supabase: Client = Depends(get_supabase),
) -> dict[str, list[dict[str, str | float | int | None]] | int]:
    """List all analyses ordered by creation date (newest first).

    Args:
        limit: Maximum number of results to return.
        offset: Number of results to skip.
        supabase: Supabase client injected via Depends.

    Returns:
        Dict with analyses list and total count.
    """

    # Get total count (limit 0 to avoid fetching rows)
    count_result = await asyncio.to_thread(
        lambda: supabase.table("analyses")
        .select("id", count="exact")
        .limit(0)
        .execute()
    )
    total = count_result.count or 0

    # Get paginated results
    result = await asyncio.to_thread(
        lambda: supabase.table("analyses")
        .select(
            "id, company_name, company_url, status, overall_score, "
            "environmental_score, social_score, governance_score, "
            "ifrs_s1_score, ifrs_s2_score, pages_crawled, "
            "status_message, error_message, started_at, completed_at, created_at"
        )
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    return {
        "analyses": result.data,
        "total": total,
    }


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: UUID,
    supabase: Client = Depends(get_supabase),
):
    """Get full analysis details including results.

    Args:
        analysis_id: UUID of the analysis.
        supabase: Supabase client injected via Depends.

    Returns:
        Dict with analysis info, FTSE results, IFRS results, and sitemap.

    Raises:
        HTTPException: If analysis not found.
    """
    analysis_id_str = str(analysis_id)

    # Fetch analysis record first (needed to 404 early if missing)
    analysis_result = await asyncio.to_thread(
        lambda: supabase.table("analyses")
        .select("*")
        .eq("id", analysis_id_str)
        .limit(1)
        .execute()
    )

    if not analysis_result.data:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    analysis = analysis_result.data[0]

    async def _fetch_ftse() -> object:
        try:
            return await asyncio.to_thread(
                lambda: supabase.table("analysis_ftse_results")
                .select(
                    "id, status, score, evidence, confidence, ai_reasoning, "
                    "source_url, source_page_title, "
                    "ftse_indicators(indicator_code, indicator_name, theme_id, "
                    "ftse_themes(theme_name, pillar, pillar_code))"
                )
                .eq("analysis_id", analysis_id_str)
                .execute()
            )
        except Exception:
            logger.warning("Join query failed for FTSE results, using simple query", exc_info=True)
            return await asyncio.to_thread(
                lambda: supabase.table("analysis_ftse_results")
                .select("id, indicator_id, status, score, evidence, confidence, ai_reasoning, source_url, source_page_title")
                .eq("analysis_id", analysis_id_str)
                .execute()
            )

    async def _fetch_ifrs() -> object:
        try:
            return await asyncio.to_thread(
                lambda: supabase.table("analysis_ifrs_results")
                .select(
                    "id, status, evidence, confidence, ai_reasoning, "
                    "ifrs_requirements(paragraph_ref, standard, chapter, "
                    "section, requirement_text, is_mandatory)"
                )
                .eq("analysis_id", analysis_id_str)
                .execute()
            )
        except Exception:
            logger.warning("Join query failed for IFRS results, using simple query")
            return await asyncio.to_thread(
                lambda: supabase.table("analysis_ifrs_results")
                .select("id, requirement_id, status, evidence, confidence, ai_reasoning")
                .eq("analysis_id", analysis_id_str)
                .execute()
            )

    async def _fetch_sitemap() -> object:
        return await asyncio.to_thread(
            lambda: supabase.table("sitemap_recommendations")
            .select("*")
            .eq("analysis_id", analysis_id_str)
            .order("priority")
            .execute()
        )

    # Run 3 independent DB queries in parallel
    ftse_results, ifrs_results, sitemap_results = await asyncio.gather(
        _fetch_ftse(),
        _fetch_ifrs(),
        _fetch_sitemap(),
    )

    return {
        "analysis": analysis,
        "ftse_results": ftse_results.data,
        "ifrs_results": ifrs_results.data,
        "sitemap_recommendations": sitemap_results.data,
    }
