'use client';

import { useEffect, useState, useCallback, useRef, use, useMemo } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  ChevronDown,
  ChevronRight,
  Globe,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  LayoutGrid,
  Minus,
} from 'lucide-react';
import { ScoreCard } from '@/components/ScoreCard';
import { AnalysisProgress } from '@/components/AnalysisProgress';
import { getAnalysis } from '@/lib/api';
import type { AnalysisDetail, FtseResultItem, SitemapRecommendation, StatusType } from '@/lib/types';
import { cn } from '@/lib/utils';

const POLL_INTERVAL_MS = 5000;
const IN_PROGRESS_STATUSES = new Set(['pending', 'crawling', 'analyzing', 'scoring']);

interface ThemeGroup {
  theme: string;
  pillar: string;
  results: FtseResultItem[];
  found: number;
  partial: number;
  missing: number;
  avgScore: number;
}

const groupByTheme = (results: FtseResultItem[]): ThemeGroup[] => {
  const map = new Map<string, FtseResultItem[]>();
  for (const r of results) {
    if (!r.ftse_indicators?.ftse_themes) { continue; }
    const theme = r.ftse_indicators.ftse_themes.theme_name;
    if (!map.has(theme)) { map.set(theme, []); }
    map.get(theme)!.push(r);
  }

  const groups: ThemeGroup[] = [];
  for (const [theme, items] of map) {
    const pillar = items[0].ftse_indicators.ftse_themes.pillar;
    const found = items.filter((i) => i.status === 'found').length;
    const partial = items.filter((i) => i.status === 'partial').length;
    const missing = items.filter((i) => i.status === 'missing').length;
    const scores = items.map((i) => i.score ?? 0);
    const avgScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    groups.push({ theme, pillar, results: items, found, partial, missing, avgScore });
  }

  return groups;
};

const groupByPillar = (themes: ThemeGroup[]): Record<string, ThemeGroup[]> => {
  const result: Record<string, ThemeGroup[]> = {
    Environmental: [],
    Social: [],
    Governance: [],
  };
  for (const t of themes) {
    if (result[t.pillar]) {
      result[t.pillar].push(t);
    }
  }
  return result;
};

const StatusIcon = ({ status }: { status: StatusType }) => {
  if (status === 'found') {
    return <CheckCircle2 className="h-3.5 w-3.5 text-[#1a5632]" />;
  }
  if (status === 'partial') {
    return <AlertTriangle className="h-3.5 w-3.5 text-[#92400e]" />;
  }
  return <XCircle className="h-3.5 w-3.5 text-[#991b1b]" />;
};

const StatusBadge = ({ status }: { status: StatusType }) => {
  const styles: Record<StatusType, string> = {
    found: 'bg-[#ecfdf5] text-[#1a5632]',
    partial: 'bg-[#fffbeb] text-[#92400e]',
    missing: 'bg-[#fef2f2] text-[#991b1b]',
  };
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium', styles[status])}>
      <StatusIcon status={status} />
      {status}
    </span>
  );
};

const EmptyState = ({ message }: { message: string }) => (
  <div className="flex items-center justify-center rounded-lg border border-dashed py-16">
    <p className="text-sm text-muted-foreground">{message}</p>
  </div>
);

/* ─── Website Blueprint ─── */

interface BlueprintItem {
  section: string;
  pageTitle: string;
  pagePath: string;
  status: StatusType;
  ftseImpact: string;
  priority: 'high' | 'medium' | 'low';
  description: string;
}

