/**
 * API client for communicating with the FastAPI backend.
 */

import type {
  AnalysisDetail,
  AnalysisListResponse,
  CreateAnalysisResponse,
  SubsectorItem,
} from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';

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

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new ApiError(
      response.status,
      `API Error ${response.status}: ${errorBody}`,
    );
  }

  return response.json() as Promise<T>;
}

export const fetchSubsectors = (): Promise<SubsectorItem[]> => {
  return request<SubsectorItem[]>('/subsectors');
};

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
