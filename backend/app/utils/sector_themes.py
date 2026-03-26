"""ICB Sector to FTSE Theme mapping with exposure levels.

Maps ICB Supersector codes to the FTSE Russell themes that apply
to companies in that sector, along with their exposure levels.
"""

import logging

logger = logging.getLogger(__name__)

# Thailand-specific: these themes are always High Exposure
# regardless of sector mapping (Primary Impact Country rule)
THAILAND_HIGH_EXPOSURE_OVERRIDES: set[str] = {
    "Anti-Corruption",
    "Corporate Governance",
}

# FTSE Guidelines: Tax Transparency applies only to
# "Large cap companies from Developed Markets that are Multinational"
# These Emerging Market countries should NOT have Tax Transparency applied.
EMERGING_MARKET_COUNTRIES: set[str] = {
    "TH", "ID", "MY", "PH", "VN", "IN", "CN", "TW",
    "KR", "BR", "MX", "ZA", "CL", "CO", "PE", "TR",
    "EG", "SA", "AE", "QA", "KW", "PK", "BD", "LK",
}

# Key = ICB Supersector code (4 digits)
# Value = list of dicts with theme name and exposure level
SECTOR_THEME_MAPPING: dict[str, list[dict[str, str]]] = {
    # Food Beverage and Tobacco (Supersector 4510)
    "4510": [
        {"theme": "Biodiversity", "exposure": "High"},
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Banks (Supersector 3010)
    "3010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
        {"theme": "Tax Transparency", "exposure": "Medium"},
    ],
    # Energy (Oil Gas Coal) (Supersector 6010)
    # Calibrated against PTG Energy CPC (Dec 2024): ESG 3.3, E 2.3, S 3.3, G 4.6
    # NAP themes removed: Biodiversity, Supply Chain: Environmental, Supply Chain: Social
    # Climate Change kept: applicable at theme level but 0 indicators for Integrated Oil & Gas
    "6010": [
        {"theme": "Climate Change", "exposure": "High", "indicators_applicable": False},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "High"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Basic Materials / Chemicals (Supersector 5520)
    "5520": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Real Estate (Supersector 3510)
    "3510": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Customer Responsibility", "exposure": "Medium"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Utilities (Supersector 6510)
    "6510": [
        {"theme": "Biodiversity", "exposure": "High"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Technology (Supersector 1010)
    "1010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Consumer Services / Retail (Supersector 4040)
    "4040": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Insurance (Supersector 3030)
    "3030": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
        {"theme": "Tax Transparency", "exposure": "Medium"},
    ],
    # Health Care (Supersector 2010)
    "2010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Industrials (Supersector 5020)
    "5020": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Supply Chain: Environmental", "exposure": "Medium"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Travel & Leisure (Supersector 4050)
    "4050": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
}

# Default themes for sectors not in the mapping
DEFAULT_THEMES: list[dict[str, str]] = [
    {"theme": "Climate Change", "exposure": "Medium"},
    {"theme": "Pollution & Resources", "exposure": "Medium"},
    {"theme": "Customer Responsibility", "exposure": "Medium"},
    {"theme": "Health & Safety", "exposure": "Medium"},
    {"theme": "Human Rights & Community", "exposure": "Medium"},
    {"theme": "Labour Standards", "exposure": "Medium"},
    {"theme": "Supply Chain: Social", "exposure": "Medium"},
    {"theme": "Anti-Corruption", "exposure": "High"},
    {"theme": "Corporate Governance", "exposure": "Medium"},
    {"theme": "Risk Management", "exposure": "Medium"},
]


def get_applicable_themes(
    subsector_code: str,
    country: str = "TH",
) -> list[dict[str, str]]:
    """Get applicable themes for a subsector.

    Uses the first 4 digits (supersector code) for matching.
    Applies Thailand override: Anti-Corruption and Corporate Governance
    are always High Exposure.
    Filters out Tax Transparency for Emerging Market countries per
    FTSE Guidelines (only applies to Developed Market large caps).

    Args:
        subsector_code: ICB subsector code (4 or 6 digits).
        country: ISO 3166-1 alpha-2 country code (default "TH").

    Returns:
        List of dicts with 'theme' and 'exposure' keys.
    """
    supersector_code = subsector_code[:4]
    themes = SECTOR_THEME_MAPPING.get(supersector_code, DEFAULT_THEMES)

    result: list[dict[str, str]] = []
    for entry in themes:
        # Skip Tax Transparency for Emerging Market countries
        if (
            entry["theme"] == "Tax Transparency"
            and country.upper() in EMERGING_MARKET_COUNTRIES
        ):
            logger.info(
                "Excluding Tax Transparency for %s (Emerging Market)",
                country.upper(),
            )
            continue

        # Apply Thailand high-exposure overrides
        if entry["theme"] in THAILAND_HIGH_EXPOSURE_OVERRIDES:
            merged = entry.copy()
            merged["exposure"] = "High"
            result.append(merged)
        else:
            result.append(entry.copy())

    logger.info(
        "Subsector %s (supersector %s), country %s: %d applicable themes",
        subsector_code,
        supersector_code,
        country.upper(),
        len(result),
    )
    return result


def get_theme_exposure(
    subsector_code: str,
    theme_name: str,
    country: str = "TH",
) -> str:
    """Get exposure level for a specific theme and subsector.

    Args:
        subsector_code: ICB subsector code (4 or 6 digits).
        theme_name: Name of the FTSE theme.
        country: ISO 3166-1 alpha-2 country code (default "TH").

    Returns:
        Exposure level string (High/Medium/Low/Not Applicable).
    """
    # Tax Transparency not applicable for Emerging Markets
    if (
        theme_name == "Tax Transparency"
        and country.upper() in EMERGING_MARKET_COUNTRIES
    ):
        return "Not Applicable"

    # Thailand override takes priority
    if theme_name in THAILAND_HIGH_EXPOSURE_OVERRIDES:
        return "High"

    themes = get_applicable_themes(subsector_code, country=country)
    for entry in themes:
        if entry["theme"] == theme_name:
            return entry["exposure"]

    # Theme not applicable for this sector
    return "Not Applicable"