const ESG_BLUEPRINT_TEMPLATE: Omit<BlueprintItem, 'status'>[] = [
  // ESG Overview
  { section: 'ESG Overview', pageTitle: 'ESG Highlights', pagePath: '/esg', ftseImpact: 'Overall +0.3', priority: 'high', description: 'Key ESG visual, company ESG index, highlight performance, key targets & achievements' },
  { section: 'ESG Overview', pageTitle: 'ESG Calendar', pagePath: '/esg/calendar', ftseImpact: 'Overall +0.1', priority: 'low', description: 'Upcoming ESG events, reporting dates, stakeholder meetings' },
  { section: 'ESG Overview', pageTitle: 'ESG Objectives & Targets', pagePath: '/esg/objectives', ftseImpact: 'Overall +0.2', priority: 'high', description: 'Key targets, achievement progress, measurable KPIs' },
  // Sustainability
  { section: 'Sustainability', pageTitle: 'Sustainability Framework', pagePath: '/sustainability', ftseImpact: 'Overall +0.2', priority: 'high', description: 'Introduction, framework, governance, president advisory' },
  { section: 'Sustainability', pageTitle: 'SDGs Alignment', pagePath: '/sustainability/sdgs', ftseImpact: 'Overall +0.2', priority: 'medium', description: 'Contribution to UN Sustainable Development Goals & ESG alignment' },
  { section: 'Sustainability', pageTitle: 'Materiality Assessment', pagePath: '/sustainability/materiality', ftseImpact: 'Overall +0.3', priority: 'high', description: 'Material ESG topics identification and prioritization matrix' },
  { section: 'Sustainability', pageTitle: 'Stakeholder Engagement', pagePath: '/sustainability/stakeholders', ftseImpact: 'Social +0.2', priority: 'medium', description: 'Stakeholder identification, engagement approach, feedback channels' },
  // Environment
  { section: 'Environment', pageTitle: 'Climate Change', pagePath: '/sustainability/environment/climate-change', ftseImpact: 'Environmental +0.5', priority: 'high', description: 'GHG emissions, climate risk, TCFD alignment, reduction targets' },
  { section: 'Environment', pageTitle: 'Biodiversity', pagePath: '/sustainability/environment/biodiversity', ftseImpact: 'Environmental +0.3', priority: 'medium', description: 'Biodiversity impact, conservation programs, land use management' },
  { section: 'Environment', pageTitle: 'Water Security', pagePath: '/sustainability/environment/water', ftseImpact: 'Environmental +0.3', priority: 'medium', description: 'Water consumption, recycling rate, water risk assessment' },
  { section: 'Environment', pageTitle: 'Supply Chain (Environment)', pagePath: '/sustainability/environment/supply-chain', ftseImpact: 'Environmental +0.2', priority: 'medium', description: 'Environmental criteria for suppliers, supply chain emissions' },
  // Social
  { section: 'Social', pageTitle: 'Corporate Responsibility', pagePath: '/sustainability/social/responsibility', ftseImpact: 'Social +0.3', priority: 'high', description: 'Community engagement, social programs, impact measurement' },
  { section: 'Social', pageTitle: 'Health and Safety', pagePath: '/sustainability/social/health-safety', ftseImpact: 'Social +0.4', priority: 'high', description: 'OHS policy, incident rates, safety programs, certifications' },
  { section: 'Social', pageTitle: 'Human Rights', pagePath: '/sustainability/social/human-rights', ftseImpact: 'Social +0.3', priority: 'high', description: 'Human rights policy, due diligence, community impact assessment' },
  { section: 'Social', pageTitle: 'Labor Standards', pagePath: '/sustainability/social/labor', ftseImpact: 'Social +0.3', priority: 'medium', description: 'Labor practices, diversity & inclusion, fair wages, working conditions' },
  { section: 'Social', pageTitle: 'Supply Chain (Social)', pagePath: '/sustainability/social/supply-chain', ftseImpact: 'Social +0.2', priority: 'medium', description: 'Social criteria for suppliers, labor audits, fair trade' },
  // Governance
  { section: 'Governance', pageTitle: 'Anti-corruption', pagePath: '/governance/anti-corruption', ftseImpact: 'Governance +0.4', priority: 'high', description: 'Anti-corruption policy, whistleblower channels, training programs' },
  { section: 'Governance', pageTitle: 'Corporate Governance', pagePath: '/governance/corporate', ftseImpact: 'Governance +0.4', priority: 'high', description: 'Board structure, independence, committee charters, governance policies' },
  { section: 'Governance', pageTitle: 'Risk Management', pagePath: '/governance/risk', ftseImpact: 'Governance +0.3', priority: 'high', description: 'Enterprise risk framework, ESG risk integration, mitigation strategies' },
  { section: 'Governance', pageTitle: 'Tax Transparency', pagePath: '/governance/tax', ftseImpact: 'Governance +0.2', priority: 'medium', description: 'Tax strategy, country-by-country reporting, tax governance' },
  // Reporting
  { section: 'Reporting', pageTitle: 'Sustainability Report', pagePath: '/reports/sustainability', ftseImpact: 'Overall +0.3', priority: 'high', description: 'Annual sustainability/ESG report (PDF download + online flipbook)' },
  { section: 'Reporting', pageTitle: 'ESG Data & Factsheet', pagePath: '/reports/esg-data', ftseImpact: 'Overall +0.2', priority: 'medium', description: 'ESG performance data, KPI summary, downloadable factsheet' },
  // Contact
  { section: 'Contact', pageTitle: 'ESG Contact / CTA', pagePath: '/contact/esg', ftseImpact: 'Overall +0.1', priority: 'low', description: 'ESG inquiry form, sustainability team contact, FAQ' },
];

