/**
 * TypeScript interfaces matching backend Pydantic schemas.
 */

export interface SubsectorItem {
  code: string;
  name: string;
  industry_name: string;
  supersector_name: string;
}

export interface AnalysisListItem {
  id: string;
  status: string;
  company_url: string;
  company_name: string | null;
  overall_score: number | null;
  environmental_score: number | null;
  social_score: number | null;
  governance_score: number | null;
  ifrs_s1_score: number | null;
  ifrs_s2_score: number | null;
  pages_crawled: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface FtseThemeInfo {
  theme_name: string;
  pillar: 'Environmental' | 'Social' | 'Governance';
  pillar_code: string;
}

export interface FtseIndicatorInfo {
  indicator_code: string;
  indicator_name: string;
  theme_id: string;
  ftse_themes: FtseThemeInfo;
}

export interface FtseResultItem {
  id: string;
  status: 'found' | 'partial' | 'missing';
  score: number | null;
  evidence: string | null;
  confidence: number | null;
  ai_reasoning: string | null;
  ftse_indicators: FtseIndicatorInfo;
}

export interface IfrsRequirementInfo {
  paragraph_ref: string;
  standard: string;
  chapter: string;
  section: string;
  requirement_text: string;
  is_mandatory: boolean;
}

export interface IfrsResultItem {
  id: string;
  status: 'found' | 'partial' | 'missing';
  evidence: string | null;
  confidence: number | null;
  ai_reasoning: string | null;
  ifrs_requirements: IfrsRequirementInfo;
}

export interface SitemapRecommendation {
  id: string;
  page_title?: string;
  page_path?: string | null;
  recommended_page_title?: string;
  recommended_page_path?: string | null;
  reason: string;
  priority: 'high' | 'medium' | 'low';
}

export interface ThemeSummary {
  theme_name: string;
  pillar: 'Environmental' | 'Social' | 'Governance';
  total: number;
  found: number;
  partial: number;
  missing: number;
  score: number;
}

export interface AnalysisDetail {
  analysis: AnalysisListItem & {
    subsector_id: string | null;
    theme_summaries?: ThemeSummary[];
  };
  ftse_results: FtseResultItem[];
  ifrs_results: IfrsResultItem[];
  sitemap_recommendations: SitemapRecommendation[];
}

export interface AnalysisListResponse {
  analyses: AnalysisListItem[];
  total: number;
}

export interface CreateAnalysisResponse {
  analysis_id: string;
  status: string;
  message: string;
}

export type StatusType = 'found' | 'partial' | 'missing';
export type PriorityType = 'high' | 'medium' | 'low';
