"""IFRS S1/S2 analysis engine using OpenAI."""

import asyncio
import json
import logging
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.config import get_settings
from app.prompts.ifrs_system import IFRS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Climate chapter has 56 items — split at this threshold
CLIMATE_BATCH_SPLIT_SIZE = 30


@dataclass
class IfrsResult:
    """Result of analyzing a single IFRS requirement.

    Attributes:
        paragraph_ref: The IFRS paragraph reference (e.g. IFRS S1.20).
        status: Assessment status — found, partial, or missing.
        evidence: Evidence text found on the website.
        confidence: Confidence level from 0.0 to 1.0.
        reasoning: AI reasoning for the assessment.
    """

    paragraph_ref: str
    status: str
    evidence: str
    confidence: float
    reasoning: str


def _build_chapter_prompt(
    chapter_name: str,
    requirements: list[dict[str, str | bool | int]],
    website_content: str,
) -> str:
    """Build a user prompt for analyzing requirements within a chapter.

    Args:
        chapter_name: Name of the IFRS chapter.
        requirements: List of requirement dicts.
        website_content: Concatenated markdown from crawled pages.

    Returns:
        Formatted user prompt string.
    """
    req_lines: list[str] = []
    for req in requirements:
        mandatory_tag = "[MANDATORY]" if req.get("is_mandatory") else "[OPTIONAL]"
        req_lines.append(
            f"- **{req['paragraph_ref']}** {mandatory_tag}: "
            f"{req['requirement_text']}"
        )

    requirements_text = "\n".join(req_lines)

    max_content_length = 120_000
    truncated_content = website_content[:max_content_length]
    if len(website_content) > max_content_length:
        truncated_content += "\n\n[Content truncated due to length]"

    from app.services.ftse_analyzer import _sanitize_text

    prompt = (
        f"## IFRS Chapter: {chapter_name}\n\n"
        f"## Requirements to Evaluate ({len(requirements)} requirements)\n\n"
        f"{requirements_text}\n\n"
        f"## Company Website Content\n\n"
        f"{truncated_content}"
    )
    return _sanitize_text(prompt)


def _split_requirements_into_batches(
    requirements_by_chapter: dict[str, list[dict[str, str | bool | int]]],
) -> list[tuple[str, list[dict[str, str | bool | int]]]]:
    """Split requirements into batches, splitting large chapters.

    The Climate chapter (56 items) is split into 2 sub-batches.
    Other chapters are sent as single batches.

    Args:
        requirements_by_chapter: Dict mapping chapter name to requirements.

    Returns:
        List of (batch_label, requirements) tuples.
    """
    batches: list[tuple[str, list[dict[str, str | bool | int]]]] = []

    for chapter_name, reqs in requirements_by_chapter.items():
        if len(reqs) > CLIMATE_BATCH_SPLIT_SIZE:
            mid = len(reqs) // 2
            batches.append((f"{chapter_name} (Part 1)", reqs[:mid]))
            batches.append((f"{chapter_name} (Part 2)", reqs[mid:]))
            logger.info(
                "Split chapter '%s' into 2 batches: %d + %d",
                chapter_name,
                mid,
                len(reqs) - mid,
            )
        else:
            batches.append((chapter_name, reqs))

    return batches