const SECTION_ORDER = ['ESG Overview', 'Sustainability', 'Environment', 'Social', 'Governance', 'Reporting', 'Contact'];

const SECTION_ICONS: Record<string, string> = {
  'ESG Overview': '◈',
  'Sustainability': '◉',
  'Environment': '●',
  'Social': '●',
  'Governance': '●',
  'Reporting': '◎',
  'Contact': '○',
};

const SECTION_PILLAR_MAP: Record<string, string> = {
  'ESG Overview': 'Overall',
  'Sustainability': 'Overall',
  'Environment': 'Environmental',
  'Social': 'Social',
  'Governance': 'Governance',
  'Reporting': 'Overall',
  'Contact': 'Overall',
};

function matchBlueprintToSitemap(
  recommendations: SitemapRecommendation[],
  crawledPages: number,
): BlueprintItem[] {
  const recTexts = recommendations.map((r) =>
    `${r.page_title ?? ''} ${r.recommended_page_title ?? ''} ${r.reason ?? ''} ${r.page_path ?? ''} ${r.recommended_page_path ?? ''}`.toLowerCase()
  );

  return ESG_BLUEPRINT_TEMPLATE.map((template) => {
    const keywords = template.pageTitle.toLowerCase().split(/\s+/);
    const pathKeywords = template.pagePath.toLowerCase().split('/').filter(Boolean);
    const allKeywords = [...keywords, ...pathKeywords];

    const matchScore = recTexts.reduce((best, text, idx) => {
      const hits = allKeywords.filter((kw) => text.includes(kw)).length;
      const ratio = hits / allKeywords.length;
      return ratio > best.ratio ? { ratio, idx } : best;
    }, { ratio: 0, idx: -1 });

    let status: StatusType = 'missing';
    if (matchScore.ratio >= 0.4) {
      const rec = recommendations[matchScore.idx];
      if (rec.page_path || rec.page_title) {
        status = rec.priority === 'low' ? 'found' : 'partial';
      }
    } else if (crawledPages > 10 && matchScore.ratio >= 0.2) {
      status = 'partial';
    }

    return { ...template, status };
  });
}

interface BlueprintSectionGroup {
  section: string;
  items: BlueprintItem[];
  found: number;
  partial: number;
  missing: number;
  total: number;
}

