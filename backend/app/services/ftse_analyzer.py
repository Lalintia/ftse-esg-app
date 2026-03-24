"""FTSE Russell ESG analysis engine using OpenAI."""

import asyncio
import json
import logging
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.config import get_settings
from app.prompts.ftse_system import FTSE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def _sanitize_text(text: str) -> str:
    """Remove characters that break OpenAI JSON requests.

    Strips null bytes, control characters (except newline/tab),
    and replaces problematic unicode that can corrupt JSON payloads.
    """
    # Remove null bytes
    text = text.replace("\x00", "")
    # Remove control characters except \n \r \t
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Replace surrogate pairs that can break JSON encoding
    text = text.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
    return text


@dataclass
class FtseResult:
    """Result of analyzing a single FTSE indicator.

    Attributes:
        indicator_code: The FTSE indicator code (e.g. ECC01).
        status: Assessment status — found, partial, or missing.
        score: Score from 0 to 5.
        evidence: Evidence text found on the website.
        confidence: Confidence level from 0.0 to 1.0.
        reasoning: AI reasoning for the assessment.
    """

    indicator_code: str
    status: str
    score: int
    evidence: str
    confidence: float
    reasoning: str


_THEME_KEYWORDS: dict[str, list[str]] = {
    "Biodiversity": ["biodiversity", "habitat", "ecosystem", "deforestation", "marine conservation", "endangered species", "palm oil sustainable", "MSC certified", "ASC certified", "RSPO"],
    "Climate Change": ["climate change", "carbon emission", "GHG emission", "greenhouse gas", "scope 1", "scope 2", "scope 3", "TCFD", "net zero", "carbon neutral", "renewable energy", "carbon footprint", "decarboni"],
    "Pollution & Resources": ["pollution prevention", "waste management", "circular economy", "hazardous waste", "effluent", "packaging recycl", "plastic reduction", "air emission", "zero waste"],
    "Supply Chain: Environmental": ["supply chain environment", "supplier environment", "sustainable sourcing", "green procurement", "environmental standard supplier"],
    "Water Security": ["water management", "wastewater", "water stress", "water consumption", "water recycl", "water withdrawal", "water intensity", "water stewardship"],
    "Customer Responsibility": ["product safety", "food safety", "data privacy", "responsible marketing", "nutrition", "product recall", "customer complaint", "quality management system", "BMS", "breast milk"],
    "Health & Safety": ["occupational health", "workplace safety", "lost time injury", "fatality rate", "incident rate", "safety management", "OHSAS", "ISO 45001"],
    "Human Rights & Community": ["human rights policy", "human rights due diligence", "indigenous people", "FPIC", "child labour", "forced labour", "modern slavery", "community engagement", "human rights impact"],
    "Labour Standards": ["labour standard", "labor standard", "diversity and inclusion", "gender pay gap", "living wage", "working hour", "freedom of association", "collective bargaining", "employee turnover", "training hour"],
    "Supply Chain: Social": ["supply chain social", "supplier code of conduct", "supplier audit", "supplier assessment", "child labor supply", "forced labor supply", "animal welfare"],
    "Anti-Corruption": ["anti-corruption", "anti-bribery", "whistleblow", "ethics policy", "political contribution", "lobbying expenditure", "corruption risk"],
    "Corporate Governance": ["board composition", "board independence", "corporate governance", "board committee", "audit committee", "nomination committee", "remuneration committee", "executive compensation", "shareholder rights", "CEO chairman separation"],
    "Risk Management": ["risk management framework", "enterprise risk", "ESG risk", "material fine", "regulatory penalty", "internal audit", "risk committee"],
    "Tax Transparency": ["tax transparency", "country-by-country reporting", "tax strategy", "tax governance", "effective tax rate"],
}


def _filter_content_for_theme(theme_name: str, website_content: str) -> str:
    """Filter website content to sections most relevant to a specific theme.

    Splits content by page sections, scores each page by keyword density,
    then selects the highest-scoring pages up to the character limit.

    Args:
        theme_name: Name of the FTSE theme.
        website_content: Full concatenated content from all pages.

    Returns:
        Filtered content with the most relevant pages for the theme.
    """
    keywords = _THEME_KEYWORDS.get(theme_name, [])
    max_chars = 80_000

    if not keywords:
        return website_content[:max_chars]

    pages = website_content.split("\n\n---\n\n")

    # Score each page by number of keyword matches (density)
    scored_pages: list[tuple[int, str]] = []
    for page in pages:
        page_lower = page.lower()
        score = sum(1 for kw in keywords if kw.lower() in page_lower)
        if score > 0:
            scored_pages.append((score, page))

    # Sort by score descending — most relevant pages first
    scored_pages.sort(key=lambda x: x[0], reverse=True)

    # Select top pages within char limit
    selected: list[str] = []
    total_chars = 0
    for score, page in scored_pages:
        if total_chars + len(page) > max_chars:
            continue
        selected.append(page)
        total_chars += len(page)

    # Fallback: if too few relevant pages, include all truncated
    if total_chars < 15_000:
        return website_content[:max_chars]

    return "\n\n---\n\n".join(selected)


