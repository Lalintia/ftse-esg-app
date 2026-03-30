-- Add theme_summaries JSONB column to analyses table
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS theme_summaries jsonb;
