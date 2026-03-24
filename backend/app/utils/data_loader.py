"""Utility functions to load and organize ESG reference data from JSON files."""

import json
import logging
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

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
