-- Per-sub-indicator assessment results.
-- Keyed by subpart_code, e.g.
--   {"EBD02_1": {"status": "found", "text": "..."},
--    "EBD02_2": {"status": "missing", "text": "..."}}
-- Text is denormalised from the KB so the frontend can render the
-- checklist without a second lookup.

ALTER TABLE analysis_ftse_results
  ADD COLUMN IF NOT EXISTS subpart_results JSONB;

COMMENT ON COLUMN analysis_ftse_results.subpart_results IS
  'Per-sub-indicator status map {subpart_code: {status, text}}';
