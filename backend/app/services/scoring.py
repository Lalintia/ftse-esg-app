"""FTSE and IFRS scoring engines.

Implements the 5-step FTSE Russell scoring methodology and
simple percentage-based IFRS compliance scoring.
"""

import logging
from dataclasses import dataclass, field

from app.utils.sector_themes import get_theme_exposure

logger = logging.getLogger(__name__)

# Thailand-specific: these themes always have High Exposure
THAILAND_HIGH_EXPOSURE_THEMES = {"Anti-Corruption", "Corporate Governance"}

# Pillar groupings for FTSE themes
PILLAR_THEMES: dict[str, list[str]] = {
    "Environmental": [
        "Biodiversity",
        "Climate Change",
        "Pollution & Resources",
        "Supply Chain: Environmental",
        "Water Security",
    ],
    "Social": [
        "Customer Responsibility",
        "Health & Safety",
        "Human Rights & Community",
        "Labour Standards",
        "Supply Chain: Social",
    ],
    "Governance": [
        "Anti-Corruption",
        "Corporate Governance",
        "Risk Management",
        "Tax Transparency",
    ],
}

# Exposure weight multipliers for pillar/overall scoring
EXPOSURE_WEIGHTS: dict[str, float] = {
    "High": 3.0,
    "Medium": 2.0,
    "Low": 1.0,
    "Not Applicable": 0.0,
}

# Threshold bands: % points scored -> theme score (0-5)
# Calibrated to match FTSE Russell exposure-weighted methodology.
# Companies with ~49% coverage should score ~2.5-3.0 overall.
SCORE_BANDS_HIGH: list[tuple[float, int]] = [
    (0.71, 5),
    (0.46, 4),
    (0.26, 3),
    (0.11, 2),
    (0.01, 1),
    (0.00, 0),
]

SCORE_BANDS_MEDIUM: list[tuple[float, int]] = [
    (0.76, 5),
    (0.51, 4),
    (0.31, 3),
    (0.16, 2),
    (0.01, 1),
    (0.00, 0),
]

SCORE_BANDS_LOW: list[tuple[float, int]] = [
    (0.81, 5),
    (0.61, 4),
    (0.41, 3),
    (0.21, 2),
    (0.01, 1),
    (0.00, 0),
]


@dataclass
class ThemeScore:
    """Score details for a single FTSE theme.

    Attributes:
        theme_name: Name of the theme.
        pillar: Parent pillar (Environmental/Social/Governance).
        exposure: Exposure level (High/Medium/Low/Not Applicable).
        indicators_total: Total number of indicators in this theme.
        indicators_found: Number of indicators with status 'found'.
        indicators_partial: Number with status 'partial'.
        indicators_missing: Number with status 'missing'.
        points_scored: Sum of indicator scores.
        points_possible: Maximum possible points.
        pct_points: Percentage of points scored.
        theme_score: Final theme score (0-5).
    """

    theme_name: str
    pillar: str
    exposure: str
    indicators_total: int
    indicators_found: int
    indicators_partial: int
    indicators_missing: int
    points_scored: float
    points_possible: float
    pct_points: float
    theme_score: int


@dataclass
class FtseScores:
    """Complete FTSE scoring breakdown.

    Attributes:
        overall_score: Overall ESG score (0.0-5.0).
        environmental_score: Environmental pillar score (0.0-5.0).
        social_score: Social pillar score (0.0-5.0).
        governance_score: Governance pillar score (0.0-5.0).
        theme_scores: Per-theme score details.
    """

    overall_score: float
    environmental_score: float
    social_score: float
    governance_score: float
    theme_scores: list[ThemeScore] = field(default_factory=list)


@dataclass
class IfrsScores:
    """IFRS compliance scoring breakdown.

    Attributes:
        s1_score: IFRS S1 compliance percentage (0-100).
        s2_score: IFRS S2 compliance percentage (0-100).
        s1_total: Total S1 requirements assessed.
        s1_found: S1 requirements found.
        s1_partial: S1 requirements partially found.
        s1_missing: S1 requirements missing.
        s2_total: Total S2 requirements assessed.
        s2_found: S2 requirements found.
        s2_partial: S2 requirements partially found.
        s2_missing: S2 requirements missing.
    """

    s1_score: float
    s2_score: float
    s1_total: int
    s1_found: int
    s1_partial: int
    s1_missing: int
    s2_total: int
    s2_found: int
    s2_partial: int
    s2_missing: int


