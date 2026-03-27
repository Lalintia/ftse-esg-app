"""Main analysis orchestrator — coordinates crawl, analysis, scoring, and storage."""

import asyncio
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from supabase import Client

from app.dependencies import get_openai, get_supabase
from app.services.crawler import PageContent, crawl_website
from app.services.ftse_analyzer import FtseResult, analyze_ftse
from app.services.ifrs_analyzer import IfrsResult, analyze_ifrs
from app.services.scoring import (
    VALID_STATUSES,
    FtseScores,
    IfrsScores,
    calculate_ftse_scores,
    calculate_ifrs_scores,
)
from app.services.sitemap_generator import SitemapRecommendation, generate_sitemap
from app.utils.data_loader import (
    get_indicators_by_theme,
    get_requirements_by_chapter,
    load_ftse_indicators,
    load_ifrs_requirements,
)
from app.utils.sector_themes import get_applicable_themes

logger = logging.getLogger(__name__)

# Industry detection prompt for auto-detect
_INDUSTRY_DETECT_PROMPT = """You are an ICB (Industry Classification Benchmark) expert.

Analyze this company website content and determine the most appropriate ICB subsector.

Return ONLY a JSON object with:
- "subsector_code": the 8-digit ICB subsector code (e.g. "45102020" for Food Products)
- "industry": short industry name in English
- "confidence": 0.0-1.0

Common ICB subsector codes:
- 60101010: Oil & Gas Producers
- 65101010: Electricity
- 55101010: Industrial Metals & Mining
- 45102020: Food Products
- 45201020: Personal Goods
- 20103010: Pharmaceuticals
- 30101010: Banks
- 35102010: Real Estate Investment & Services
- 10101015: Software
- 15101010: Telecommunications
- 40201020: General Retailers
- 40501020: Restaurants & Bars
- 50101010: Industrial Transportation
- 40101010: Automobiles
- 50201030: Electronic & Electrical Equipment
- 55201010: Chemicals
- 50201010: Construction & Materials
- 60102020: Alternative Energy
- 15104025: Media
- 65102020: Gas, Water & Multi-utilities

Website content (first 3000 chars):
"""


async def _detect_subsector(openai_client, website_content: str) -> str | None:
    """Auto-detect ICB subsector from crawled website content.

    Args:
        openai_client: AsyncOpenAI client.
        website_content: Concatenated website content.

    Returns:
        Detected ICB subsector code, or None if detection fails.
    """
    import json as _json
    from app.config import get_settings
    settings = get_settings()

    snippet = website_content[:3000]
    try:
        response = await openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _INDUSTRY_DETECT_PROMPT},
                {"role": "user", "content": snippet},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            timeout=120.0,
        )
        raw = response.choices[0].message.content or "{}"
        data = _json.loads(raw)
        code = data.get("subsector_code", "")
        industry = data.get("industry", "unknown")
        confidence = data.get("confidence", 0)

        usage = response.usage
        if usage:
            logger.info(
                "Industry detection tokens — input: %d, output: %d",
                usage.prompt_tokens,
                usage.completion_tokens,
            )

        logger.info(
            "Auto-detected industry: %s (code: %s, confidence: %.2f)",
            industry, code, confidence,
        )
        if code and len(code) >= 4:
            return code
        return None
    except Exception as exc:
        logger.error("Industry auto-detection failed: %s", exc)
        return None

# Titles containing these words are not useful for company name extraction
_SKIP_TITLE_WORDS = [
    "cookie", "privacy", "terms", "policy", "404", "error", "login",
    "whistleblow", "อนุรักษ์", "กิจกรรม", "ข่าวสาร", "ติดต่อ",
    "sitemap", "search", "register", "sign in", "forgot",
    "csr news", "news archive", "blog", "contact", "career",
    "สมัครงาน", "ร่วมงาน", "แผนที่", "ประกาศ",
]


def _is_usable_title(title: str) -> bool:
    """Check if a page title is likely a company name, not a content page.

    Args:
        title: Page title string.

    Returns:
        True if the title does not match skip patterns.
    """
    lower = title.lower()
    return not any(word in lower for word in _SKIP_TITLE_WORDS)


