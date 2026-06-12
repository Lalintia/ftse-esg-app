"""Shared derivation of applicable indicators/sub-indicators per subsector.

Single source of truth for the 3-layer filtering (theme -> indicator ->
sub-indicator) used by both the full analysis pipeline and the instant
pre-check endpoint.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.utils.data_loader import get_indicators_by_theme
from app.utils.sector_themes import get_applicable_themes
from app.utils.subpart_resolver import get_subparts_for_subsector

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
MAPPING_PATH = DATA_DIR / "indicator_subsector_mapping.json"


@dataclass
class ApplicabilityResult:
    """Applicable indicators for one subsector, grouped by theme."""

    indicators_by_theme: dict[str, list[dict]] = field(default_factory=dict)
    zero_indicator_themes: list[dict[str, str]] = field(default_factory=list)
    theme_exposures: dict[str, str] = field(default_factory=dict)

    @property
    def total_indicators(self) -> int:
        return sum(len(inds) for inds in self.indicators_by_theme.values())

    @property
    def total_themes(self) -> int:
        return len(self.indicators_by_theme) + len(self.zero_indicator_themes)


def _load_mapping() -> dict[str, dict]:
    if not MAPPING_PATH.exists():
        raise FileNotFoundError(
            f"Required data file missing: {MAPPING_PATH}. "
            "Rebuild the Docker image or ensure the data/ directory is mounted."
        )
    try:
        with open(MAPPING_PATH, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in {MAPPING_PATH}: {exc}") from exc


def _matches_subsector(subsector_code: str, codes: list[str]) -> bool:
    return any(subsector_code.startswith(c) or c == subsector_code for c in codes)


def derive_applicable(subsector_code: str) -> ApplicabilityResult:
    """Filter indicators for a subsector (theme applicability + mapping).

    Mirrors the FTSE 3-layer logic: applicable themes from the Guidelines
    table, then per-indicator type/subsector rules from RC11, including
    exclude_subsectors and themes kept at theme level with zero indicators
    (FTSE minimum score = 1).

    Args:
        subsector_code: 8-digit ICB subsector code.

    Returns:
        ApplicabilityResult with indicators grouped by applicable theme.
    """
    applicable_themes = get_applicable_themes(subsector_code)
    applicable_theme_names = {t["theme"] for t in applicable_themes}
    indicator_mapping = _load_mapping()
    indicators_by_theme = get_indicators_by_theme()

    no_indicator_themes = {
        t["theme"] for t in applicable_themes
        if not t.get("indicators_applicable", True)
    }

    result = ApplicabilityResult(
        zero_indicator_themes=[
            {"theme": str(t["theme"]), "exposure": str(t["exposure"])}
            for t in applicable_themes
            if not t.get("indicators_applicable", True)
        ],
        theme_exposures={
            str(t["theme"]): str(t["exposure"]) for t in applicable_themes
        },
    )

    for theme, inds in indicators_by_theme.items():
        if theme not in applicable_theme_names or theme in no_indicator_themes:
            continue

        applicable_inds: list[dict] = []
        for ind in inds:
            code = ind["indicator_code"]
            m = indicator_mapping.get(code, {"type": "core", "subsectors": []})

            if _matches_subsector(subsector_code, m.get("exclude_subsectors", [])):
                continue

            if m["type"] in ("core", "performance"):
                applicable_inds.append(ind)
            elif _matches_subsector(subsector_code, m.get("subsectors", [])):
                applicable_inds.append(ind)

        if applicable_inds:
            result.indicators_by_theme[theme] = applicable_inds

    return result


def count_subparts_by_indicator(subsector_code: str) -> dict[str, int]:
    """Number of applicable sub-indicators per indicator code."""
    counts: dict[str, int] = {}
    for entry in get_subparts_for_subsector(subsector_code).values():
        code = entry["indicator_code"]
        counts[code] = counts.get(code, 0) + 1
    return counts
