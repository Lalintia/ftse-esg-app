-- ============================================================
-- FTSE ESG Web App — Initial Database Schema
-- Run this in Supabase SQL Editor
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. ICB Subsectors (173 subsectors with hierarchy)
-- ============================================================
CREATE TABLE icb_subsectors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code VARCHAR(10) NOT NULL UNIQUE,
  name VARCHAR(200) NOT NULL,
  industry_code VARCHAR(4) NOT NULL,
  industry_name VARCHAR(200) NOT NULL,
  supersector_code VARCHAR(6) NOT NULL,
  supersector_name VARCHAR(200) NOT NULL,
  sector_code VARCHAR(8) NOT NULL,
  sector_name VARCHAR(200) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_icb_industry_code ON icb_subsectors(industry_code);
CREATE INDEX idx_icb_supersector_code ON icb_subsectors(supersector_code);
CREATE INDEX idx_icb_sector_code ON icb_subsectors(sector_code);

COMMENT ON TABLE icb_subsectors IS 'ICB (Industry Classification Benchmark) 173 subsectors with full hierarchy';

-- ============================================================
-- 2. FTSE Themes (14 themes, 3 pillars)
-- ============================================================
CREATE TABLE ftse_themes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pillar VARCHAR(20) NOT NULL CHECK (pillar IN ('Environmental', 'Social', 'Governance')),
  pillar_code CHAR(1) NOT NULL CHECK (pillar_code IN ('E', 'S', 'G')),
  theme_name VARCHAR(100) NOT NULL UNIQUE,
  theme_order SMALLINT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ftse_themes_pillar ON ftse_themes(pillar_code);

COMMENT ON TABLE ftse_themes IS 'FTSE Russell 14 ESG themes mapped to 3 pillars (E/S/G)';

-- ============================================================
-- 3. FTSE Indicators (300+ indicators)
-- ============================================================
CREATE TABLE ftse_indicators (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  indicator_code VARCHAR(30) NOT NULL UNIQUE,
  indicator_name VARCHAR(300) NOT NULL,
  description TEXT,
  theme_id UUID NOT NULL REFERENCES ftse_themes(id) ON DELETE RESTRICT,
  exposure_level VARCHAR(20) CHECK (exposure_level IN ('High', 'Medium', 'Low', 'Not Applicable')),
  data_type VARCHAR(50),
  scoring_methodology TEXT,
  is_core BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ftse_indicators_theme ON ftse_indicators(theme_id);
CREATE INDEX idx_ftse_indicators_code ON ftse_indicators(indicator_code);
CREATE INDEX idx_ftse_indicators_exposure ON ftse_indicators(exposure_level);
CREATE INDEX idx_ftse_indicators_core ON ftse_indicators(is_core);

COMMENT ON TABLE ftse_indicators IS 'FTSE Russell 300+ ESG indicators with theme mapping and exposure levels';

-- ============================================================
-- 3.1 Indicator-Subsector Applicability (many-to-many)
-- ============================================================
CREATE TABLE ftse_indicator_subsectors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  indicator_id UUID NOT NULL REFERENCES ftse_indicators(id) ON DELETE CASCADE,
  subsector_id UUID NOT NULL REFERENCES icb_subsectors(id) ON DELETE CASCADE,
  is_applicable BOOLEAN NOT NULL DEFAULT TRUE,
  weight NUMERIC(5, 4),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(indicator_id, subsector_id)
);

CREATE INDEX idx_indicator_subsectors_indicator ON ftse_indicator_subsectors(indicator_id);
CREATE INDEX idx_indicator_subsectors_subsector ON ftse_indicator_subsectors(subsector_id);

COMMENT ON TABLE ftse_indicator_subsectors IS 'Many-to-many mapping: which indicators apply to which ICB subsectors';

-- ============================================================
-- 4. IFRS Requirements (S1/S2 checklist)
-- ============================================================
CREATE TABLE ifrs_requirements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  standard VARCHAR(10) NOT NULL CHECK (standard IN ('IFRS S1', 'IFRS S2')),
  chapter VARCHAR(100) NOT NULL,
  section VARCHAR(100),
  paragraph_ref VARCHAR(50),
  requirement_code VARCHAR(30) UNIQUE,
  requirement_text TEXT NOT NULL,
  guidance_text TEXT,
  is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
  display_order SMALLINT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ifrs_standard ON ifrs_requirements(standard);
CREATE INDEX idx_ifrs_chapter ON ifrs_requirements(chapter);
CREATE INDEX idx_ifrs_mandatory ON ifrs_requirements(is_mandatory);