function groupBlueprintBySection(items: BlueprintItem[]): BlueprintSectionGroup[] {
  const map = new Map<string, BlueprintItem[]>();
  for (const item of items) {
    if (!map.has(item.section)) { map.set(item.section, []); }
    map.get(item.section)!.push(item);
  }

  return SECTION_ORDER
    .filter((s) => map.has(s))
    .map((section) => {
      const sectionItems = map.get(section)!;
      return {
        section,
        items: sectionItems,
        found: sectionItems.filter((i) => i.status === 'found').length,
        partial: sectionItems.filter((i) => i.status === 'partial').length,
        missing: sectionItems.filter((i) => i.status === 'missing').length,
        total: sectionItems.length,
      };
    });
}

const BlueprintCompleteness = ({ groups }: { groups: BlueprintSectionGroup[] }) => {
  const total = groups.reduce((s, g) => s + g.total, 0);
  const found = groups.reduce((s, g) => s + g.found, 0);
  const partial = groups.reduce((s, g) => s + g.partial, 0);
  const pct = total > 0 ? Math.round(((found + partial * 0.5) / total) * 100) : 0;

  return (
    <div className="mb-8 rounded-lg border bg-card p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <LayoutGrid className="h-4 w-4 text-muted-foreground" />
          <div>
            <h3 className="text-sm font-semibold">Website Completeness</h3>
            <p className="text-[11px] text-muted-foreground">
              {found + partial}/{total} sections covered — based on ESG best-practice template
            </p>
          </div>
        </div>
        <span className={cn(
          'text-2xl font-bold tracking-tight',
          pct >= 70 ? 'text-[#1a5632]' : pct >= 40 ? 'text-[#92400e]' : 'text-[#991b1b]',
        )}>
          {pct}%
        </span>
      </div>
      {/* Progress bar */}
      <div className="h-2 w-full rounded-full bg-[#e8e8e3] overflow-hidden">
        <div className="flex h-full">
          <div
            className="h-full bg-[#1a5632] transition-all duration-700 ease-out"
            style={{ width: `${(found / total) * 100}%` }}
          />
          <div
            className="h-full bg-[#d4a017] transition-all duration-700 ease-out"
            style={{ width: `${(partial / total) * 100}%` }}
          />
        </div>
      </div>
      <div className="mt-2 flex items-center gap-4 text-[10px] text-muted-foreground">
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-full bg-[#1a5632]" /> {found} found
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-full bg-[#d4a017]" /> {partial} partial
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-full bg-[#e8e8e3] border border-[#d4d4cf]" /> {total - found - partial} missing
        </span>
      </div>
    </div>
  );
};

const BlueprintSectionCard = ({ group }: { group: BlueprintSectionGroup }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const completePct = group.total > 0
    ? Math.round(((group.found + group.partial * 0.5) / group.total) * 100)
    : 0;

  return (
    <div className="rounded-lg border bg-card transition-all hover:border-foreground/20">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        className="flex w-full items-center justify-between p-4 text-left"
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <span className="text-muted-foreground text-xs select-none">{SECTION_ICONS[group.section] ?? '○'}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-semibold truncate">{group.section}</h4>
              <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                {SECTION_PILLAR_MAP[group.section]}
              </span>
            </div>
            <div className="mt-1.5 flex items-center gap-2">
              {/* Mini progress bar */}
              <div className="h-1 w-20 rounded-full bg-[#e8e8e3] overflow-hidden">
                <div className="flex h-full">
                  <div className="h-full bg-[#1a5632]" style={{ width: `${(group.found / group.total) * 100}%` }} />
                  <div className="h-full bg-[#d4a017]" style={{ width: `${(group.partial / group.total) * 100}%` }} />
                </div>
              </div>
              <span className="text-[11px] text-muted-foreground">
                {group.found + group.partial}/{group.total}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3 shrink-0 ml-3">
          {group.missing > 0 && (
            <span className="rounded-full bg-[#fef2f2] px-2 py-0.5 text-[10px] font-medium text-[#991b1b]">
              {group.missing} missing
            </span>
          )}
          <ChevronDown className={cn('h-4 w-4 text-muted-foreground transition-transform', isExpanded && 'rotate-180')} />
        </div>
      </button>

      {isExpanded && (
        <div className="border-t px-4 py-3">
          <div className="space-y-1.5">
            {group.items.map((item) => (
              <div
                key={item.pagePath}
                className={cn(
                  'flex items-start gap-3 rounded-md px-3 py-2.5 transition-colors',
                  item.status === 'missing'
                    ? 'bg-[#fef2f2]/50 border border-dashed border-[#991b1b]/20'
                    : item.status === 'partial'
                      ? 'bg-[#fffbeb]/50'
                      : 'bg-muted/30',
                )}
              >
                <StatusIcon status={item.status} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-semibold">{item.pageTitle}</span>
                    <span className={cn(
                      'rounded-full px-1.5 py-px text-[9px] font-medium',
                      item.priority === 'high' && 'bg-[#fef2f2] text-[#991b1b]',
                      item.priority === 'medium' && 'bg-[#fffbeb] text-[#92400e]',
                      item.priority === 'low' && 'bg-[#f0f4ff] text-[#3b5998]',
                    )}>
                      {item.priority}
                    </span>
                    {item.status === 'missing' && (
                      <span className="text-[9px] font-medium text-[#1a5632] bg-[#ecfdf5] px-1.5 py-px rounded-full">
                        {item.ftseImpact}
                      </span>
                    )}
                  </div>
                  <p className="mt-0.5 font-mono text-[10px] text-muted-foreground">{item.pagePath}</p>
                  {item.status === 'missing' && (
                    <p className="mt-1 text-[11px] leading-relaxed text-muted-foreground">
                      {item.description}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const WebsiteBlueprint = ({
  recommendations,
  pagesCrawled,
}: {
  recommendations: SitemapRecommendation[];
  pagesCrawled: number;
}) => {
  const blueprintItems = useMemo(
    () => matchBlueprintToSitemap(recommendations, pagesCrawled),
    [recommendations, pagesCrawled],
  );
  const sectionGroups = useMemo(
    () => groupBlueprintBySection(blueprintItems),
    [blueprintItems],
  );

  return (
    <div>
      <BlueprintCompleteness groups={sectionGroups} />
      <div className="space-y-3">
        {sectionGroups.map((group) => (
          <BlueprintSectionCard key={group.section} group={group} />
        ))}
      </div>
    </div>
  );
};

const ThemeCard = ({ group }: { group: ThemeGroup }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const total = group.results.length;
  const mainStatus: StatusType = group.found > total / 2 ? 'found' : group.missing > total / 2 ? 'missing' : 'partial';

  return (
    <div className="rounded-lg border bg-card transition-all hover:border-foreground/20">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        className="flex w-full items-start justify-between p-4 text-left"
      >
        <div className="flex-1">
          <div className="mb-1 flex items-center gap-2">
            <StatusBadge status={mainStatus} />
          </div>
          <h4 className="text-sm font-semibold">{group.theme}</h4>
          <p className="mt-0.5 text-xs text-muted-foreground">
            {total} indicators — {group.found} found, {group.partial} partial, {group.missing} missing
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold tracking-tight">
            {group.avgScore.toFixed(1)}
          </span>
          <ChevronDown className={cn(
            'h-4 w-4 text-muted-foreground transition-transform',
            isExpanded && 'rotate-180',
          )} />
        </div>
      </button>

      {isExpanded && (
        <div className="border-t px-4 py-3">
          <div className="space-y-2">
            {group.results.map((r) => (
              <div key={r.id} className="flex items-start gap-3 rounded-md bg-muted/30 px-3 py-2">
                <StatusIcon status={r.status} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-medium text-muted-foreground">
                      {r.ftse_indicators.indicator_code}
                    </span>
                    <span className="text-xs">{r.ftse_indicators.indicator_name}</span>
                  </div>
                  {r.evidence && (
                    <p className="mt-1 text-[11px] leading-relaxed text-muted-foreground">
                      {r.evidence}
                    </p>
                  )}
                </div>
                {r.score !== null && (
                  <span className="shrink-0 text-xs font-semibold">{r.score}/5</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default function AnalysisDashboard({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [data, setData] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'ftse' | 'blueprint' | 'sitemap'>('ftse');
  const tabBarRef = useRef<HTMLDivElement>(null);

  const fetchData = useCallback(async () => {
    try {
      const result = await getAnalysis(id);
      setData(result);
      return result.analysis.status;
    } catch {
      setError('Failed to load analysis. It may not exist.');
      return 'failed';
    }
  }, [id]);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | null = null;

    const poll = async () => {
      const status = await fetchData();
      if (IN_PROGRESS_STATUSES.has(status)) {
        timer = setTimeout(poll, POLL_INTERVAL_MS);
      }
    };

    poll();

    return () => {
      if (timer) { clearTimeout(timer); }
    };
  }, [fetchData]);

  const ftseResults = data?.ftse_results ?? [];
  const themeGroups = useMemo(() => groupByTheme(ftseResults), [ftseResults]);
  const pillarGroups = useMemo(() => groupByPillar(themeGroups), [themeGroups]);

  if (error) {
    return (
      <div role="alert" className="mx-auto max-w-3xl px-6 py-20 text-center">
        <h2 className="text-lg font-semibold">Error</h2>
        <p className="mt-2 text-sm text-muted-foreground">{error}</p>
        <Link href="/" className="mt-6 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
          Back
        </Link>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-foreground border-t-transparent" />
      </div>
    );
  }

  const { analysis, sitemap_recommendations } = data;
  const isInProgress = IN_PROGRESS_STATUSES.has(analysis.status);

  if (isInProgress) {
    return (
      <div className="mx-auto max-w-lg px-6 py-12">
        <Link href="/" className="mb-8 inline-flex items-center gap-2 text-xs uppercase tracking-[0.1em] text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-3 w-3" />
          Back
        </Link>
        <div className="text-center">
          <h2 className="text-2xl font-bold tracking-tight">Analysing</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {analysis.company_name ?? analysis.company_url}
          </p>
        </div>
        <AnalysisProgress status={analysis.status} pagesCrawled={analysis.pages_crawled} statusMessage={analysis.status_message} />
      </div>
    );
  }

  const companyDisplayName = analysis.company_name ?? (() => {
    try { return new URL(analysis.company_url).hostname; } catch { return analysis.company_url; }
  })();

  const tabs = [
    { key: 'ftse' as const, label: 'FTSE Themes', count: ftseResults.length },
    { key: 'blueprint' as const, label: 'Website Blueprint', count: ESG_BLUEPRINT_TEMPLATE.length },
    { key: 'sitemap' as const, label: 'Sitemap', count: sitemap_recommendations.length },
  ];

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      {/* Nav */}
      <Link href="/" className="mb-8 inline-flex items-center gap-2 text-xs uppercase tracking-[0.1em] text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-3 w-3" />
        Back
      </Link>

      {/* Header */}
      <div className="mb-12 animate-fade-up">
        <h1 className="text-4xl font-bold tracking-[-0.03em] sm:text-5xl">{companyDisplayName}</h1>
        <div className="mt-3 flex items-center gap-4 text-sm text-muted-foreground">
          <a
            href={analysis.company_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-foreground"
          >
            <Globe className="h-3.5 w-3.5" />
            {analysis.company_url}
            <ExternalLink className="h-3 w-3" />
          </a>
          <span>{analysis.pages_crawled} pages</span>
        </div>
      </div>

      {/* Score Hero */}
      <div className="mb-12 grid grid-cols-1 gap-8 sm:grid-cols-4 animate-fade-up-d1">
        <div className="flex justify-center sm:justify-start">
          <ScoreCard
            score={analysis.overall_score ?? 0}
            label="Overall"
            subtitle="out of 5.0"
            size="xl"
          />
        </div>
        <div className="flex justify-center">
          <ScoreCard
            score={analysis.environmental_score ?? 0}
            label="Environmental"
            size="md"
          />
        </div>
        <div className="flex justify-center">
          <ScoreCard
            score={analysis.social_score ?? 0}
            label="Social"
            size="md"
          />
        </div>
        <div className="flex justify-center">
          <ScoreCard
            score={analysis.governance_score ?? 0}
            label="Governance"
            size="md"
          />
        </div>
      </div>

      {/* Tabs — sticky so switching tabs doesn't scroll away */}
      <div ref={tabBarRef} role="tablist" className="sticky top-14 z-40 -mx-6 mb-8 flex gap-1 border-b bg-background/95 backdrop-blur-sm px-6 animate-fade-up-d3">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            role="tab"
            id={`tab-${tab.key}`}
            aria-selected={activeTab === tab.key}
            aria-controls={`tabpanel-${tab.key}`}
            onClick={() => {
              const scrollY = window.scrollY;
              setActiveTab(tab.key);
              requestAnimationFrame(() => {
                window.scrollTo(0, scrollY);
              });
            }}
            className={cn(
              'px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px',
              activeTab === tab.key
                ? 'border-foreground text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground',
            )}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-1.5 text-xs text-muted-foreground">({tab.count})</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content — min-height prevents scroll jump when switching tabs */}
      <div role="tabpanel" id={`tabpanel-${activeTab}`} aria-labelledby={`tab-${activeTab}`} className="min-h-screen animate-fade-up-d4">
        {activeTab === 'ftse' && (
          <div className="space-y-10">
            {(['Environmental', 'Social', 'Governance'] as const).map((pillar) => {
              const themes = pillarGroups[pillar];
              if (!themes || themes.length === 0) { return null; }

              return (
                <div key={pillar}>
                  <h3 className="mb-4 text-xs font-bold uppercase tracking-[0.15em] text-muted-foreground">
                    {pillar}
                  </h3>
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                    {themes.map((group) => (
                      <ThemeCard key={group.theme} group={group} />
                    ))}
                  </div>
                </div>
              );
            })}
            {ftseResults.length === 0 && (
              <EmptyState message="No FTSE indicator results available." />
            )}
          </div>
        )}

        {activeTab === 'blueprint' && (
          <WebsiteBlueprint
            recommendations={sitemap_recommendations}
            pagesCrawled={analysis.pages_crawled}
          />
        )}

        {activeTab === 'sitemap' && (
          sitemap_recommendations.length > 0 ? (
            <div className="space-y-2">
              {sitemap_recommendations.map((item) => {
                const title = item.recommended_page_title || item.page_title || 'Recommended Page';
                const path = item.recommended_page_path || item.page_path;
                return (
                  <div key={item.id} className="rounded-lg border bg-card p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={cn(
                        'rounded-full px-2 py-0.5 text-[11px] font-medium',
                        item.priority === 'high' && 'bg-red-50 text-red-700',
                        item.priority === 'medium' && 'bg-amber-50 text-amber-700',
                        item.priority === 'low' && 'bg-blue-50 text-blue-700',
                      )}>
                        {item.priority}
                      </span>
                      <h4 className="text-sm font-semibold">{title}</h4>
                    </div>
                    {path && (
                      <p className="mb-1.5 font-mono text-xs text-muted-foreground">{path}</p>
                    )}
                    <p className="text-xs text-muted-foreground leading-relaxed">{item.reason}</p>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState message="No sitemap recommendations available." />
          )
        )}
      </div>
    </div>
  );
}
