/**
 * API client for communicating with the FastAPI backend.
 */

import type {
  AnalysisDetail,
  AnalysisListResponse,
  CreateAnalysisResponse,
} from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '/api';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? '';

class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15_000);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(API_KEY && { 'X-API-Key': API_KEY }),
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
  return request<CreateAnalysisResponse>('/analyses', {
    method: 'POST',
    body: JSON.stringify({
      company_url: companyUrl,
      subsector_code: subsectorCode,
    }),
  });
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
