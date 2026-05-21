"""Resolve sub-indicators for a given subsector.

Sectors with verified FTSE CDD reference (e.g., PTG Oil & Gas) use sector-specific
override files as authoritative source. Other sectors fall back to description-based
parsing from indicator_subparts.json with theme/subsector filtering.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.utils.sector_themes import get_applicable_themes

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
GLOBAL_SUBPARTS_PATH = DATA_DIR / "indicator_subparts.json"

# CDD-derived override files are kept as REFERENCE ONLY for validation.
# They are NOT loaded into the resolver — using them as runtime input would
# constitute data leakage (the verification would just be reading back the
# reference). Description-based parsing remains the single source of truth.
SECTOR_OVERRIDE_FILES: dict[str, str] = {}


@lru_cache(maxsize=1)
def _load_global() -> dict[str, dict]:
    return json.loads(GLOBAL_SUBPARTS_PATH.read_text())


@lru_cache(maxsize=8)
def _load_override(filename: str) -> dict[str, dict]:
    path = DATA_DIR / filename
    return json.loads(path.read_text())


def get_subparts_for_subsector(subsector_code: str) -> dict[str, dict]:
    """Return sub-indicator entries applicable to the given subsector.

    If the subsector has a CDD override file → return the override unchanged
    (CDD is the complete authoritative list, including NAP filtering at theme +
    indicator level).

    Otherwise → return description-based entries filtered by applicable themes
    and indicator-subsector mapping rules.
    """
    if subsector_code in SECTOR_OVERRIDE_FILES:
        return _load_override(SECTOR_OVERRIDE_FILES[subsector_code])

    data = _load_global()
    themes = get_applicable_themes(subsector_code)
    applicable_theme_names = {
        t["theme"] for t in themes if t.get("indicators_applicable", True)
    }

    result: dict[str, dict] = {}
    for code, entry in data.items():
        if entry["theme_name"] not in applicable_theme_names:
            continue

        indicator_type = entry.get("type", "core")
        subsectors = entry.get("subsectors", [])
        if indicator_type in ("specific", "geography"):
            if subsector_code not in subsectors:
                continue

        result[code] = entry

    return result


def count_subparts(subsector_code: str) -> int:
    return len(get_subparts_for_subsector(subsector_code))