def _get_exposure_for_theme(
    theme_name: str,
    indicators: list[dict[str, str | bool]],
) -> str:
    """Determine exposure level for a theme.

    Thailand context: Anti-Corruption and Corporate Governance
    are always High Exposure.

    Args:
        theme_name: Name of the FTSE theme.
        indicators: Indicators for this theme.

    Returns:
        Exposure level string.
    """
    if theme_name in THAILAND_HIGH_EXPOSURE_THEMES:
        return "High"

    # Use the most common exposure level among indicators
    # Note: JSON null becomes Python None, so we must handle it explicitly
    exposure_counts: dict[str, int] = {}
    for ind in indicators:
        raw_level = ind.get("exposure_level")
        level = str(raw_level) if raw_level is not None else "Medium"
        exposure_counts[level] = exposure_counts.get(level, 0) + 1

    if not exposure_counts:
        return "Medium"

    return max(exposure_counts, key=lambda k: exposure_counts[k])


def _pct_to_theme_score(pct: float, exposure: str) -> int:
    """Convert percentage points to theme score using threshold bands.

    Args:
        pct: Percentage of points scored (0.0 to 1.0).
        exposure: Exposure level determining which band to use.

    Returns:
        Theme score from 0 to 5.
    """
    if exposure == "Not Applicable":
        return 0

    bands = {
        "High": SCORE_BANDS_HIGH,
        "Medium": SCORE_BANDS_MEDIUM,
        "Low": SCORE_BANDS_LOW,
    }.get(exposure, SCORE_BANDS_MEDIUM)

    for threshold, score in bands:
        if pct >= threshold:
            return score
    return 0


def _weighted_average(
    scores: list[tuple[float, str]],
) -> float:
    """Calculate exposure-weighted average of scores.

    Args:
        scores: List of (score, exposure_level) tuples.

    Returns:
        Weighted average score, or 0.0 if no applicable themes.
    """
    total_weight = 0.0
    weighted_sum = 0.0

    for score, exposure in scores:
        weight = EXPOSURE_WEIGHTS.get(exposure, 0.0)
        if weight > 0:
            weighted_sum += score * weight
            total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 2)


def calculate_ftse_scores(
    results: list[dict[str, str | int | float]],
    indicators_by_theme: dict[str, list[dict[str, str | bool]]],
    subsector_code: str | None = None,
) -> FtseScores:
    """Calculate FTSE ESG scores using the 5-step methodology.

    Steps:
    1. Determine Theme Exposure (H/M/L/NA)
    2. Calculate % Indicator Points per theme
    3. Convert to Theme Score (0-5) via threshold bands
    4. Calculate Pillar Scores (exposure-weighted average)
    5. Calculate Overall ESG Score (exposure-weighted average)

    Args:
        results: List of result dicts with indicator_code, status, score.
        indicators_by_theme: Dict mapping theme_name to indicator dicts.
        subsector_code: Optional ICB subsector code for sector-specific
            exposure levels.

    Returns:
        FtseScores with complete breakdown.
    """
    # Index results by indicator code
    results_by_code: dict[str, dict[str, str | int | float]] = {
        r["indicator_code"]: r for r in results
    }

    theme_scores: list[ThemeScore] = []

    for theme_name, indicators in indicators_by_theme.items():
        if subsector_code:
            exposure = get_theme_exposure(subsector_code, theme_name)
        else:
            exposure = _get_exposure_for_theme(theme_name, indicators)

        found_count = 0
        partial_count = 0
        missing_count = 0
        points_scored = 0.0
        points_possible = len(indicators) * 5.0

        for ind in indicators:
            code = ind["indicator_code"]
            result = results_by_code.get(code)

            if result:
                status = str(result.get("status", "missing"))
                score = float(result.get("score", 0))

                if status == "found":
                    found_count += 1
                elif status == "partial":
                    partial_count += 1
                else:
                    missing_count += 1

                points_scored += score
            else:
                missing_count += 1

        pct = points_scored / points_possible if points_possible > 0 else 0.0
        t_score = _pct_to_theme_score(pct, exposure)

        theme_scores.append(ThemeScore(
            theme_name=theme_name,
            pillar=_get_pillar_for_theme(theme_name),
            exposure=exposure,
            indicators_total=len(indicators),
            indicators_found=found_count,
            indicators_partial=partial_count,
            indicators_missing=missing_count,
            points_scored=points_scored,
            points_possible=points_possible,
            pct_points=round(pct, 4),
            theme_score=t_score,
        ))

    # Step 4: Pillar scores
    pillar_scores: dict[str, float] = {}
    for pillar_name, pillar_theme_names in PILLAR_THEMES.items():
        pillar_theme_data = [
            (float(ts.theme_score), ts.exposure)
            for ts in theme_scores
            if ts.theme_name in pillar_theme_names
        ]
        pillar_scores[pillar_name] = _weighted_average(pillar_theme_data)

    # Step 5: Overall score
    all_theme_data = [
        (float(ts.theme_score), ts.exposure)
        for ts in theme_scores
    ]
    overall = _weighted_average(all_theme_data)

    scores = FtseScores(
        overall_score=overall,
        environmental_score=pillar_scores.get("Environmental", 0.0),
        social_score=pillar_scores.get("Social", 0.0),
        governance_score=pillar_scores.get("Governance", 0.0),
        theme_scores=theme_scores,
    )

    logger.info(
        "FTSE scoring complete: overall=%.2f, E=%.2f, S=%.2f, G=%.2f",
        scores.overall_score,
        scores.environmental_score,
        scores.social_score,
        scores.governance_score,
    )
    return scores