def _build_theme_prompt(
    theme_name: str,
    indicators: list[dict[str, str | bool]],
    website_content: str,
) -> str:
    """Build a user prompt for analyzing indicators within a theme.

    Args:
        theme_name: Name of the FTSE theme.
        indicators: List of indicator dicts with code, name, description.
        website_content: Concatenated markdown from crawled pages.

    Returns:
        Formatted user prompt string.
    """
    indicator_lines: list[str] = []
    for ind in indicators:
        indicator_lines.append(
            f"- **{ind['indicator_code']}**: {ind['indicator_name']}\n"
            f"  Description: {ind['description']}"
        )

    indicators_text = "\n".join(indicator_lines)

    # Filter content to pages relevant to this theme
    filtered_content = _filter_content_for_theme(theme_name, website_content)

    prompt = (
        f"## Theme: {theme_name}\n\n"
        f"## Indicators to Evaluate ({len(indicators)} indicators)\n\n"
        f"{indicators_text}\n\n"
        f"## Company Website Content (filtered for {theme_name})\n\n"
        f"{filtered_content}"
    )
    return _sanitize_text(prompt)


async def _analyze_theme(
    openai_client: AsyncOpenAI,
    theme_name: str,
    indicators: list[dict[str, str | bool]],
    website_content: str,
    semaphore: asyncio.Semaphore,
) -> list[FtseResult]:
    """Analyze all indicators for a single FTSE theme.

    Args:
        openai_client: AsyncOpenAI client.
        theme_name: Name of the FTSE theme.
        indicators: Indicator dicts for this theme.
        website_content: Concatenated website content.
        semaphore: Concurrency limiter.

    Returns:
        List of FtseResult for each indicator in the theme.
    """
    settings = get_settings()
    user_prompt = _build_theme_prompt(theme_name, indicators, website_content)
    indicator_codes = [ind["indicator_code"] for ind in indicators]

    async with semaphore:
        logger.info(
            "Analyzing FTSE theme: %s (%d indicators)",
            theme_name,
            len(indicators),
        )
        try:
            response = await openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": FTSE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            usage = response.usage
            if usage:
                logger.info(
                    "FTSE theme %s tokens — input: %d, output: %d, total: %d",
                    theme_name,
                    usage.prompt_tokens,
                    usage.completion_tokens,
                    usage.total_tokens,
                )

            raw_text = response.choices[0].message.content or "{}"
            data = json.loads(raw_text)
            raw_results: list[dict[str, str | int | float]] = data.get("results", [])

            # Map results by indicator code for lookup
            results_map: dict[str, dict[str, str | int | float]] = {
                r["indicator_code"]: r
                for r in raw_results
                if "indicator_code" in r
            }

            results: list[FtseResult] = []
            for code in indicator_codes:
                if code in results_map:
                    r = results_map[code]
                    results.append(FtseResult(
                        indicator_code=code,
                        status=str(r.get("status", "missing")),
                        score=int(r.get("score", 0)),
                        evidence=str(r.get("evidence", "")),
                        confidence=float(r.get("confidence", 0.0)),
                        reasoning=str(r.get("reasoning", "")),
                    ))
                else:
                    logger.warning(
                        "Indicator %s not in AI response for theme %s",
                        code,
                        theme_name,
                    )
                    results.append(FtseResult(
                        indicator_code=code,
                        status="missing",
                        score=0,
                        evidence="",
                        confidence=0.0,
                        reasoning="Indicator not returned by AI analysis.",
                    ))

            logger.info("FTSE theme %s complete: %d results", theme_name, len(results))
            return results

        except json.JSONDecodeError as exc:
            logger.error("JSON parse error for FTSE theme %s: %s", theme_name, exc)
            return [
                FtseResult(
                    indicator_code=code,
                    status="missing",
                    score=0,
                    evidence="",
                    confidence=0.0,
                    reasoning=f"Analysis failed: JSON parse error — {exc}",
                )
                for code in indicator_codes
            ]
        except Exception as exc:
            logger.error("FTSE analysis failed for theme %s: %s", theme_name, exc)
            return [
                FtseResult(
                    indicator_code=code,
                    status="missing",
                    score=0,
                    evidence="",
                    confidence=0.0,
                    reasoning=f"Analysis failed: {exc}",
                )
                for code in indicator_codes
            ]


async def analyze_ftse(
    openai_client: AsyncOpenAI,
    website_content: str,
    indicators_by_theme: dict[str, list[dict[str, str | bool]]],
) -> list[FtseResult]:
    """Analyze website content against all FTSE indicators grouped by theme.

    Sends parallel requests (limited by concurrency semaphore) for each
    of the 14 FTSE themes.

    Args:
        openai_client: AsyncOpenAI client.
        website_content: Concatenated markdown from all crawled pages.
        indicators_by_theme: Dict mapping theme_name to list of indicator dicts.

    Returns:
        Flat list of FtseResult for all indicators across all themes.
    """
    settings = get_settings()
    semaphore = asyncio.Semaphore(settings.ANALYSIS_CONCURRENCY)

    tasks = [
        _analyze_theme(
            openai_client=openai_client,
            theme_name=theme_name,
            indicators=indicators,
            website_content=website_content,
            semaphore=semaphore,
        )
        for theme_name, indicators in indicators_by_theme.items()
    ]

    logger.info("Starting FTSE analysis: %d themes in parallel", len(tasks))
    theme_results = await asyncio.gather(*tasks, return_exceptions=True)

    all_results: list[FtseResult] = []
    for idx, result in enumerate(theme_results):
        if isinstance(result, Exception):
            theme_name = list(indicators_by_theme.keys())[idx]
            logger.error("Theme %s raised exception: %s", theme_name, result)
            for ind in indicators_by_theme[theme_name]:
                all_results.append(FtseResult(
                    indicator_code=ind["indicator_code"],
                    status="missing",
                    score=0,
                    evidence="",
                    confidence=0.0,
                    reasoning=f"Analysis failed with exception: {result}",
                ))
        else:
            all_results.extend(result)

    logger.info("FTSE analysis complete: %d total results", len(all_results))
    return all_results
