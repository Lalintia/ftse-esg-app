-- Add crawled_urls JSONB column to store website architecture data
-- Structure: { all_discovered: string[], selected: string[], pages: [{url, title}], pdfs: [{url, filename, chars, pages}] }
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS crawled_urls JSONB DEFAULT NULL;

COMMENT ON COLUMN analyses.crawled_urls IS 'Website architecture data: discovered URLs, selected pages, and PDF downloads';
