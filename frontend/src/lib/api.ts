/**
 * API client for communicating with the FastAPI backend.
 */

import type {
  AnalysisDetail,
  AnalysisListResponse,
  CreateAnalysisResponse,
  PrecheckResponse,
} from '@/lib/types';

// All API calls go through the Next.js proxy route — API key is injected server-side.
const API_BASE = '/api/proxy';

class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const DEFAULT_TIMEOUT_MS = 15_000;
// Creating an analysis can take >15s when the database is cold (e.g. Supabase
// resuming from pause) — the backend still succeeds, so allow a longer wait
// before aborting to avoid showing a false failure to the user.
const CREATE_ANALYSIS_TIMEOUT_MS = 60_000;

async function request<T>(
  path: string,
  options?: RequestInit,
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      let message = `Request failed with status ${response.status}`;
      try {
        const errorBody = await response.text();
        const parsed = JSON.parse(errorBody);
        if (parsed.detail && typeof parsed.detail === 'string') {
          message = parsed.detail;
        }
      } catch {
        // keep default message
      }
      throw new ApiError(response.status, message);
    }

    return response.json() as Promise<T>;
  } finally {
    clearTimeout(timeoutId);
  }
}

export type { IndustryCategory } from '@/lib/constants';
export { INDUSTRY_CATEGORIES } from '@/lib/constants';

export const createAnalysis = (
  companyUrl: string,
  subsectorCode: string,
): Promise<CreateAnalysisResponse> => {
  return request<CreateAnalysisResponse>(
    '/analyses',
    {
      method: 'POST',
      body: JSON.stringify({
        company_url: companyUrl,
        subsector_code: subsectorCode,
      }),
    },
    CREATE_ANALYSIS_TIMEOUT_MS,
  );
};

// Auto-detect mode fetches the homepage + one AI call — allow more than the
// default read timeout but far less than a full analysis.
const PRECHECK_TIMEOUT_MS = 45_000;

export const precheckAnalysis = (
  companyUrl: string,
  subsectorCode: string,
): Promise<PrecheckResponse> => {
  return request<PrecheckResponse>(
    '/precheck',
    {
      method: 'POST',
      body: JSON.stringify({
        company_url: companyUrl,
        subsector_code: subsectorCode,
      }),
    },
    PRECHECK_TIMEOUT_MS,
  );
};

export const getAnalysis = (id: string): Promise<AnalysisDetail> => {
  return request<AnalysisDetail>(`/analyses/${id}`);
};

export const getAnalyses = (
  limit = 20,
  offset = 0,
): Promise<AnalysisListResponse> => {
  return request<AnalysisListResponse>(
    `/analyses?limit=${limit}&offset=${offset}`,
  );
};

export { ApiError };