def _get_pillar_for_theme(theme_name: str) -> str:
    """Get the pillar name for a given theme.

    Args:
        theme_name: Name of the FTSE theme.

    Returns:
        Pillar name (Environmental, Social, or Governance).
    """
    for pillar, themes in PILLAR_THEMES.items():
        if theme_name in themes:
            return pillar
    return "Unknown"


def calculate_ifrs_scores(
    results: list[dict[str, str | float]],
    requirements: list[dict[str, str | bool | int]],
) -> IfrsScores:
    """Calculate IFRS S1/S2 compliance scores.

    Scoring: found=1.0, partial=0.5, missing=0.0
    Score = (sum of points / total requirements) * 100

    Args:
        results: List of result dicts with paragraph_ref and status.
        requirements: List of all IFRS requirements.

    Returns:
        IfrsScores with S1 and S2 breakdowns.
    """
    results_by_ref: dict[str, dict[str, str | float]] = {
        r["paragraph_ref"]: r for r in results
    }

    s1_found = 0
    s1_partial = 0
    s1_missing = 0
    s1_total = 0
    s2_found = 0
    s2_partial = 0
    s2_missing = 0
    s2_total = 0

    for req in requirements:
        standard = req["standard"]
        ref = req["paragraph_ref"]
        result = results_by_ref.get(ref)
        status = str(result.get("status", "missing")) if result else "missing"

        if standard == "IFRS S1":
            s1_total += 1
            if status == "found":
                s1_found += 1
            elif status == "partial":
                s1_partial += 1
            else:
                s1_missing += 1
        else:
            s2_total += 1
            if status == "found":
                s2_found += 1
            elif status == "partial":
                s2_partial += 1
            else:
                s2_missing += 1

    s1_points = s1_found + (s1_partial * 0.5)
    s2_points = s2_found + (s2_partial * 0.5)

    s1_score = round((s1_points / s1_total) * 100, 2) if s1_total > 0 else 0.0
    s2_score = round((s2_points / s2_total) * 100, 2) if s2_total > 0 else 0.0

    scores = IfrsScores(
        s1_score=s1_score,
        s2_score=s2_score,
        s1_total=s1_total,
        s1_found=s1_found,
        s1_partial=s1_partial,
        s1_missing=s1_missing,
        s2_total=s2_total,
        s2_found=s2_found,
        s2_partial=s2_partial,
        s2_missing=s2_missing,
    )

    logger.info(
        "IFRS scoring complete: S1=%.1f%% (%d/%d), S2=%.1f%% (%d/%d)",
        scores.s1_score,
        s1_found,
        s1_total,
        scores.s2_score,
        s2_found,
        s2_total,
    )
    return scores
