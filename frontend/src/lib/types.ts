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
  status_message: string | null;
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

export interface SubpartResult {
  status: 'found' | 'partial' | 'missing';
  text: string;
}

export interface FtseResultItem {
  id: string;
  status: 'found' | 'partial' | 'missing';
  score: number | null;
  evidence: string | null;
  confidence: number | null;
  ai_reasoning: string | null;
  source_url: string | null;
  source_page_title: string | null;
  subpart_results: Record<string, SubpartResult> | null;
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
  estimated_impact?: string | null;
}

export interface RecommendationMeta {
  type: 'new' | 'enhance';
  existing_page_url: string;
  data_to_add: string[];
  addresses_gaps: string[];
}

export function parseRecommendationMeta(rec: SitemapRecommendation): RecommendationMeta {
  if (!rec.estimated_impact) {
    return { type: 'new', existing_page_url: '', data_to_add: [], addresses_gaps: [] };
  }
  try {
    const parsed = JSON.parse(rec.estimated_impact);
    return {
      type: parsed.type === 'enhance' ? 'enhance' : 'new',
      existing_page_url: parsed.existing_page_url || '',
      data_to_add: Array.isArray(parsed.data_to_add)
        ? parsed.data_to_add.filter((item: unknown): item is string => typeof item === 'string').map((item: string) => item.slice(0, 500))
        : [],
      addresses_gaps: Array.isArray(parsed.addresses_gaps)
        ? parsed.addresses_gaps.filter((item: unknown): item is string => typeof item === 'string').map((item: string) => item.slice(0, 20))
        : [],
    };
  } catch {
    return { type: 'new', existing_page_url: '', data_to_add: [], addresses_gaps: [] };
  }
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
    crawled_urls?: CrawledUrls | null;
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

export interface CrawledPageInfo {
  url: string;
  title: string;
}

export interface CrawledPdfInfo {
  url: string;
  filename: string;
  chars: number;
  pages: number;
}

export interface CrawledUrls {
  all_discovered: string[];
  selected: string[];
  pages: CrawledPageInfo[];
  pdfs: CrawledPdfInfo[];
}

export interface PrecheckTheme {
  theme_name: string;
  pillar: string;
  exposure: string;
  indicator_count: number;
  subpart_count: number;
  zero_indicator: boolean;
}

export interface PrecheckResponse {
  company_url: string;
  subsector_code: string;
  subsector_name: string;
  industry_name: string;
  auto_detected: boolean;
  total_themes: number;
  total_indicators: number;
  total_sub_indicators: number;
  themes: PrecheckTheme[];
}
