# FTSE ESG Web App — Progress & Notes

Updated: 23 March 2569

---

## Project Overview

**Web App for analyzing company websites against FTSE Russell ESG + IFRS S1/S2 standards**

Sale team enters company URL → App crawls & analyzes → Dashboard showing gaps + estimated score + recommended sitemap

### Use Cases
- Internal Sales tool — analyze potential clients' websites
- Show compliance gaps (FTSE + IFRS) to pitch ESG consulting services
- Generate reports with recommended sitemap improvements

---

## Decisions Made

| Topic | Decision |
|---|---|
| Users | Sale team (internal tool) |
| UI/UX | Beautiful, professional UI following UX/UI principles |
| Dashboard Language | English |
| Crawler | Playwright (headless Chrome, unlimited, free) |
| AI Engine | OpenAI GPT-4.1-mini |
| Database | Supabase (project: ftse-esg-app, region: Mumbai) |
| Frontend | Next.js 16 + Tailwind CSS + shadcn/ui + Recharts |
| Backend | Python FastAPI |
| Output | Dashboard + Export PDF |
| Standards | FTSE Russell (14 Themes, 381 Indicators) + IFRS S1/S2 (111 Requirements) |
| Deployment | Docker + Nginx on AWS EC2 (t3.medium) |

---

## FTSE Indicator Methodology

### Key Finding
FTSE evaluates **125-300+ indicators per company** depending on subsector and country:
- 125 = average minimum
- 300+ = maximum for companies with many applicable themes
- 56% general questions, 44% subsector/country-specific

### Indicator Types (from PDF legend)
- **Core** (no marker): applies to all companies within applicable theme
- **(S)** Sector-specific: applies only to specified subsectors
- **(P)** Performance: performance indicators (applies like core)
- **(G)** Geography-specific: applies based on country

### Our Mapping (from FTSE official PDF)
| Type | Count |
|---|---|
| Core | 196 |
| Specific (S) | 176 |
| Performance (P) | 6 |
| Geography (G) | 3 |
| **Total** | **381** |

### Food Products (45102020) — Thai Union Example
- **13/14 themes applicable** (Tax Transparency excluded for Thai Emerging Market)
- **~240 indicators** applicable (core + performance + Food-specific)
- This is consistent with FTSE methodology: Food Products has many themes → more indicators

### FTSE Data Sources (from FAQ v1.5)
FTSE reads ALL publicly available documents:
- Corporate website (all ESG-related pages)
- Sustainability Report / SD Report PDF
- Annual Report / 56-1 One Report PDF
- Corporate Governance Report PDF
- Human Rights Policy, Environment Policy, Supplier Code of Conduct PDFs
- CDP Climate Change Response (from cdp.net)
- AGM Notice, Press Releases

### Indicators Excluded
- BMS (Breast Milk Substitutes) SCR13-32: specific to infant formula producers
- Nuclear (SHS18-24, SHS22, SHS42-43): specific to nuclear energy
- South Africa (SLS27): specific to companies operating in South Africa
- Tax Transparency (GTX01-12): only for Large cap Developed Market + Multinational

### Thailand Context
- Thailand = Emerging Market → Tax Transparency NOT applicable
- Thailand = Primary Impact Country → Anti-Corruption + Corporate Governance = High Exposure always

---

## Build Phases — Status

### Phase 1 — Database + Data ✅ DONE
- [x] Supabase project (ftse-esg-app, Mumbai region)
- [x] 9 database tables with schema, RLS, triggers
- [x] 14 FTSE themes (E:5, S:5, G:4)
- [x] 173 ICB subsectors
- [x] 381 FTSE indicators with S/P/G markers
- [x] 111 IFRS S1/S2 requirements
- [x] Indicator-subsector mapping (196 core + 176 specific + 6 performance + 3 geography)
- [x] ICB old→new code conversion (179 mappings)
- [x] Sector-theme applicability mapping (12 supersectors + default)

### Phase 2 — Backend ✅ DONE
- [x] FastAPI app with config, dependencies, models
- [x] Playwright crawler (free, unlimited)
- [x] Sitemap.xml discovery + ESG keyword page selection + priority ranking
- [x] PDF download + full text extraction (pdfplumber, entire document)
- [x] PDF report discovery: navigates to /investor-relations, /sustainability, /downloads etc.
- [x] ESG PDF detection: sustainability report, annual report, 56-1, CG report, policies
- [x] Up to 5 PDFs per analysis, 200K chars per PDF, 500K total
- [x] Content filtering per theme (keyword density scoring, top pages first)
- [x] OpenAI prompts: FTSE (quantitative data aware) + IFRS + Sitemap
- [x] FTSE analyzer: theme batches parallel with semaphore
- [x] IFRS analyzer: chapter batches parallel
- [x] Scoring engine: 5-step FTSE + calibrated threshold bands
- [x] Subsector indicator filtering (theme applicability + indicator-subsector mapping)
- [x] Thailand: Anti-Corruption + CG = High, Tax Transparency excluded
- [x] BMS/Nuclear/South Africa indicators excluded where not applicable
- [x] Company name extraction (multi-page title analysis + domain fallback)
- [x] Background task orchestrator with status tracking
- [x] API endpoints: POST/GET analyses, GET subsectors, GET health

