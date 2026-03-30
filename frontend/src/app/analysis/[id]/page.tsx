'use client';

import { useEffect, useState, useCallback, useRef, use, useMemo } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  ChevronDown,
  Globe,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  XCircle,
} from 'lucide-react';
import { ScoreCard } from '@/components/ScoreCard';
import { AnalysisProgress } from '@/components/AnalysisProgress';
import { WebsiteArchitecture } from '@/components/WebsiteArchitecture';
import { getAnalysis } from '@/lib/api';
import type { AnalysisDetail, FtseResultItem, StatusType } from '@/lib/types';
import { cn } from '@/lib/utils';

const POLL_INTERVAL_MS = 5000;

function isSafeUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:' || parsed.protocol === 'http:';
  } catch {
    return false;
  }
}
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

/* ─── Theme Card ─── */

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
                  {r.source_url && isSafeUrl(r.source_url) && (
                    <a
                      href={r.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 inline-flex items-center gap-1 text-[11px] text-emerald-600 hover:text-emerald-700 hover:underline"
                    >
                      <ExternalLink className="h-3 w-3" />
                      {r.source_page_title || 'View source'}
                    </a>
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
  const [activeTab, setActiveTab] = useState<'ftse' | 'architecture'>('ftse');
  const tabBarRef = useRef<HTMLDivElement>(null);

  const fetchData = useCallback(async () => {
    try {
      const result = await getAnalysis(id);
      setData(result);
      setError(null);
      return result.analysis.status;
    } catch (err) {
      if (err instanceof Error && 'statusCode' in err && (err as { statusCode: number }).statusCode === 404) {
        setError('Analysis not found.');
        return 'failed';
      }
      // Transient network error — keep polling
      return data?.analysis.status ?? 'pending';
    }
  }, [id, data?.analysis.status]);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | null = null;
    let cancelled = false;

    const poll = async () => {
      if (cancelled) { return; }
      const status = await fetchData();
      if (!cancelled && IN_PROGRESS_STATUSES.has(status)) {
        timer = setTimeout(poll, POLL_INTERVAL_MS);
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (timer) { clearTimeout(timer); }
    };
  }, [fetchData]);

  const ftseResults = useMemo(() => data?.ftse_results ?? [], [data?.ftse_results]);
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
      <div role="status" aria-label="Loading analysis" className="flex items-center justify-center py-32">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-foreground border-t-transparent" aria-hidden="true" />
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
    { key: 'architecture' as const, label: 'Website Architecture', count: sitemap_recommendations.length },
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

        {activeTab === 'architecture' && (
          <WebsiteArchitecture
            crawledUrls={analysis.crawled_urls}
            recommendations={sitemap_recommendations}
            companyName={companyDisplayName}
            ftseResults={ftseResults}
          />
        )}
      </div>
    </div>
  );
}
