# FTSE ESG Web App — Progress & Notes

Updated: 24 March 2569

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

### Phase 5 — Deployment ✅ DEPLOYED
- [x] backend/Dockerfile (Python 3.11 + Playwright + Chromium)
- [x] frontend/Dockerfile (Multi-stage Next.js standalone)
- [x] nginx/nginx.conf (Reverse proxy, 300s timeout)
- [x] docker-compose.yml (3 services)
- [x] .env.production template
- [x] deploy.sh helper script
- [x] Deploy to AWS EC2 (t3.medium, Singapore)
- [x] Domain: esg.ohmai.me (Cloudflare DNS + SSL via Let's Encrypt)
- [x] Host nginx proxies esg.ohmai.me → Docker port 8080

### Phase 6 — UI Redesign ✅ DONE (24 March 2569)
- [x] Devialet-inspired editorial design (Helvetica Neue, off-white/warm gray)
- [x] Simplified industry dropdown (20 categories in plain English)
- [x] AI auto-detect industry from crawled content (OpenAI, ~1000 tokens)
- [x] Theme card grid layout (3 columns, grouped by E/S/G pillar)
- [x] Expandable indicator details per theme
- [x] Sticky tab bar with scroll position preservation
- [x] Sitemap recommendations with page title + path
- [x] Status sanitization (handle AI returning unexpected values)
- [x] Fixed 7 truncated Thai indicator names
- [x] Removed Recent Analyses from input page
- [x] Added ESG project card to ohmai.me portfolio

### Phase 7 — Bug Fixes & UX Improvements ✅ DONE (24 March 2569)
- [x] Auto-sync truncated indicator names from JSON → Supabase on startup (7 names fixed)
- [x] Live progress messages during analysis (status_message field in DB)
  - Sitemap discovery, page scraping (X/Y), PDF download with filename
  - Auto-detect industry, analyzing indicators, scoring, sitemap generation
  - Frontend displays message below progress bar with pulse animation
- [x] Fixed PDF download failing with 405 Not Allowed (missing browser headers)
  - httpx was sending requests without User-Agent → websites block it
  - Added browser-like headers (User-Agent, Accept, Accept-Language)
  - Confirmed: Thai Union PDFs download successfully (SD Report 15MB, etc.)
- [x] Replaced Playwright PDF fallback from download-event to API request context
  - Old method waited for "download" event → timeout on PDFs that open in browser
  - New method uses `context.request.get()` — more reliable
  - Added try/finally to prevent browser process leak
- [x] PDF strategy: web-first, PDF supplements — only core reports EN
  - Only download SD Report + One Report/Annual Report (max 3 files)
  - Skip Thai language PDFs (EN preferred — TH was duplicating content, wasting 200K chars)
  - Removed auto-discover of TCFD/annex/policy PDFs (SupplyChainProgressReport, shark finning, etc.)
  - Reduced max PDF chars from 800K → 500K
- [x] Fixed OpenAI 429 rate limit errors (Water Security, Risk Management, Labour Standards all failed)
  - Root cause: PDF content increased tokens per request → hit 200K TPM limit on gpt-4.1-nano
  - Added retry with backoff (3 attempts, wait 5/10/15s)
  - Reduced analysis concurrency from 3 → 2 to spread token usage

### Phase 8 — Two-Round Analysis (Website-first, PDF supplements) ✅ DONE (24 March 2569)
- [x] FTSE analysis now runs 2 rounds instead of 1
  - Round 1: Analyze all themes using **website HTML content only**
  - Round 2: Re-analyze themes with >50% missing/partial indicators using **website + PDF combined**
  - Merge results: keep the higher score per indicator (PDF can only improve, never lower)
- [x] HTML and PDF content separated in crawler output (`analyzer.py`)
  - HTML pages → `website_content` (primary source)
  - PDF reports → `pdf_content` (supplement for gap-filling)
- [x] IFRS analysis unchanged — still uses all content combined (single round)
- [x] Progress message shows "(Round 1: website → Round 2: PDF for gaps)" when PDFs available
- **Expected improvement:** Better accuracy because website data is analyzed first without PDF noise, then PDF fills in quantitative data gaps (water usage, emissions, H&S stats, etc.)
- **Trade-off:** ~1.5-2x slower for FTSE analysis when PDFs are available (2 rounds instead of 1), but only re-analyzes themes that actually need it

---

## Test Results — Thai Union Benchmark

**Thai Union Group PCL** — Real FTSE ESG Score: **4.3/5.0** (92nd percentile)

| Version | Overall | E | S | G | Indicators | Pages | Key Change |
|---|---|---|---|---|---|---|---|
| v1 | 1.88 | 2.75 | 1.00 | 1.64 | 381 | 15 | Baseline (Firecrawl) |
| v8 | 2.86 | 3.0 | 2.64 | 3.0 | 218 | 45 | +Subsector mapping, Playwright |
| v10 | 2.75 | 3.0 | 2.57 | 2.62 | 238 | 47 | +PDF reading |
| Latest | **3.11** | 3.0 | **3.07** | **3.38** | 218 | 51 | +BMS removed, content filtering |
| v12 (auto) | **2.86** | 2.79 | **2.86** | **3.0** | 214 | 48 | +Auto-detect industry, redesign UI |
| v13 | 1.20 | 1.20 | 1.75 | 0.38 | 214 | 49 | PDF download broken (0 PDFs, 405 error) |
| v14 | 1.60 | 1.90 | 1.40 | 1.40 | 214 | 49 | Same PDF bug, Food & Beverages selected |
| v15 | 1.50 | 1.40 | 1.80 | 1.10 | 196 | 52 | PDF fixed but 429 rate limit killed 3 themes (Water, Risk, Labour = 0.0) |
| **REAL** | **4.3** | ~4+ | ~4+ | ~4+ | ~240 | — | FTSE Russell official |

**Best achieved: 3.11/5.0 (72% of real score)** — v12 auto-detect: 2.86/5.0 (67%)

**Note:** v13-v14: PDF broken (405). v15: PDF works but rate limit (429) failed 3 themes. Fixed: core reports EN only + retry + concurrency 2. Awaiting v16 re-test.

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

### Phase 9 — Agent Skills Installation (26 March 2569)
- [x] Installed 10 agent skills via skills.sh (`npx skills add`)
- [x] 4 project-specific (`.agents/skills/`) + 6 global (`~/.agents/skills/`)

**Project Skills** (FTSE only — `.agents/skills/`):
| Skill | Source | Purpose |
|-------|--------|---------|
| supabase-postgres-best-practices | supabase/agent-skills (Official) | Database best practices |
| next-best-practices | vercel-labs/next-skills (Official) | Next.js patterns |
| shadcn | shadcn/ui (Official) | UI component usage |
| vercel-react-best-practices | vercel-labs/agent-skills | React patterns |

**Global Skills** (all projects — `~/.agents/skills/`):
| Skill | Source | Purpose |
|-------|--------|---------|
| systematic-debugging | obra/superpowers | Structured debugging |
| frontend-design | anthropics/skills (Official) | Frontend design guidelines |
| pdf | anthropics/skills (Official) | PDF handling |
| python-error-handling | wshobson/agents | Error handling patterns |
| python-performance-optimization | wshobson/agents | Python optimization |
| agent-browser | vercel-labs/agent-browser | Browser automation |

---

### Phase 10 — PTG Energy Calibration (26 March 2569)
Calibrated the entire analysis pipeline against real FTSE Russell data for PTG Energy (Oil & Gas — Integrated Oil & Gas).

**Reference data:** FTSE CPC PDF (Dec 2024) + Excel CDD (May 2025) — ESG 3.3, E 2.3, S 3.3, G 4.6

**Changes made:**
- [x] Fixed Oil & Gas theme mapping — removed 3 NAP themes (Biodiversity, Supply Chain Env/Social), kept Climate Change as zero-indicator theme (score=1)
- [x] Fixed indicator applicability — 142 indicators match PTG reference exactly
- [x] Added `exclude_subsectors` mechanism for core/performance indicators NAP at subsector level
- [x] Added `indicators_applicable: False` flag for themes with 0 indicators (FTSE minimum score = 1)
- [x] Crawler: subdomain auto-discovery (investor.X, ir.X, sustainability.X)
- [x] Crawler: smart PDF reading — scan TOC first, read only ESG-relevant pages (127/359 vs 85/359 sequential)
- [x] Added Thai keywords for content filtering (กำกับดูแลกิจการ, ต่อต้านทุจริต, อาชีวอนามัย, etc.)
- [x] Upgraded AI model: gpt-4.1-nano → **gpt-4.1-mini** (major accuracy improvement)

**Test Results — PTG Energy Benchmark:**

| Run | Model | Overall | E | S | G | Found | Key Change |
|---|---|---|---|---|---|---|---|
| R1 | nano | 2.00 | 1.33 | 3.33 | 1.25 | 58/142 | Baseline (web only) |
| R4 | nano | 1.85 | 1.33 | 2.00 | 2.25 | 58/142 | +Thai keywords |
| R5 | nano | 1.62 | 1.00 | 1.33 | 2.62 | 49/142 | +Smart PDF, inconsistent |
| **R6** | **mini** | **3.65** | **2.67** | **4.33** | **4.00** | **112/142** | **+gpt-4.1-mini** |
| **REAL** | **FTSE** | **3.3** | **2.3** | **3.3** | **4.6** | **96/142** | **FTSE Russell official** |

**Key findings:**
- Indicator mapping: 100% accurate (142/142 match PTG reference)
- AI model was the bottleneck: nano found 58 indicators, mini found 112
- gpt-4.1-nano highly inconsistent (18% variance between runs)
- PTG itself has data for 96/142 indicators — we found 112 (some false positives to calibrate)
- Smart PDF reading critical: PTG One Report is 359 pages, governance data starts at page 149

**Token cost per analysis (gpt-4.1-mini):**
- Input: ~200K tokens × $0.40/1M = ~$0.08
- Output: ~25K tokens × $1.60/1M = ~$0.04
- **Total: ~$0.12 per analysis (~4.2 บาท)**

**Additional changes (same session):**
- [x] IFRS analysis temporarily disabled (save ~20% tokens, no verified reference data)
- [x] IFRS tab + quick stats hidden in frontend
- [x] Code review fixes: log bug (path→target_url), duplicate @dataclass, double-count guard in scoring, PDF fallback fix
- [x] Token cost reduced: ~$0.096/analysis (~3.4 บาท) without IFRS

**PTG-Calibrated Prompt (same session):**
- [x] Analyzed 30 false positive patterns (37% wrong metric, 30% report mention, 13% committee, 10% training, 7% general policy)
- [x] Added 5 common false positive patterns with real examples to prompt
- [x] Added theme-specific guidance for CG, Anti-Corruption, Pollution, Water
- [x] Fixed frontend subsector code: 60101010 → 60101000 (Integrated Oil & Gas)
- [x] Run 8 result: ESG **3.31** vs target 3.30 (**ห่างแค่ 0.01!**)

### Phase 11 — Security Hardening (26 March 2569)
Security audit using `security-auditor` skill — found 12 issues, fixed 9:

| Severity | Issue | Status |
|---|---|---|
| CRIT-1 | API keys in .env | No issue (never committed) |
| **CRIT-2** | **SSRF — private IP access** | **Fixed** — block 127.x, 10.x, 172.16.x, 169.254.x |
| HIGH-1 | No authentication | Deferred |
| **HIGH-2** | **No rate limiting** | **Fixed** — 5 req/min analysis, 30 req/min API |
| **HIGH-3** | **No query limit cap** | **Fixed** — max 100 |
| **HIGH-4** | **Docker runs as root** | **Fixed** — appuser:1001 |
| **MED-1** | **No security headers** | **Fixed** — nosniff, DENY, XSS, HSTS |
| **MED-2** | **No HTTPS enforcement** | **Fixed** — HSTS header |
| **MED-3** | **XML sitemap DoS** | **Fixed** — 10MB limit |
| **MED-4** | **CORS wildcard** | **Fixed** — esg.ohmai.me only |

**Additional fixes (same session):**
- [x] Fixed frontend subsector code 60101010 → 60101000 — indicator counts now match ref exactly
- [x] Fixed Dockerfile: Playwright browsers in /opt/playwright-browsers for non-root user
- [x] Fixed nginx rate limit: merged zones to avoid strict limit on GET requests
- [x] Fixed count query: limit(0) to avoid fetching all rows
- [x] Fixed EmptyState component declaration order
- [x] Code review with `performance-error-reviewer` + `react-typescript-reviewer` skills (3 rounds)

**Final verified result (deployed on esg.ohmai.me):**
- ESG Overall: **3.4** vs target **3.3** (+0.1)
- Environmental: **2.0** vs target **2.3** (-0.3)
- Social: **4.3** vs target **3.3** (+1.0)
- Governance: **4.0** vs target **4.6** (-0.6)
- Indicator counts: **142/142 match PTG reference — all 8 themes correct**

**Remaining work:**
- [ ] Add API authentication (HIGH-1)
- [ ] Score band calibration (Social 4.3 vs target 3.3 — still high)
- [ ] Reduce false positives (~31 false positives remain)
- [ ] Test consistency by running multiple times with gpt-4.1-mini
- [ ] Test with other companies to validate changes don't break other sectors
- [ ] Re-enable IFRS when verified reference data is available

---

### Research: FTSE Methodology (24 March 2569)
- FTSE Russell uses 600+ human analysts (manual extraction, ~5 hrs/company)
- They read BOTH website HTML AND PDF documents (Annual Report, Sustainability Report, etc.)
- LSEG announced new "LSEG Sustainability Ratings and Data" (9 March 2026) — rules-based, AI-ready
- LSEG signed deals with Anthropic, Microsoft, OpenAI (GBP 1.9 billion)
- Thai Union website analysis (HTML only, no PDF): ~75% of indicators are qualitative (policy/commitment) which website covers well, but 92 quantitative indicators (Water Security, H&S, Pollution, Climate) need numbers from PDFs

*Created by Claude from conversations with P'Ohm — Updated 26 March 2569*
