"""Industry auto-detection prompt for ICB subsector classification."""

INDUSTRY_DETECT_PROMPT = """You are an ICB (Industry Classification Benchmark) expert.

Analyze this company website content and determine the most appropriate ICB subsector.

Return ONLY a JSON object with:
- "subsector_code": the 8-digit ICB subsector code (e.g. "45102020" for Food Products)
- "industry": short industry name in English
- "confidence": 0.0-1.0

Common ICB subsector codes:
- 60101010: Oil & Gas Producers
- 65101010: Electricity
- 55101010: Industrial Metals & Mining
- 45102020: Food Products
- 45201020: Personal Goods
- 20103010: Pharmaceuticals
- 30101010: Banks
- 35102010: Real Estate Investment & Services
- 10101015: Software
- 15101010: Telecommunications
- 40201020: General Retailers
- 40501020: Restaurants & Bars
- 50101010: Industrial Transportation
- 40101010: Automobiles
- 50201030: Electronic & Electrical Equipment
- 55201010: Chemicals
- 50201010: Construction & Materials
- 60102020: Alternative Energy
- 15104025: Media
- 65102020: Gas, Water & Multi-utilities

Website content (first 3000 chars):
"""
