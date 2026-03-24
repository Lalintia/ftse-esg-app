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

/**
 * Simplified industry categories mapped to ICB subsector codes.
 * Each industry maps to one representative subsector code.
 */
export interface IndustryCategory {
  label: string;
  value: string;
  description: string;
}

export const INDUSTRY_CATEGORIES: IndustryCategory[] = [
  { label: 'Auto-detect from website', value: 'auto', description: 'AI will determine the industry automatically' },
  { label: 'Oil, Gas & Energy', value: '60101010', description: 'Oil & gas producers, pipelines, energy services' },
  { label: 'Electricity & Utilities', value: '65101010', description: 'Electric utilities, gas distribution, water' },
  { label: 'Renewable Energy', value: '60102020', description: 'Solar, wind, alternative energy' },
  { label: 'Mining & Metals', value: '55101010', description: 'Mining, steel, aluminium, precious metals' },
  { label: 'Chemicals', value: '55201010', description: 'Commodity & specialty chemicals' },
  { label: 'Construction & Materials', value: '50201010', description: 'Building materials, construction companies' },
  { label: 'Food & Beverages', value: '45102020', description: 'Food producers, brewers, soft drinks' },
  { label: 'Personal & Household Goods', value: '45201020', description: 'Personal care, household products, tobacco' },
  { label: 'Healthcare & Pharmaceuticals', value: '20103010', description: 'Pharma, biotech, medical devices, hospitals' },
  { label: 'Banks & Financial Services', value: '30101010', description: 'Banks, insurance, financial services' },
  { label: 'Real Estate', value: '35102010', description: 'Property developers, REITs' },
  { label: 'Technology', value: '10101015', description: 'Software, hardware, IT services, semiconductors' },
  { label: 'Telecommunications', value: '15101010', description: 'Telecom operators, mobile, broadband' },
  { label: 'Media & Entertainment', value: '15104025', description: 'Broadcasting, publishing, entertainment' },
  { label: 'Retail & Consumer Services', value: '40201020', description: 'General retailers, specialty stores, e-commerce' },
  { label: 'Travel & Leisure', value: '40501020', description: 'Hotels, airlines, restaurants, tourism' },
  { label: 'Transportation & Logistics', value: '50101010', description: 'Shipping, trucking, railroads, airlines' },
  { label: 'Automobiles & Parts', value: '40101010', description: 'Auto manufacturers, car parts, tyres' },
  { label: 'Industrial & Manufacturing', value: '50201030', description: 'Machinery, electronics, aerospace, defence' },
];

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
