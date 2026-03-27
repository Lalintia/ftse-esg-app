"""Sitemap recommendation generator using OpenAI."""

import json
import logging
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.config import get_settings
from app.prompts.sitemap_system import SITEMAP_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class SitemapRecommendation:
    """A recommended web page to improve ESG disclosure.

    Attributes:
        page_title: Suggested page title.
        page_path: Suggested URL path.
        reason: Why this page is recommended.
        priority: high, medium, or low.
        addresses_gaps: List of indicator/requirement codes addressed.
    """

    page_title: str
    page_path: str
    reason: str
    priority: str
    addresses_gaps: list[str]


def _build_gaps_summary(
    ftse_gaps: list[dict[str, str]],
    ifrs_gaps: list[dict[str, str]],
) -> str:
    """Build a summary of gaps for the AI prompt.

    Args:
        ftse_gaps: List of dicts with indicator_code, theme_name, indicator_name, status.
        ifrs_gaps: List of dicts with paragraph_ref, standard, section, status.

    Returns:
        Formatted text summarizing all gaps.
    """
    lines: list[str] = []

    # Group FTSE gaps by theme
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

    # Group IFRS gaps by standard
    ifrs_by_standard: dict[str, list[dict[str, str]]] = {}
    for gap in ifrs_gaps:
        std = gap.get("standard", "Unknown")
        if std not in ifrs_by_standard:
            ifrs_by_standard[std] = []
        ifrs_by_standard[std].append(gap)

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
) -> list[SitemapRecommendation]:
    """Generate sitemap recommendations based on identified gaps.

    Sends all gaps to OpenAI in a single request and receives
    consolidated page recommendations.

    Args:
        openai_client: AsyncOpenAI client.
        ftse_gaps: FTSE indicators with missing/partial status.
        ifrs_gaps: IFRS requirements with missing/partial status.

    Returns:
        List of SitemapRecommendation sorted by priority.
    """
    if not ftse_gaps and not ifrs_gaps:
        logger.info("No gaps found — skipping sitemap generation")
        return []

    settings = get_settings()
    gaps_summary = _build_gaps_summary(ftse_gaps, ifrs_gaps)

    logger.info(
        "Generating sitemap recommendations for %d FTSE + %d IFRS gaps",
        len(ftse_gaps),
        len(ifrs_gaps),
    )

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

        raw_text = response.choices[0].message.content or "{}"
        data = json.loads(raw_text)
        raw_recs: list[dict[str, str | list[str]]] = data.get("recommendations", [])

        recommendations: list[SitemapRecommendation] = []
        for rec in raw_recs:
            priority = str(rec.get("priority", "medium"))
            if priority not in {"high", "medium", "low"}:
                priority = "medium"

            addresses = rec.get("addresses_gaps", [])
            if not isinstance(addresses, list):
                addresses = []

            recommendations.append(SitemapRecommendation(
                page_title=str(rec.get("page_title", "")),
                page_path=str(rec.get("page_path", "")),
                reason=str(rec.get("reason", "")),
                priority=priority,
                addresses_gaps=[str(g) for g in addresses],
            ))

        # Sort by priority: high first, then medium, then low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 1))

        logger.info("Generated %d sitemap recommendations", len(recommendations))
        return recommendations

    except json.JSONDecodeError as exc:
        logger.error("JSON parse error in sitemap generation: %s", exc)
        return []
    except Exception as exc:
        logger.error("Sitemap generation failed: %s", exc)
        return []