async def _analyze_batch(
    openai_client: AsyncOpenAI,
    batch_label: str,
    requirements: list[dict[str, str | bool | int]],
    website_content: str,
    semaphore: asyncio.Semaphore,
) -> list[IfrsResult]:
    """Analyze a batch of IFRS requirements.

    Args:
        openai_client: AsyncOpenAI client.
        batch_label: Label for logging (chapter name or sub-batch).
        requirements: Requirement dicts for this batch.
        website_content: Concatenated website content.
        semaphore: Concurrency limiter.

    Returns:
        List of IfrsResult for each requirement in the batch.
    """
    settings = get_settings()
    user_prompt = _build_chapter_prompt(batch_label, requirements, website_content)
    paragraph_refs = [req["paragraph_ref"] for req in requirements]

    async with semaphore:
        logger.info(
            "Analyzing IFRS batch: %s (%d requirements)",
            batch_label,
            len(requirements),
        )
        try:
            response = await openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": IFRS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=120.0,
            )

            usage = response.usage
            if usage:
                logger.info(
                    "IFRS batch %s tokens — input: %d, output: %d, total: %d",
                    batch_label,
                    usage.prompt_tokens,
                    usage.completion_tokens,
                    usage.total_tokens,
                )

            raw_text = response.choices[0].message.content or "{}"
            data = json.loads(raw_text)
            raw_results: list[dict[str, str | float]] = data.get("results", [])

            results_map: dict[str, dict[str, str | float]] = {
                r["paragraph_ref"]: r
                for r in raw_results
                if "paragraph_ref" in r
            }

            results: list[IfrsResult] = []
            for ref in paragraph_refs:
                if ref in results_map:
                    r = results_map[ref]
                    results.append(IfrsResult(
                        paragraph_ref=ref,
                        status=str(r.get("status", "missing")),
                        evidence=str(r.get("evidence", "")),
                        confidence=float(r.get("confidence", 0.0)),
                        reasoning=str(r.get("reasoning", "")),
                    ))
                else:
                    logger.warning(
                        "Requirement %s not in AI response for batch %s",
                        ref,
                        batch_label,
                    )
                    results.append(IfrsResult(
                        paragraph_ref=ref,
                        status="missing",
                        evidence="",
                        confidence=0.0,
                        reasoning="Requirement not returned by AI analysis.",
                    ))

            logger.info("IFRS batch %s complete: %d results", batch_label, len(results))
            return results

        except json.JSONDecodeError as exc:
            logger.error("JSON parse error for IFRS batch %s: %s", batch_label, exc)
            return [
                IfrsResult(
                    paragraph_ref=ref,
                    status="missing",
                    evidence="",
                    confidence=0.0,
                    reasoning=f"Analysis failed: JSON parse error — {exc}",
                )
                for ref in paragraph_refs
            ]
        except Exception as exc:
            logger.error("IFRS analysis failed for batch %s: %s", batch_label, exc)
            return [
                IfrsResult(
                    paragraph_ref=ref,
                    status="missing",
                    evidence="",
                    confidence=0.0,
                    reasoning=f"Analysis failed: {exc}",
                )
                for ref in paragraph_refs
            ]


async def analyze_ifrs(
    openai_client: AsyncOpenAI,
    website_content: str,
    requirements_by_chapter: dict[str, list[dict[str, str | bool | int]]],
) -> list[IfrsResult]:
    """Analyze website content against all IFRS S1/S2 requirements.

    Splits requirements into batches by chapter, with the Climate
    chapter (56 items) split into 2 sub-batches. Sends parallel
    requests limited by concurrency semaphore.

    Args:
        openai_client: AsyncOpenAI client.
        website_content: Concatenated markdown from all crawled pages.
        requirements_by_chapter: Dict mapping chapter name to requirement dicts.

    Returns:
        Flat list of IfrsResult for all requirements.
    """
    settings = get_settings()
    semaphore = asyncio.Semaphore(settings.ANALYSIS_CONCURRENCY)
    batches = _split_requirements_into_batches(requirements_by_chapter)

    tasks = [
        _analyze_batch(
            openai_client=openai_client,
            batch_label=batch_label,
            requirements=reqs,
            website_content=website_content,
            semaphore=semaphore,
        )
        for batch_label, reqs in batches
    ]

    logger.info("Starting IFRS analysis: %d batches in parallel", len(tasks))
    batch_results = await asyncio.gather(*tasks, return_exceptions=True)

    all_results: list[IfrsResult] = []
    for idx, result in enumerate(batch_results):
        if isinstance(result, Exception):
            batch_label = batches[idx][0]
            logger.error("IFRS batch %s raised exception: %s", batch_label, result)
            for req in batches[idx][1]:
                all_results.append(IfrsResult(
                    paragraph_ref=req["paragraph_ref"],
                    status="missing",
                    evidence="",
                    confidence=0.0,
                    reasoning=f"Analysis failed with exception: {result}",
                ))
        else:
            all_results.extend(result)

    logger.info("IFRS analysis complete: %d total results", len(all_results))
    return all_results