def _extract_name_from_title(raw_title: str) -> str:
    """Extract company name from a page title by splitting on separators.

    Picks the shortest part after splitting on | - etc., since the
    company name is usually shorter than the tagline/description.

    Args:
        raw_title: Raw page title string.

    Returns:
        Extracted company name.
    """
    for separator in [" | ", " - ", " – ", " — "]:
        if separator in raw_title:
            parts = [p.strip() for p in raw_title.split(separator) if p.strip()]
            if not parts:
                continue
            shortest = min(parts, key=len)
            if len(shortest) >= 2:
                return shortest
            return parts[0]
    return raw_title.strip()


def _extract_name_from_domain(url: str) -> str:
    """Extract a company name from the domain as a last resort.

    Examples:
        www.scb.co.th -> SCB
        www.pttgc.com -> PTTGC

    Args:
        url: Company website URL.

    Returns:
        Uppercased domain-based name.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    # Remove www. prefix
    hostname = re.sub(r"^www\.", "", hostname)
    # Take the first part before .co, .com, etc.
    name_part = hostname.split(".")[0] if hostname else ""
    return name_part.upper()


def _looks_like_company_name(name: str) -> bool:
    """Check if extracted name looks like a real company name.

    A good company name is typically short (under 60 chars) and doesn't
    contain generic content page words.

    Args:
        name: Candidate company name.

    Returns:
        True if the name looks like a company name.
    """
    if len(name) > 60 or len(name) < 2:
        return False
    generic_words = [
        "news", "archive", "article", "page", "home", "welcome",
        "about us", "our story", "overview", "annual report",
        "sustainability report", "csr report",
    ]
    lower = name.lower()
    return not any(word in lower for word in generic_words)


def _extract_company_name(
    pages: list[PageContent],
    base_url: str,
) -> str | None:
    """Extract the company name from crawled pages.

    Strategy:
    1. Find the homepage (URL closest to base URL).
    2. If the homepage title looks like a company name, use it.
    3. If not, look for a common company name across multiple page titles.
    4. As a last resort, extract from the domain name.

    Args:
        pages: List of crawled pages.
        base_url: The original company URL.

    Returns:
        Extracted company name, or None if no pages available.
    """
    if not pages:
        return None

    clean_base = base_url.rstrip("/")

    # Find homepage — URL that matches base URL most closely
    homepage: PageContent | None = None
    for page in pages:
        page_clean = page.url.rstrip("/")
        if page_clean == clean_base or page_clean in (
            f"{clean_base}/en",
            f"{clean_base}/th",
            f"{clean_base}/index.html",
        ):
            homepage = page
            break

    if not homepage:
        homepage = pages[0]

    # Try homepage title first
    raw_title = homepage.title.strip()
    if raw_title and raw_title != homepage.url and _is_usable_title(raw_title):
        name = _extract_name_from_title(raw_title)
        if _looks_like_company_name(name):
            return name

    # Look for a common company name across page titles
    # Many pages have format: "Page Title | Company Name"
    # The company name part repeats across pages
    from collections import Counter
    name_candidates: list[str] = []
    for page in pages[:15]:
        title = page.title.strip()
        if not title or title == page.url:
            continue
        for separator in [" | ", " - ", " – ", " — "]:
            if separator in title:
                parts = [p.strip() for p in title.split(separator) if p.strip()]
                name_candidates.extend(parts)
                break

    if name_candidates:
        counts = Counter(name_candidates)
        most_common_name, most_common_count = counts.most_common(1)[0]
        if most_common_count >= 2 and _looks_like_company_name(most_common_name):
            return most_common_name

    # Fallback: scan for any usable title
    for page in pages[:10]:
        title = page.title.strip()
        if title and title != page.url and _is_usable_title(title):
            name = _extract_name_from_title(title)
            if _looks_like_company_name(name):
                return name

    # Last resort: extract from domain
    return _extract_name_from_domain(base_url)


def _update_status(
    supabase: Client,
    analysis_id: str,
    status: str,
    error_message: str | None = None,
    status_message: str | None = None,
) -> None:
    """Update the analysis status in the database.

    Args:
        supabase: Supabase client.
        analysis_id: UUID of the analysis.
        status: New status value.
        error_message: Optional error message if status is 'failed'.
        status_message: Optional human-readable progress message.
    """
    update_data: dict[str, str | None] = {"status": status}
    if status_message is not None:
        update_data["status_message"] = status_message
    if error_message:
        update_data["error_message"] = error_message
    if status == "completed" or status == "failed":
        update_data["completed_at"] = datetime.now(timezone.utc).isoformat()

    supabase.table("analyses").update(update_data).eq("id", analysis_id).execute()
    logger.info("Analysis %s status updated to: %s", analysis_id, status)


def _update_message(
    supabase: Client,
    analysis_id: str,
    message: str,
) -> None:
    """Update only the status_message field for live progress feedback.

    Args:
        supabase: Supabase client.
        analysis_id: UUID of the analysis.
        message: Human-readable progress message.
    """
    supabase.table("analyses").update(
        {"status_message": message}
    ).eq("id", analysis_id).execute()


def _save_ftse_results(
    supabase: Client,
    analysis_id: str,
    results: list[FtseResult],
    indicators: list[dict[str, str | bool]],
) -> None:
    """Save FTSE analysis results to the database.

    Args:
        supabase: Supabase client.
        analysis_id: UUID of the analysis.
        results: List of FtseResult from analysis.
        indicators: All FTSE indicators for looking up IDs.
    """
    # Look up indicator UUIDs from the database
    indicator_rows = (
        supabase.table("ftse_indicators")
        .select("id, indicator_code")
        .execute()
    )
    code_to_id: dict[str, str] = {
        row["indicator_code"]: row["id"]
        for row in indicator_rows.data
    }

    seen: dict[str, dict[str, str | float | int | None]] = {}
    for r in results:
        indicator_id = code_to_id.get(r.indicator_code)
        if not indicator_id:
            logger.warning("No DB record for indicator %s — skipping", r.indicator_code)
            continue

        status = r.status if r.status in VALID_STATUSES else "missing"

        seen[indicator_id] = {
            "analysis_id": analysis_id,
            "indicator_id": indicator_id,
            "status": status,
            "score": r.score,
            "evidence": r.evidence or None,
            "confidence": r.confidence,
            "ai_reasoning": r.reasoning or None,
        }

    rows = list(seen.values())
    if rows:
        batch_size = 50
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            supabase.table("analysis_ftse_results").upsert(
                batch, on_conflict="analysis_id,indicator_id"
            ).execute()
        logger.info("Saved %d FTSE results for analysis %s", len(rows), analysis_id)


def _save_ifrs_results(
    supabase: Client,
    analysis_id: str,
    results: list[IfrsResult],
) -> None:
    """Save IFRS analysis results to the database.

    Args:
        supabase: Supabase client.
        analysis_id: UUID of the analysis.
        results: List of IfrsResult from analysis.
    """
    # Look up requirement UUIDs from the database
    req_rows = (
        supabase.table("ifrs_requirements")
        .select("id, paragraph_ref")
        .execute()
    )
    ref_to_id: dict[str, str] = {
        row["paragraph_ref"]: row["id"]
        for row in req_rows.data
    }

    seen: dict[str, dict[str, str | float | None]] = {}
    for r in results:
        requirement_id = ref_to_id.get(r.paragraph_ref)
        if not requirement_id:
            logger.warning("No DB record for requirement %s — skipping", r.paragraph_ref)
            continue

        # Sanitize status — AI sometimes returns unexpected values
        status = r.status if r.status in VALID_STATUSES else "missing"

        seen[requirement_id] = {
            "analysis_id": analysis_id,
            "requirement_id": requirement_id,
            "status": status,
            "evidence": r.evidence or None,
            "confidence": r.confidence,
            "ai_reasoning": r.reasoning or None,
        }

    rows = list(seen.values())
    if rows:
        batch_size = 50
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            supabase.table("analysis_ifrs_results").upsert(
                batch, on_conflict="analysis_id,requirement_id"
            ).execute()
        logger.info("Saved %d IFRS results for analysis %s", len(rows), analysis_id)


def _save_scores(
    supabase: Client,
    analysis_id: str,
    ftse_scores: FtseScores,
    ifrs_scores: IfrsScores,
) -> None:
    """Save calculated scores to the analysis record.

    Args:
        supabase: Supabase client.
        analysis_id: UUID of the analysis.
        ftse_scores: Calculated FTSE scores.
        ifrs_scores: Calculated IFRS scores.
    """
    supabase.table("analyses").update({
        "overall_score": ftse_scores.overall_score,
        "environmental_score": ftse_scores.environmental_score,
        "social_score": ftse_scores.social_score,
        "governance_score": ftse_scores.governance_score,
        "ifrs_s1_score": ifrs_scores.s1_score,
        "ifrs_s2_score": ifrs_scores.s2_score,
    }).eq("id", analysis_id).execute()

    logger.info("Saved scores for analysis %s", analysis_id)


def _save_sitemap(
    supabase: Client,
    analysis_id: str,
    recommendations: list[SitemapRecommendation],
) -> None:
    """Save sitemap recommendations to the database.

    Args:
        supabase: Supabase client.
        analysis_id: UUID of the analysis.
        recommendations: List of SitemapRecommendation.
    """
    rows: list[dict[str, str | None]] = []
    for rec in recommendations:
        rows.append({
            "analysis_id": analysis_id,
            "recommended_page_title": rec.page_title,
            "recommended_page_path": rec.page_path,
            "reason": rec.reason,
            "priority": rec.priority,
        })

    if rows:
        supabase.table("sitemap_recommendations").insert(rows).execute()
        logger.info(
            "Saved %d sitemap recommendations for analysis %s",
            len(rows),
            analysis_id,
        )


def _extract_ftse_gaps(
    results: list[FtseResult],
    indicators_by_theme: dict[str, list[dict[str, str | bool]]],
) -> list[dict[str, str]]:
    """Extract FTSE gaps (missing/partial) for sitemap generation.

    Args:
        results: List of FtseResult.
        indicators_by_theme: Indicators grouped by theme.

    Returns:
        List of gap dicts with indicator_code, theme_name, indicator_name, status.
    """
    indicator_lookup: dict[str, dict[str, str]] = {}
    for theme_name, indicators in indicators_by_theme.items():
        for ind in indicators:
            indicator_lookup[ind["indicator_code"]] = {
                "theme_name": theme_name,
                "indicator_name": str(ind.get("indicator_name", "")),
            }

    gaps: list[dict[str, str]] = []
    for r in results:
        if r.status in ("missing", "partial"):
            info = indicator_lookup.get(r.indicator_code, {})
            gaps.append({
                "indicator_code": r.indicator_code,
                "theme_name": info.get("theme_name", "Unknown"),
                "indicator_name": info.get("indicator_name", ""),
                "status": r.status,
            })

    return gaps


def _extract_ifrs_gaps(
    results: list[IfrsResult],
    requirements: list[dict[str, str | bool | int]],
) -> list[dict[str, str]]:
    """Extract IFRS gaps (missing/partial) for sitemap generation.

    Args:
        results: List of IfrsResult.
        requirements: All IFRS requirements.

    Returns:
        List of gap dicts with paragraph_ref, standard, section, status.
    """
    req_lookup: dict[str, dict[str, str]] = {
        req["paragraph_ref"]: {
            "standard": str(req.get("standard", "")),
            "section": str(req.get("section", "")),
        }
        for req in requirements
    }

    gaps: list[dict[str, str]] = []
    for r in results:
        if r.status in ("missing", "partial"):
            info = req_lookup.get(r.paragraph_ref, {})
            gaps.append({
                "paragraph_ref": r.paragraph_ref,
                "standard": info.get("standard", "Unknown"),
                "section": info.get("section", ""),
                "status": r.status,
            })

    return gaps


async def run_analysis(
    analysis_id: str,
    company_url: str,
    subsector_code: str | None = None,
) -> None:
    """Run a full ESG analysis pipeline.

    Flow:
    1. Update status to 'crawling'
    2. Crawl the company website
    3. Update status to 'analyzing'
    4. Run FTSE + IFRS analysis in parallel
    5. Calculate scores
    6. Generate sitemap recommendations
    7. Save all results to database
    8. Update status to 'completed'

    On any error: set status='failed' with error_message.

    Args:
        analysis_id: UUID of the analysis record.
        company_url: Company website URL to analyze.
        subsector_code: Optional ICB subsector code for context.
    """
    supabase = get_supabase()
    openai_client = get_openai()

    try:
        # Step 1: Crawl
        _update_status(supabase, analysis_id, "crawling", status_message="Starting web crawler...")
        supabase.table("analyses").update({
            "started_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", analysis_id).execute()

        from app.config import get_settings
        settings = get_settings()

        def _crawl_progress(msg: str) -> None:
            _update_message(supabase, analysis_id, msg)

        crawl_result = await crawl_website(
            url=company_url,
            max_pages=settings.MAX_PAGES_TO_CRAWL,
            on_progress=_crawl_progress,
        )

        # Extract company name from homepage title
        company_name = _extract_company_name(
            pages=crawl_result.pages,
            base_url=company_url,
        )

        supabase.table("analyses").update({
            "pages_crawled": crawl_result.pages_crawled,
            "company_name": company_name,
            "status_message": f"Crawled {crawl_result.pages_crawled} pages from {company_name or company_url}",
        }).eq("id", analysis_id).execute()

        # Separate HTML pages from PDF pages
        html_pages = [
            p for p in crawl_result.pages
            if not p.title.startswith("PDF:")
        ]
        pdf_pages = [
            p for p in crawl_result.pages
            if p.title.startswith("PDF:")
        ]

        website_content = "\n\n---\n\n".join(
            f"# {page.title}\nSource: {page.url}\n\n{page.markdown_text}"
            for page in html_pages
        )

        pdf_content = "\n\n---\n\n".join(
            f"# {page.title}\nSource: {page.url}\n\n{page.markdown_text}"
            for page in pdf_pages
        ) if pdf_pages else ""

        logger.info(
            "Content split: %d HTML pages, %d PDF documents",
            len(html_pages), len(pdf_pages),
        )

        # Step 1.5: Auto-detect subsector if not provided
        if not subsector_code:
            logger.info("No subsector code — running auto-detection")
            _update_message(supabase, analysis_id, "Auto-detecting industry...")
            subsector_code = await _detect_subsector(openai_client, website_content)
            if subsector_code:
                # Update analysis record with detected subsector
                sub_result = (
                    supabase.table("icb_subsectors")
                    .select("id")
                    .eq("code", subsector_code)
                    .limit(1)
                    .execute()
                )
                if sub_result.data:
                    supabase.table("analyses").update({
                        "subsector_id": sub_result.data[0]["id"],
                    }).eq("id", analysis_id).execute()
                    logger.info("Updated analysis with auto-detected subsector: %s", subsector_code)
            else:
                logger.warning("Auto-detection failed — using all 381 indicators")

        # Step 2: Load reference data
        ftse_indicators = load_ftse_indicators()
        ifrs_requirements = load_ifrs_requirements()
        indicators_by_theme = get_indicators_by_theme()
        requirements_by_chapter = get_requirements_by_chapter()

        # Filter indicators by subsector mapping (theme applicability + indicator-subsector)
        zero_indicator_themes_list: list[dict[str, str]] = []
        if subsector_code:
            applicable_themes = get_applicable_themes(subsector_code)
            applicable_theme_names = {t["theme"] for t in applicable_themes}
            all_theme_count = sum(
                len(inds) for inds in indicators_by_theme.values()
            )

            # Load indicator-subsector mapping
            from pathlib import Path
            import json as _json
            mapping_path = Path(__file__).resolve().parent.parent.parent / "data" / "indicator_subsector_mapping.json"
            indicator_mapping: dict[str, dict] = {}
            if mapping_path.exists():
                with open(mapping_path, encoding="utf-8") as f:
                    indicator_mapping = _json.load(f)

            # Build lookup for themes with indicators_applicable=False
            # (e.g., Climate Change for Oil & Gas: theme applies but 0 indicators)
            no_indicator_themes: set[str] = set()
            for t in applicable_themes:
                if not t.get("indicators_applicable", True):
                    no_indicator_themes.add(t["theme"])

            filtered_by_theme: dict[str, list[dict[str, str | bool]]] = {}
            for theme, inds in indicators_by_theme.items():
                if theme not in applicable_theme_names:
                    continue
                if theme in no_indicator_themes:
                    continue

                applicable_inds: list[dict[str, str | bool]] = []
                for ind in inds:
                    code = ind["indicator_code"]
                    m = indicator_mapping.get(code, {"type": "core", "subsectors": []})

                    # Check exclude_subsectors (indicators NAP for specific subsectors)
                    exclude = m.get("exclude_subsectors", [])
                    if any(subsector_code.startswith(s) or s == subsector_code for s in exclude):
                        continue

                    if m["type"] in ("core", "performance"):
                        applicable_inds.append(ind)
                    else:
                        subs = m.get("subsectors", [])
                        if any(subsector_code.startswith(s) or s == subsector_code for s in subs):
                            applicable_inds.append(ind)

                if applicable_inds:
                    filtered_by_theme[theme] = applicable_inds

            filtered_count = sum(
                len(inds) for inds in filtered_by_theme.values()
            )

            # Collect zero-indicator themes for scoring (FTSE minimum score = 1)
            zero_indicator_themes_list = [
                {"theme": t["theme"], "exposure": t["exposure"]}
                for t in applicable_themes
                if not t.get("indicators_applicable", True)
            ]

            logger.info(
                "Subsector %s: evaluating %d/%d indicators across %d/%d themes"
                " (%d zero-indicator themes)",
                subsector_code,
                filtered_count,
                all_theme_count,
                len(filtered_by_theme),
                len(indicators_by_theme),
                len(zero_indicator_themes_list),
            )
            indicators_by_theme = filtered_by_theme

        # Step 3: Analyze FTSE + IFRS in parallel
        total_themes = len(indicators_by_theme)
        total_indicators = sum(len(inds) for inds in indicators_by_theme.values())
        has_pdf = bool(pdf_content)
        round_info = " (Round 1: website → Round 2: PDF for gaps)" if has_pdf else " (website only)"
        _update_status(
            supabase, analysis_id, "analyzing",
            status_message=f"Analyzing {total_indicators} indicators across {total_themes} themes{round_info}",
        )

        # FTSE: two-round (website first, PDF for gaps)
        # IFRS: temporarily disabled to save tokens (~20% cost reduction)
        logger.warning(
            "IFRS analysis disabled (cost saving). Scores will be zero for %s.",
            analysis_id,
        )
        ftse_results = await analyze_ftse(
            openai_client, website_content, indicators_by_theme, pdf_content=pdf_content,
        )
        ifrs_results: list[IfrsResult] = []

        # Step 4: Save raw results
        _update_message(supabase, analysis_id, f"Saving {len(ftse_results)} FTSE results...")
        _save_ftse_results(supabase, analysis_id, ftse_results, ftse_indicators)

        # Step 5: Calculate scores
        ftse_result_dicts = [
            {
                "indicator_code": r.indicator_code,
                "status": r.status,
                "score": r.score,
            }
            for r in ftse_results
        ]

        _update_message(supabase, analysis_id, "Calculating ESG scores...")
        ftse_scores = calculate_ftse_scores(
            ftse_result_dicts,
            indicators_by_theme,
            subsector_code=subsector_code,
            zero_indicator_themes=zero_indicator_themes_list if subsector_code else None,
        )
        ifrs_scores = calculate_ifrs_scores([], ifrs_requirements)
        _save_scores(supabase, analysis_id, ftse_scores, ifrs_scores)

        # Step 6: Generate sitemap recommendations
        _update_message(supabase, analysis_id, "Generating sitemap recommendations...")
        ftse_gaps = _extract_ftse_gaps(ftse_results, indicators_by_theme)

        recommendations = await generate_sitemap(
            openai_client=openai_client,
            ftse_gaps=ftse_gaps,
            ifrs_gaps=[],
        )
        _save_sitemap(supabase, analysis_id, recommendations)

        # Step 7: Complete
        _update_status(supabase, analysis_id, "completed", status_message="Analysis complete!")
        logger.info("Analysis %s completed successfully", analysis_id)

    except Exception as exc:
        logger.error("Analysis %s failed: %s", analysis_id, exc, exc_info=True)
        safe_msg = "Analysis failed due to an internal error. Please try again."
        if "SSRF" in str(exc):
            safe_msg = "The provided URL could not be accessed safely."
        elif isinstance(exc, httpx.TimeoutException):
            safe_msg = "Website took too long to respond. Please try again."
        try:
            _update_status(
                supabase,
                analysis_id,
                "failed",
                error_message=safe_msg,
            )
        except Exception as save_exc:
            logger.error(
                "Failed to save error status for analysis %s: %s",
                analysis_id,
                save_exc,
            )
