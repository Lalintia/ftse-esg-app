"""Instant pre-check endpoint: URL/industry -> applicable indicator counts.

Answers "what would the analysis check?" in seconds, without crawling the
whole site or running the full (paid) assessment. With an explicit subsector
the response is pure KB lookup; with 'auto' it fetches only the homepage and
runs one small industry-detection call.
"""

import asyncio
import logging
import re

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI
from supabase import Client

from app.dependencies import get_openai, get_supabase
from app.limiter import limiter
from app.models.schemas import AnalysisRequest, PrecheckResponse, PrecheckTheme
from app.services.analyzer import _detect_subsector
from app.services.crawler import is_safe_url
from app.services.scoring import _get_pillar_for_theme
from app.utils.applicability import count_subparts_by_indicator, derive_applicable

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Precheck"])

_HOMEPAGE_TIMEOUT_S = 12.0
_HOMEPAGE_MAX_BYTES = 1_000_000
_TAG_RE = re.compile(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<[^>]+>")


async def _fetch_homepage_text(url: str) -> str:
    """Fetch the homepage and strip it to plain text for industry detection."""
    if not is_safe_url(url):
        raise HTTPException(status_code=400, detail="URL is not allowed.")

    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=_HOMEPAGE_TIMEOUT_S
        ) as client:
            response = await client.get(url)
    except httpx.HTTPError as exc:
        logger.warning("Precheck homepage fetch failed for %s: %s", url, exc)
        raise HTTPException(
            status_code=422,
            detail="Could not fetch the website homepage.",
        ) from exc

    # Redirects may land on a different host — re-validate before reading
    if not is_safe_url(str(response.url)):
        raise HTTPException(status_code=400, detail="URL is not allowed.")

    html = response.text[:_HOMEPAGE_MAX_BYTES]
    text = _TAG_RE.sub(" ", html)
    return re.sub(r"\s+", " ", text).strip()


async def _resolve_subsector(
    body: AnalysisRequest,
    openai_client: AsyncOpenAI,
) -> tuple[str, bool]:
    """Return (subsector_code, was_auto_detected)."""
    if body.subsector_code != "auto":
        return body.subsector_code, False

    content = await _fetch_homepage_text(str(body.company_url))
    if not content:
        raise HTTPException(
            status_code=422,
            detail="Homepage has no readable content for industry detection.",
        )
    detected = await _detect_subsector(openai_client, content)
    if not detected:
        raise HTTPException(
            status_code=422,
            detail="Could not auto-detect the industry from the homepage.",
        )
    return detected, True


@router.post("/precheck", response_model=PrecheckResponse)
@limiter.limit("10/minute")
async def precheck(
    request: Request,
    body: AnalysisRequest,
    supabase: Client = Depends(get_supabase),
    openai_client: AsyncOpenAI = Depends(get_openai),
) -> PrecheckResponse:
    """Report what a full analysis would check for this URL/industry.

    Returns theme/indicator/sub-indicator counts derived from the KB,
    without running the full assessment.

    Raises:
        HTTPException: If the subsector code is unknown or, in auto mode,
            the homepage cannot be fetched or classified.
    """
    subsector_code, auto_detected = await _resolve_subsector(body, openai_client)

    subsector_row = await asyncio.to_thread(
        lambda: supabase.table("icb_subsectors")
        .select("code, name, industry_name")
        .eq("code", subsector_code)
        .limit(1)
        .execute()
    )
    if not subsector_row.data:
        raise HTTPException(status_code=400, detail="Invalid subsector code.")

    applicability = derive_applicable(subsector_code)
    subpart_counts = count_subparts_by_indicator(subsector_code)

    themes: list[PrecheckTheme] = []
    total_subparts = 0
    for theme, indicators in applicability.indicators_by_theme.items():
        # Indicators without an explicit subpart entry count as one question
        theme_subparts = sum(
            subpart_counts.get(ind["indicator_code"], 1) for ind in indicators
        )
        total_subparts += theme_subparts
        themes.append(PrecheckTheme(
            theme_name=theme,
            pillar=_get_pillar_for_theme(theme),
            exposure=applicability.theme_exposures.get(theme, "Medium"),
            indicator_count=len(indicators),
            subpart_count=theme_subparts,
            zero_indicator=False,
        ))
    for zt in applicability.zero_indicator_themes:
        themes.append(PrecheckTheme(
            theme_name=zt["theme"],
            pillar=_get_pillar_for_theme(zt["theme"]),
            exposure=zt["exposure"],
            indicator_count=0,
            subpart_count=0,
            zero_indicator=True,
        ))
    themes.sort(key=lambda t: (t.pillar, t.theme_name))

    return PrecheckResponse(
        company_url=str(body.company_url),
        subsector_code=subsector_code,
        subsector_name=str(subsector_row.data[0]["name"]),
        industry_name=str(subsector_row.data[0].get("industry_name") or ""),
        auto_detected=auto_detected,
        total_themes=len(themes),
        total_indicators=applicability.total_indicators,
        total_sub_indicators=total_subparts,
        themes=themes,
    )