COMMENT ON TABLE ifrs_requirements IS 'IFRS S1/S2 sustainability disclosure requirements from KPMG checklist';

-- ============================================================
-- 5. Analyses (each company analysis session)
-- ============================================================
CREATE TABLE analyses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_name VARCHAR(300),
  company_url TEXT NOT NULL,
  subsector_id UUID REFERENCES icb_subsectors(id) ON DELETE SET NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'crawling', 'analyzing', 'completed', 'failed')),
  overall_score NUMERIC(5, 2),
  environmental_score NUMERIC(5, 2),
  social_score NUMERIC(5, 2),
  governance_score NUMERIC(5, 2),
  ifrs_s1_score NUMERIC(5, 2),
  ifrs_s2_score NUMERIC(5, 2),
  pages_crawled INTEGER DEFAULT 0,
  error_message TEXT,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_by UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analyses_status ON analyses(status);
CREATE INDEX idx_analyses_subsector ON analyses(subsector_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX idx_analyses_company_url ON analyses(company_url);

COMMENT ON TABLE analyses IS 'Each analysis session: a company URL analyzed against FTSE ESG + IFRS S1/S2';

-- ============================================================
-- 6. Analysis FTSE Results (per indicator per analysis)
-- ============================================================
CREATE TABLE analysis_ftse_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
  indicator_id UUID NOT NULL REFERENCES ftse_indicators(id) ON DELETE RESTRICT,
  status VARCHAR(20) NOT NULL DEFAULT 'missing'
    CHECK (status IN ('found', 'partial', 'missing')),
  score NUMERIC(5, 2),
  evidence TEXT,
  source_url TEXT,
  source_page_title VARCHAR(500),
  confidence NUMERIC(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
  ai_reasoning TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(analysis_id, indicator_id)
);

CREATE INDEX idx_ftse_results_analysis ON analysis_ftse_results(analysis_id);
CREATE INDEX idx_ftse_results_indicator ON analysis_ftse_results(indicator_id);
CREATE INDEX idx_ftse_results_status ON analysis_ftse_results(status);

COMMENT ON TABLE analysis_ftse_results IS 'Per-indicator FTSE ESG results for each analysis';

-- ============================================================
-- 7. Analysis IFRS Results (per requirement per analysis)
-- ============================================================
CREATE TABLE analysis_ifrs_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
  requirement_id UUID NOT NULL REFERENCES ifrs_requirements(id) ON DELETE RESTRICT,
  status VARCHAR(20) NOT NULL DEFAULT 'missing'
    CHECK (status IN ('found', 'partial', 'missing')),
  evidence TEXT,
  source_url TEXT,
  source_page_title VARCHAR(500),
  confidence NUMERIC(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
  ai_reasoning TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(analysis_id, requirement_id)
);

CREATE INDEX idx_ifrs_results_analysis ON analysis_ifrs_results(analysis_id);
CREATE INDEX idx_ifrs_results_requirement ON analysis_ifrs_results(requirement_id);
CREATE INDEX idx_ifrs_results_status ON analysis_ifrs_results(status);

COMMENT ON TABLE analysis_ifrs_results IS 'Per-requirement IFRS S1/S2 results for each analysis';

-- ============================================================
-- 8. Sitemap Recommendations (per analysis)
-- ============================================================
CREATE TABLE sitemap_recommendations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
  recommended_page_title VARCHAR(300) NOT NULL,
  recommended_page_path VARCHAR(500),
  reason TEXT NOT NULL,
  priority VARCHAR(10) NOT NULL DEFAULT 'medium'
    CHECK (priority IN ('high', 'medium', 'low')),
  related_theme_id UUID REFERENCES ftse_themes(id) ON DELETE SET NULL,
  related_ifrs_standard VARCHAR(10) CHECK (related_ifrs_standard IN ('IFRS S1', 'IFRS S2')),
  estimated_impact TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sitemap_rec_analysis ON sitemap_recommendations(analysis_id);
CREATE INDEX idx_sitemap_rec_priority ON sitemap_recommendations(priority);

COMMENT ON TABLE sitemap_recommendations IS 'Recommended web pages a company should add to improve ESG disclosure';

-- ============================================================
-- Auto-update updated_at trigger
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
DO $$
DECLARE
  tbl TEXT;
BEGIN
  FOR tbl IN
    SELECT unnest(ARRAY[
      'icb_subsectors',
      'ftse_themes',
      'ftse_indicators',
      'ifrs_requirements',
      'analyses',
      'analysis_ftse_results',
      'analysis_ifrs_results',
      'sitemap_recommendations'
    ])
  LOOP
    EXECUTE format(
      'CREATE TRIGGER trigger_updated_at_%I
       BEFORE UPDATE ON %I
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at_column()',
      tbl, tbl
    );
  END LOOP;
END;
$$;

-- ============================================================
-- Row Level Security (RLS) — enable but allow all for now
-- ============================================================
ALTER TABLE icb_subsectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE ftse_themes ENABLE ROW LEVEL SECURITY;
ALTER TABLE ftse_indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE ftse_indicator_subsectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE ifrs_requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_ftse_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_ifrs_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE sitemap_recommendations ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users full access (adjust later for production)
DO $$
DECLARE
  tbl TEXT;
BEGIN
  FOR tbl IN
    SELECT unnest(ARRAY[
      'icb_subsectors',
      'ftse_themes',
      'ftse_indicators',
      'ftse_indicator_subsectors',
      'ifrs_requirements',
      'analyses',
      'analysis_ftse_results',
      'analysis_ifrs_results',
      'sitemap_recommendations'
    ])
  LOOP
    EXECUTE format(
      'CREATE POLICY "Allow authenticated access" ON %I
       FOR ALL
       TO authenticated
       USING (true)
       WITH CHECK (true)',
      tbl
    );
  END LOOP;
END;
$$;

-- Also allow anon read for reference tables
DO $$
DECLARE
  tbl TEXT;
BEGIN
  FOR tbl IN
    SELECT unnest(ARRAY[
      'icb_subsectors',
      'ftse_themes',
      'ftse_indicators',
      'ftse_indicator_subsectors',
      'ifrs_requirements'
    ])
  LOOP
    EXECUTE format(
      'CREATE POLICY "Allow anon read" ON %I
       FOR SELECT
       TO anon
       USING (true)',
      tbl
    );
  END LOOP;
END;
$$;

-- ============================================================
-- Seed Data: FTSE 14 Themes with Pillar Mapping
-- ============================================================
INSERT INTO ftse_themes (pillar, pillar_code, theme_name, theme_order, description) VALUES
  -- Environmental (5 themes)
  ('Environmental', 'E', 'Biodiversity', 1,
   'Land use, deforestation, ecosystem impact, biodiversity protection, and habitat management'),
  ('Environmental', 'E', 'Climate Change', 2,
   'GHG emissions Scope 1/2/3, energy use, climate strategy, TCFD, transition and physical risks'),
  ('Environmental', 'E', 'Pollution & Resources', 3,
   'Waste management, pollution prevention, circular economy, and hazardous materials'),
  ('Environmental', 'E', 'Supply Chain: Environmental', 4,
   'Environmental standards for suppliers, supply chain environmental risk management'),
  ('Environmental', 'E', 'Water Security', 5,
   'Water use, water stress, water recycling targets, and water risk management'),

  -- Social (5 themes)
  ('Social', 'S', 'Customer Responsibility', 6,
   'Product safety, data privacy, responsible marketing, and quality management'),
  ('Social', 'S', 'Health & Safety', 7,
   'Occupational health, workplace safety, accident rates, and safety management systems'),
  ('Social', 'S', 'Human Rights & Community', 8,
   'Human rights due diligence, community engagement, indigenous rights, and impact assessment'),
  ('Social', 'S', 'Labour Standards', 9,
   'Fair wages, working hours, freedom of association, diversity, and forced/child labour prevention'),
  ('Social', 'S', 'Supply Chain: Social', 10,
   'Supply chain labour standards, supplier code of conduct, and supplier assessment'),

  -- Governance (4 themes)
  ('Governance', 'G', 'Anti-Corruption', 11,
   'Bribery prevention, whistleblowing, anti-corruption training, and ethical conduct'),
  ('Governance', 'G', 'Corporate Governance', 12,
   'Board structure, independence, executive compensation, CEO/Chair separation, and shareholder rights'),
  ('Governance', 'G', 'Risk Management', 13,
   'Enterprise risk management, ESG risk integration, fines, and audit processes'),
  ('Governance', 'G', 'Tax Transparency', 14,
   'Tax strategy, country-by-country reporting, and tax governance');

-- ============================================================
-- Done! Verify table creation
-- ============================================================
SELECT table_name, (
  SELECT COUNT(*) FROM information_schema.columns c
  WHERE c.table_name = t.table_name AND c.table_schema = 'public'
) AS column_count
FROM information_schema.tables t
WHERE t.table_schema = 'public'
  AND t.table_type = 'BASE TABLE'
ORDER BY t.table_name;