### Phase 3 — Frontend ✅ DONE
- [x] Next.js 16 + Tailwind + shadcn/ui
- [x] Input page: URL + searchable subsector dropdown + recent analyses
- [x] Dashboard: Score circles, Radar chart, Gap tables, FTSE/IFRS/Sitemap tabs
- [x] Analysis progress: Pipeline animation
- [x] History page
- [x] Export PDF button (placeholder)

### Phase 4 — Testing & Bug Fixes ✅ DONE
- [x] Tested: PTTGC, SCB, CP ALL, Thai Union (multiple iterations)
- [x] Fixed: Firecrawl → Playwright migration
- [x] Fixed: IFRS duplicate key (upsert + dedup)
- [x] Fixed: Company name extraction
- [x] Fixed: IFRS compliance >100%
- [x] Fixed: Radar chart rendering
- [x] Fixed: ICB old→new code conversion for indicator mapping
- [x] Fixed: Indicator mapping file path
- [x] Fixed: BMS indicators incorrectly labeled as core
- [x] Fixed: Nuclear indicators incorrectly labeled as core
- [x] Fixed: Tax Transparency excluded for Emerging Markets
- [x] Fixed: 145 indicators missing exposure_level → all assigned
- [x] Fixed: Content filtering keywords too generic → keyword density scoring
- [x] Fixed: PDF content diluting AI analysis → per-theme filtering

### Phase 5 — Deployment ✅ READY TO DEPLOY
- [x] backend/Dockerfile (Python 3.11 + Playwright + Chromium)
- [x] frontend/Dockerfile (Multi-stage Next.js standalone)
- [x] nginx/nginx.conf (Reverse proxy, 300s timeout)
- [x] docker-compose.yml (3 services)
- [x] .env.production template
- [x] deploy.sh helper script
- [ ] Deploy to AWS EC2

---

## Test Results — Thai Union Benchmark

**Thai Union Group PCL** — Real FTSE ESG Score: **4.3/5.0** (92nd percentile)

| Version | Overall | E | S | G | Indicators | Pages | Key Change |
|---|---|---|---|---|---|---|---|
| v1 | 1.88 | 2.75 | 1.00 | 1.64 | 381 | 15 | Baseline (Firecrawl) |
| v8 | 2.86 | 3.0 | 2.64 | 3.0 | 218 | 45 | +Subsector mapping, Playwright |
| v10 | 2.75 | 3.0 | 2.57 | 2.62 | 238 | 47 | +PDF reading |
| Latest | **3.11** | 3.0 | **3.07** | **3.38** | 218 | 51 | +BMS removed, content filtering |
| **REAL** | **4.3** | ~4+ | ~4+ | ~4+ | ~240 | — | FTSE Russell official |

**Best achieved: 3.11/5.0 (72% of real score)**

### Score Gap Analysis
| Factor | Estimated Impact |
|---|---|
| AI reads table data poorly (quantitative indicators in PDF tables) | ~0.5 |
| AI model capability (mini vs full) | ~0.3 |
| Scoring threshold calibration | ~0.3 |
| **Total gap** | **~1.2** |

---

## Deployment Plan

### AWS EC2 Setup
| Setting | Value |
|---|---|
| Instance | t3.medium (2 vCPU, 4GB RAM) |
| AMI | Ubuntu 24.04 LTS |
| Storage | 30GB gp3 |
| Ports | 22, 80, 443 |
| Est. cost | ~$30/month (~1,050 THB) |

### Steps
1. Create EC2 + Install Docker
2. Clone repo + create .env.production
3. `./deploy.sh`
4. Point domain → EC2 IP
5. Setup SSL (Cloudflare or Let's Encrypt)

---

## Future Improvements
- [ ] Scoring calibration (threshold bands tuning with more benchmark companies)
- [ ] Better AI quantitative data parsing (table extraction from PDFs)
- [ ] Try GPT-4.1 full model for comparison
- [ ] PDF export implementation
- [ ] CDP data integration
- [ ] Batch analysis (multiple companies)
- [ ] Score trend tracking over time

---

*Created by Claude from conversations with P'Ohm — 23 March 2569*
