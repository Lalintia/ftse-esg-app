"""ICB Subsector to FTSE Theme mapping with exposure levels.

Maps ICB subsector codes (8-digit, new ICB post-2019) to the FTSE Russell themes
that apply to companies in that sector, along with their exposure levels.

Source: Guidelines-FTSE-Russell-2026-TH-final_.pdf pp. 41-51
        "3. Themes for sectors/subsectors" reference table.

Old ICB (4-digit) → New ICB (8-digit) translation:
        icb-legacy-to-new-mapping.xlsx (FTSE Russell, July 2020)
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

# Key = ICB Subsector code (8 digits, new ICB post-2019)
# Value = list of dicts with theme name and exposure level
#
# Themes sourced from Guidelines PDF pp. 41-51.
# Sectors not listed here fall through to DEFAULT_THEMES.
# Exposure: High = primary/material ESG risk; Medium = applicable but lower materiality.
SECTOR_THEME_MAPPING: dict[str, list[dict[str, str | bool]]] = {

    # ── TECHNOLOGY (Industry 10) ────────────────────────────────────────────
    # Computer Services (old: 9533) — p.43
    "10101010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Software (old: 9537) — not in PDF; inherits Technology supersector profile
    "10101015": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Consumer Digital Services / Internet (old: 9535) — not in PDF; Technology profile
    "10101020": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Semiconductors (old: 9576) — p.49
    "10102010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Computer Hardware (old: 9572) — p.43
    "10102030": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],

    # ── TELECOMMUNICATIONS / MEDIA (Industry 15) ───────────────────────────
    # Cable Television Services (old: Broadcasting & Entertainment 5553) — p.42
    "15102010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Telecommunications Services (old: Fixed Line 6535) — not in PDF; DEFAULT profile
    "15102015": [
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
    ],

    # ── HEALTH CARE (Industry 20) ───────────────────────────────────────────
    # Biotechnology (old: 4573) — not in PDF; Health Care supersector profile
    "20103010": [
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
    # Pharmaceuticals (old: 4577) — not in PDF; Health Care supersector profile
    "20103015": [
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

    # ── FINANCIALS: BANKS (Industry 30) ────────────────────────────────────
    # Banks (old: 8355) — p.41
    # Note: PDF does not include Customer Responsibility for Banks.
    "30101010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
        {"theme": "Tax Transparency", "exposure": "Medium"},
    ],

    # ── FINANCIALS: FINANCIAL SERVICES (Industry 30) ───────────────────────
    # Consumer Lending / Consumer Finance (old: 8773) — p.43
    "30201020": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Mortgage Finance (old: 8779) — not in PDF; Financial Services profile
    "30201025": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Diversified Financial Services / Specialty Finance (old: 8775) — p.50
    # Differs from Consumer Lending: no Customer Responsibility
    "30202000": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Asset Managers and Custodians (old: 8771) — p.41
    "30202010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Investment Services (old: 8777) — p.46
    "30202015": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Mortgage REITs: Residential (old: 8676) — not in PDF; Real Estate/Finance hybrid
    "30203020": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],

    # ── FINANCIALS: INSURANCE (Industry 30) ────────────────────────────────
    # Life Insurance (old: 8575) — p.47
    "30301010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
        {"theme": "Tax Transparency", "exposure": "Medium"},
    ],
    # Full Line Insurance (old: 8532) — not in PDF; Insurance supersector profile
    "30302010": [
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
    # Reinsurance (old: 8538) — p.49
    "30302020": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
        {"theme": "Tax Transparency", "exposure": "Medium"},
    ],
    # Property and Casualty Insurance (old: 8536) — p.48
    "30302025": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
        {"theme": "Tax Transparency", "exposure": "Medium"},
    ],

    # ── REAL ESTATE (Industry 35) ───────────────────────────────────────────
    # Real Estate Holding and Development (old: 8633) — p.48
    # PDF includes Supply Chain: Environmental and Supply Chain: Social.
    # PDF does NOT include Customer Responsibility (removed from prior mapping).
    "35101010": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Supply Chain: Environmental", "exposure": "Medium"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Real Estate Services (old: 8637) — not in PDF; lighter Real Estate profile
    "35101015": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Diversified REITs (old: 8674) — not in PDF; Real Estate investment profile
    "35102000": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Hotel and Lodging REITs (old: 8677) — not in PDF; Hotels + Real Estate profile
    "35102015": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "Medium"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Office REITs (old: 8671) — not in PDF; Real Estate investment profile
    "35102030": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Residential REITs (old: 8673) — not in PDF; Real Estate investment profile
    "35102040": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Retail REITs (old: 8672) — not in PDF; Real Estate + Retail profile
    "35102045": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Other Specialty REITs (old: 8675) — not in PDF; Real Estate investment profile
    "35102070": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],

    # ── CONSUMER DISCRETIONARY (Industry 40) ───────────────────────────────
    # Automobiles (old: 3353) — not in PDF; Auto manufacturing profile
    "40101020": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Home Construction (old: 3728) — not in PDF; similar to Heavy Construction
    "40202010": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Media Agencies (old: 5555) — p.47
    "40301020": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Publishing (old: 5557) — not in PDF; similar to Media Agencies
    "40301030": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Diversified Retailers / Broadline Retailers (old: 5373) — p.42
    "40401010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Casinos and Gambling (old: 5752) — not in PDF; Travel & Leisure profile
    "40501020": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Hotels and Motels (old: 5753) — p.46
    "40501025": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "Medium"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Restaurants and Bars (old: 5757) — p.49
    "40501040": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],

    # ── CONSUMER STAPLES (Industry 45) ─────────────────────────────────────
    # Brewers (old: 3533) — not in PDF; Food & Beverage profile
    "45101010": [
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
    # Distillers and Vintners (old: 3535) — not in PDF; Food & Beverage profile
    "45101015": [
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
    # Soft Drinks (old: 3537) — p.49
    "45101020": [
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
    # Farming, Fishing, Ranching and Plantations (old: 3573) — p.44
    # PDF does NOT include Customer Responsibility for this sector.
    "45102010": [
        {"theme": "Biodiversity", "exposure": "High"},
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Food Products (old: 3577) — p.45
    "45102020": [
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
    # Tobacco (old: 3785) — not in PDF; Food & Beverage profile with strong CR
    "45103010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Food Retailers and Wholesalers (old: 5337) — p.45
    "45201010": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Customer Responsibility", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Personal Products (old: 3767) — p.48
    "45201020": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Nondurable Household Products (old: 3724) — not in PDF; Personal Products profile
    "45201030": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "Medium"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],

    # ── INDUSTRIALS (Industry 50) ───────────────────────────────────────────
    # Construction / Heavy Construction (old: 2357) — p.45
    "50101010": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Building Materials: Other / Building Materials & Fixtures (old: 2353) — p.42
    "50101035": [
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
    ],

    # ── BASIC MATERIALS: BASIC RESOURCES (Industry 55) ─────────────────────
    # Forestry (old: 1733) — not in PDF; similar to Farming & Fishing
    "55101010": [
        {"theme": "Biodiversity", "exposure": "High"},
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Supply Chain: Social", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Paper (old: 1737) — not in PDF; Basic Resources profile
    "55101015": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Supply Chain: Environmental", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "Medium"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Supply Chain: Social", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # General Mining (old: 1775) — not in PDF; similar to Iron & Steel
    "55102000": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Iron and Steel (old: 1757) — p.46
    "55102010": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Aluminum (old: 1753) — not in PDF; similar to Nonferrous Metals
    "55102035": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Nonferrous Metals (old: 1755) — p.48
    "55102050": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Diamonds and Gemstones (old: 1773) — not in PDF; mining profile
    "55103020": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Gold Mining (old: 1777) — not in PDF; mining profile
    "55103025": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Platinum and Precious Metals (old: 1779) — not in PDF; mining profile
    "55103030": [
        {"theme": "Biodiversity", "exposure": "Medium"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],

    # ── BASIC MATERIALS: CHEMICALS (Industry 55) ───────────────────────────
    # Chemicals: Diversified / Commodity Chemicals (old: 1353) — p.43
    # PDF does not include Risk Management for this sector.
    "55201000": [
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
    ],
    # Specialty Chemicals (old: 1357) — p.49
    # PDF does not include Risk Management for this sector.
    "55201020": [
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
    ],

    # ── ENERGY (Industry 60) ───────────────────────────────────────────────
    # Integrated Oil and Gas (old: 0537) — p.46
    # Climate Change kept at theme level; indicators_applicable=False per PTG calibration
    # (Integrated O&G subsector has 0 applicable CC indicators in FTSE 2026 TH set).
    # Biodiversity same treatment: Guidelines p.46 marks it geography/multinational-
    # dependent (underlined check) and the PTG CDD flags every EBD indicator as NAP
    # for a Thailand-only company.
    "60101000": [
        {"theme": "Climate Change", "exposure": "High", "indicators_applicable": False},
        {"theme": "Biodiversity", "exposure": "High", "indicators_applicable": False},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "High"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Oil: Crude Producers / Exploration & Production (old: 0533) — p.44
    "60101010": [
        {"theme": "Biodiversity", "exposure": "High"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "High"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Oil Equipment and Services (old: 0573) — not in PDF; Energy services profile
    "60101030": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Pipelines (old: 0577) — not in PDF; Energy infrastructure profile
    "60101035": [
        {"theme": "Climate Change", "exposure": "Medium"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "Medium"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Coal (old: 1771) — p.42
    "60101040": [
        {"theme": "Biodiversity", "exposure": "High"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "High"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "High"},
        {"theme": "Risk Management", "exposure": "High"},
    ],

    # ── UTILITIES (Industry 65) ─────────────────────────────────────────────
    # Alternative Electricity (old: 7537) — p.41
    # PDF does not include Supply Chain: Social or Risk Management.
    "65101010": [
        {"theme": "Biodiversity", "exposure": "High"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
    # Conventional Electricity (old: 7535) — p.44
    # PDF includes Risk Management; does not include Supply Chain: Social.
    "65101015": [
        {"theme": "Biodiversity", "exposure": "High"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
        {"theme": "Risk Management", "exposure": "Medium"},
    ],
    # Water (old: 7577) — p.51
    # PDF does not include Supply Chain: Social or Risk Management.
    "65102030": [
        {"theme": "Biodiversity", "exposure": "High"},
        {"theme": "Climate Change", "exposure": "High"},
        {"theme": "Pollution & Resources", "exposure": "High"},
        {"theme": "Water Security", "exposure": "High"},
        {"theme": "Health & Safety", "exposure": "High"},
        {"theme": "Human Rights & Community", "exposure": "High"},
        {"theme": "Labour Standards", "exposure": "Medium"},
        {"theme": "Anti-Corruption", "exposure": "High"},
        {"theme": "Corporate Governance", "exposure": "Medium"},
    ],
}

# Default themes for subsector codes not in the mapping above.
DEFAULT_THEMES: list[dict[str, str | bool]] = [
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
) -> list[dict[str, str | bool]]:
    """Get applicable themes for a subsector.

    Looks up the 8-digit ICB subsector code directly.
    Applies Thailand override: Anti-Corruption and Corporate Governance
    are always High Exposure.
    Filters out Tax Transparency for Emerging Market countries per
    FTSE Guidelines (only applies to Developed Market large caps).

    Args:
        subsector_code: ICB subsector code (8 digits, new ICB post-2019).
        country: ISO 3166-1 alpha-2 country code (default "TH").

    Returns:
        List of dicts with 'theme' and 'exposure' keys.
    """
    themes = SECTOR_THEME_MAPPING.get(subsector_code, DEFAULT_THEMES)

    result: list[dict[str, str | bool]] = []
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
        "Subsector %s, country %s: %d applicable themes",
        subsector_code,
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
        subsector_code: ICB subsector code (8 digits, new ICB post-2019).
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
            return str(entry["exposure"])

    # Theme not applicable for this sector
    return "Not Applicable"
