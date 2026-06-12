"""Industry auto-detection prompt for ICB subsector classification."""

# Every code below must exist in the official ICB 173-subsector list
# (icb_subsectors table) and should have an explicit theme profile in
# app/utils/sector_themes.py where possible.
INDUSTRY_DETECT_PROMPT = """You are an ICB (Industry Classification Benchmark) expert.

Analyze this company website content and determine the most appropriate ICB subsector.

Return ONLY a JSON object with:
- "subsector_code": the 8-digit ICB subsector code (e.g. "45102020" for Food Products)
- "industry": short industry name in English
- "confidence": 0.0-1.0

Common ICB subsector codes:
- 60101000: Integrated Oil & Gas
- 60101010: Oil: Crude Producers (Exploration & Production)
- 65101015: Conventional Electricity
- 65101010: Alternative Electricity (solar, wind, renewables)
- 65102030: Water Utilities
- 55102000: General Mining
- 55102010: Iron & Steel
- 55201000: Chemicals (commodity / diversified)
- 55201020: Specialty Chemicals
- 50101010: Construction (heavy construction, contractors)
- 50101035: Building Materials
- 50203000: Diversified Industrials (machinery, manufacturing)
- 50206060: Transportation Services (logistics)
- 45102020: Food Products
- 45102010: Farming, Fishing, Ranching and Plantations
- 45201020: Personal Products
- 20103015: Pharmaceuticals
- 20103010: Biotechnology
- 30101010: Banks
- 30201020: Consumer Lending (consumer finance, leasing)
- 30302010: Insurance (full line)
- 35101010: Real Estate Holding & Development
- 10101015: Software
- 10102010: Semiconductors
- 15102015: Telecommunications Services (mobile, fixed-line)
- 40301020: Media Agencies (broadcasting, entertainment)
- 40401010: Diversified Retailers
- 40501025: Hotels & Motels
- 40501040: Restaurants & Bars
- 40101020: Automobiles

Website content (first 3000 chars):
"""
