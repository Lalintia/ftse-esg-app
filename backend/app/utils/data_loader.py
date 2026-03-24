"""Utility functions to load and organize ESG reference data from JSON files."""

import json
import logging
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

from supabase import Client

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@lru_cache
def load_ftse_indicators() -> list[dict[str, Any]]:
    """Load FTSE Russell indicators from JSON file.

    Returns:
        List of indicator dictionaries with keys: indicator_code,
        indicator_name, description, theme_code, theme_name,
        data_type, exposure_level, is_core.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
    """
    file_path = DATA_DIR / "ftse_indicators.json"
    logger.info("Loading FTSE indicators from %s", file_path)
    with open(file_path, encoding="utf-8") as f:
        indicators: list[dict[str, Any]] = json.load(f)
    logger.info("Loaded %d FTSE indicators", len(indicators))
    return indicators


@lru_cache
def load_ifrs_requirements() -> list[dict[str, Any]]:
    """Load IFRS S1/S2 requirements from JSON file.

    Returns:
        List of requirement dictionaries with keys: standard,
        chapter, section, paragraph_ref, requirement_text,
        is_mandatory, display_order.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
    """
    file_path = DATA_DIR / "ifrs_requirements.json"
    logger.info("Loading IFRS requirements from %s", file_path)
    with open(file_path, encoding="utf-8") as f:
        requirements: list[dict[str, Any]] = json.load(f)
    logger.info("Loaded %d IFRS requirements", len(requirements))
    return requirements


def get_indicators_by_theme() -> dict[str, list[dict[str, Any]]]:
    """Group FTSE indicators by theme name.

    Returns:
        Dictionary mapping theme_name to list of indicators
        belonging to that theme.
    """
    indicators = load_ftse_indicators()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for indicator in indicators:
        theme_name = indicator.get("theme_name", "Unknown")
        grouped[theme_name].append(indicator)
    return dict(grouped)


def sync_indicator_names_to_db(supabase: Client) -> int:
    """Update indicator_name in Supabase from the JSON source file.

    Compares each indicator_code's name in the DB against the JSON file
    and updates any that differ (e.g. previously truncated names).

    Args:
        supabase: Authenticated Supabase client.

    Returns:
        Number of indicators updated.
    """
    indicators = load_ftse_indicators()
    json_names: dict[str, str] = {
        ind["indicator_code"]: ind["indicator_name"]
        for ind in indicators
    }

    db_rows = (
        supabase.table("ftse_indicators")
        .select("id, indicator_code, indicator_name")
        .execute()
    )

    updated = 0
    for row in db_rows.data:
        code = row["indicator_code"]
        expected_name = json_names.get(code)
        if expected_name and row.get("indicator_name") != expected_name:
            supabase.table("ftse_indicators").update(
                {"indicator_name": expected_name}
            ).eq("id", row["id"]).execute()
            logger.info("Updated indicator %s name: %s", code, expected_name)
            updated += 1

    if updated:
        logger.info("Synced %d indicator names to database", updated)
    else:
        logger.info("All indicator names already in sync")
    return updated


def get_requirements_by_chapter() -> dict[str, list[dict[str, Any]]]:
    """Group IFRS requirements by chapter.

    Returns:
        Dictionary mapping chapter name to list of requirements
        belonging to that chapter.
    """
    requirements = load_ifrs_requirements()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for requirement in requirements:
        chapter = requirement.get("chapter", "Unknown")
        grouped[chapter].append(requirement)
    return dict(grouped)
