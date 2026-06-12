export interface IndustryCategory {
  label: string;
  value: string;
  description: string;
}

// Codes must be valid 8-digit ICB subsector codes that exist in the
// icb_subsectors table (official 173 list) — invalid codes fail backend
// validation with "Invalid subsector code". Prefer codes that have an
// explicit profile in backend/app/utils/sector_themes.py; unmapped codes
// fall back to DEFAULT_THEMES.
export const INDUSTRY_CATEGORIES: IndustryCategory[] = [
  { label: 'Auto-detect from website', value: 'auto', description: 'AI will determine the industry automatically' },
  { label: 'Oil, Gas & Energy', value: '60101000', description: 'Integrated oil & gas, producers, pipelines' },
  { label: 'Electricity & Utilities', value: '65101015', description: 'Conventional electric utilities, power generation' },
  { label: 'Renewable Energy', value: '65101010', description: 'Solar, wind, alternative electricity' },
  { label: 'Mining & Metals', value: '55102000', description: 'General mining, steel, aluminium, precious metals' },
  { label: 'Chemicals', value: '55201000', description: 'Commodity & specialty chemicals' },
  { label: 'Construction & Materials', value: '50101010', description: 'Construction companies, building materials' },
  { label: 'Food & Beverages', value: '45102020', description: 'Food producers, brewers, soft drinks' },
  { label: 'Personal & Household Goods', value: '45201020', description: 'Personal care, household products' },
  { label: 'Healthcare & Pharmaceuticals', value: '20103015', description: 'Pharma, biotech, medical devices, hospitals' },
  { label: 'Banks & Financial Services', value: '30101010', description: 'Banks, insurance, financial services' },
  { label: 'Consumer Finance', value: '30201020', description: 'Consumer lending, leasing, hire purchase' },
  { label: 'Real Estate', value: '35101010', description: 'Property developers, real estate holding' },
  { label: 'Technology', value: '10101015', description: 'Software, hardware, IT services, semiconductors' },
  { label: 'Telecommunications', value: '15102015', description: 'Telecom operators, mobile, broadband' },
  { label: 'Media & Entertainment', value: '40301020', description: 'Broadcasting, publishing, entertainment' },
  { label: 'Retail & Consumer Services', value: '40401010', description: 'General retailers, specialty stores, e-commerce' },
  { label: 'Travel & Leisure', value: '40501025', description: 'Hotels, restaurants, tourism' },
  { label: 'Transportation & Logistics', value: '50206060', description: 'Shipping, trucking, railroads, logistics' },
  { label: 'Automobiles & Parts', value: '40101020', description: 'Auto manufacturers, car parts, tyres' },
  { label: 'Industrial & Manufacturing', value: '50203000', description: 'Machinery, electronics, diversified industrials' },
];
