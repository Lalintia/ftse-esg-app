"""Sitemap recommendation generator using OpenAI."""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field

from openai import AsyncOpenAI, RateLimitError, APIStatusError, APITimeoutError

from app.config import get_settings
from app.prompts.sitemap_system import SITEMAP_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def _sanitize_prompt_field(text: str, max_len: int = 200) -> str:
    """Strip characters that could be used for prompt injection.

    Args:
        text: Raw text from crawled page metadata.
        max_len: Maximum allowed length.

    Returns:
        Sanitized text safe to include in AI prompts.
    """
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"[`*#\[\]<>{}\\]", "", text)
    return text[:max_len]


@dataclass
class SitemapRecommendation:
    """A recommended web page to create or enhance for ESG disclosure.

    Attributes:
        page_title: Page title (existing or suggested).
        page_path: URL path (existing or suggested).
        reason: Why this recommendation is needed.
        priority: high, medium, or low.
        addresses_gaps: List of indicator codes addressed.
        rec_type: "new" (create page) or "enhance" (add data to existing).
        existing_page_url: URL of existing page to enhance (empty if new).
        data_to_add: Specific data points to add.
    """

    page_title: str
    page_path: str
    reason: str
    priority: str
    addresses_gaps: list[str]
    rec_type: str = "new"
    existing_page_url: str = ""
    data_to_add: list[str] = field(default_factory=list)


def _build_gaps_summary(
    ftse_gaps: list[dict[str, str]],
    ifrs_gaps: list[dict[str, str]],
    existing_pages: list[dict[str, str]] | None = None,
) -> str:
    """Build a summary of gaps and existing pages for the AI prompt.

    Args:
        ftse_gaps: List of dicts with indicator_code, theme_name, indicator_name, status.
        ifrs_gaps: List of dicts with paragraph_ref, standard, section, status.
        existing_pages: List of dicts with url, title from crawled pages.

    Returns:
        Formatted text for the AI prompt.
    """
    lines: list[str] = []

    if existing_pages:
        lines.append("## Existing Pages on Company Website\n")
        for page in existing_pages:
            title = _sanitize_prompt_field(page.get("title", ""))
            url = _sanitize_prompt_field(page.get("url", ""), max_len=500)
            lines.append(f"- {title} → {url}")
        lines.append("")

    ftse_by_theme: dict[str, list[dict[str, str]]] = {}
    for gap in ftse_gaps:
        theme = gap.get("theme_name", "Unknown")
        if theme not in ftse_by_theme:
            ftse_by_theme[theme] = []
        ftse_by_theme[theme].append(gap)

    lines.append("## FTSE Russell Gaps\n")
    for theme, gaps in ftse_by_theme.items():
        lines.append(f"### {theme} ({len(gaps)} gaps)")
        for g in gaps:
            status_tag = f"[{g.get('status', 'missing').upper()}]"
            lines.append(
                f"- {g['indicator_code']}: {g.get('indicator_name', '')} {status_tag}"
            )
        lines.append("")

    ifrs_by_standard: dict[str, list[dict[str, str]]] = {}
    for gap in ifrs_gaps:
        std = gap.get("standard", "Unknown")
        if std not in ifrs_by_standard:
            ifrs_by_standard[std] = []
        ifrs_by_standard[std].append(gap)

    if ifrs_by_standard:
        lines.append("## IFRS S1/S2 Gaps\n")
        for std, gaps in ifrs_by_standard.items():
            lines.append(f"### {std} ({len(gaps)} gaps)")
            for g in gaps:
                status_tag = f"[{g.get('status', 'missing').upper()}]"
                lines.append(
                    f"- {g['paragraph_ref']}: {g.get('section', '')} {status_tag}"
                )
            lines.append("")

    return "\n".join(lines)


async def generate_sitemap(
    openai_client: AsyncOpenAI,
    ftse_gaps: list[dict[str, str]],
    ifrs_gaps: list[dict[str, str]],
    existing_pages: list[dict[str, str]] | None = None,
) -> list[SitemapRecommendation]:
    """Generate sitemap recommendations based on identified gaps.

    Args:
        openai_client: AsyncOpenAI client.
        ftse_gaps: FTSE indicators with missing/partial status.
        ifrs_gaps: IFRS requirements with missing/partial status.
        existing_pages: Crawled pages with url and title.

    Returns:
        List of SitemapRecommendation sorted by priority.
    """
    if not ftse_gaps and not ifrs_gaps:
        logger.info("No gaps found — skipping sitemap generation")
        return []

    settings = get_settings()
    gaps_summary = _build_gaps_summary(ftse_gaps, ifrs_gaps, existing_pages)

    logger.info(
        "Generating sitemap recommendations for %d FTSE + %d IFRS gaps (%d existing pages)",
        len(ftse_gaps),
        len(ifrs_gaps),
        len(existing_pages) if existing_pages else 0,
    )

    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            response = await openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SITEMAP_SYSTEM_PROMPT},
                    {"role": "user", "content": gaps_summary},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                timeout=120.0,
            )
            break
        except (RateLimitError, APITimeoutError) as retry_exc:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                logger.warning("Sitemap generation retry in %ds: %s", wait_time, type(retry_exc).__name__)
                await asyncio.sleep(wait_time)
            else:
                raise
        except APIStatusError as retry_exc:
            if retry_exc.status_code in (429, 502, 503) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                logger.warning("Sitemap generation retry in %ds: status %d", wait_time, retry_exc.status_code)
                await asyncio.sleep(wait_time)
            else:
                raise

    if response is None:
        logger.error("Sitemap generation: no response after %d retries", max_retries)
        return []

    try:

        raw_text = response.choices[0].message.content or "{}"
        data = json.loads(raw_text)
        raw_recs: list[dict] = data.get("recommendations", [])

        recommendations: list[SitemapRecommendation] = []
        for rec in raw_recs:
            priority = str(rec.get("priority", "medium"))
            if priority not in {"high", "medium", "low"}:
                priority = "medium"

            addresses = rec.get("addresses_gaps", [])
            if not isinstance(addresses, list):
                addresses = []

            data_to_add = rec.get("data_to_add", [])
            if not isinstance(data_to_add, list):
                data_to_add = []

            rec_type = str(rec.get("type", "new"))
            if rec_type not in {"new", "enhance"}:
                rec_type = "new"

            recommendations.append(SitemapRecommendation(
                page_title=str(rec.get("page_title", "")),
                page_path=str(rec.get("page_path", "")),
                reason=str(rec.get("reason", "")),
                priority=priority,
                addresses_gaps=[str(g) for g in addresses],
                rec_type=rec_type,
                existing_page_url=str(rec.get("existing_page_url", "")),
                data_to_add=[str(d) for d in data_to_add],
            ))

        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 1))

        enhance_count = sum(1 for r in recommendations if r.rec_type == "enhance")
        new_count = sum(1 for r in recommendations if r.rec_type == "new")
        logger.info(
            "Generated %d recommendations (%d enhance, %d new)",
            len(recommendations), enhance_count, new_count,
        )
        return recommendations

    except json.JSONDecodeError as exc:
        logger.error("JSON parse error in sitemap generation: %s", exc, exc_info=True)
        return []
    except Exception as exc:
        logger.error("Sitemap generation failed: %s", exc, exc_info=True)
        return []
