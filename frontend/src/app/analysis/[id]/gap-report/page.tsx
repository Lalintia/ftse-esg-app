'use client';

import { use, useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Printer } from 'lucide-react';
import { getAnalysis } from '@/lib/api';
import type { AnalysisDetail, FtseResultItem } from '@/lib/types';

const PILLAR_ORDER = ['Environmental', 'Social', 'Governance'];

interface ThemeGaps {
  theme: string;
  pillar: string;
  total: number;
  missing: FtseResultItem[];
  partial: FtseResultItem[];
}

const groupGapsByTheme = (results: FtseResultItem[]): ThemeGaps[] => {
  const map = new Map<string, ThemeGaps>();
  for (const r of results) {
    const theme = r.ftse_indicators?.ftse_themes?.theme_name ?? 'Unknown';
    const pillar = r.ftse_indicators?.ftse_themes?.pillar ?? 'Unknown';
    if (!map.has(theme)) {
      map.set(theme, { theme, pillar, total: 0, missing: [], partial: [] });
    }
    const group = map.get(theme)!;
    group.total += 1;
    if (r.status === 'missing') {
      group.missing.push(r);
    } else if (r.status === 'partial') {
      group.partial.push(r);
    }
  }
  return [...map.values()].sort((a, b) => {
    const pa = PILLAR_ORDER.indexOf(a.pillar);
    const pb = PILLAR_ORDER.indexOf(b.pillar);
    return pa !== pb ? pa - pb : a.theme.localeCompare(b.theme);
  });
};

const missingSubparts = (r: FtseResultItem): [string, string][] => {
  if (!r.subpart_results) {
    return [];
  }
  return Object.entries(r.subpart_results)
    .filter(([, sp]) => sp.status === 'missing')
    .map(([code, sp]) => [code, sp.text]);
};

export default function GapReportPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [data, setData] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAnalysis(id)
      .then(setData)
      .catch(() => setError('Failed to load the analysis.'));
  }, [id]);

  if (error) {
    return <div className="mx-auto max-w-3xl p-8 text-sm text-red-700">{error}</div>;
  }
  if (!data) {
    return <div className="mx-auto max-w-3xl p-8 text-sm text-muted-foreground">Loading…</div>;
  }

  const { analysis, ftse_results: results } = data;
  const groups = groupGapsByTheme(results);
  const totalMissing = groups.reduce((n, g) => n + g.missing.length, 0);
  const totalPartial = groups.reduce((n, g) => n + g.partial.length, 0);
  const totalIndicators = results.length;
  const reportDate = analysis.completed_at ?? analysis.created_at;

  return (
    <div className="mx-auto max-w-3xl px-8 py-10 print:max-w-none print:px-0 print:py-0">
      {/* Toolbar — hidden when printing */}
      <div className="mb-8 flex items-center justify-between print:hidden">
        <Link
          href={`/analysis/${id}`}
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to analysis
        </Link>
        <button
          type="button"
          onClick={() => window.print()}
          className="inline-flex items-center gap-2 rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background hover:opacity-90"
        >
          <Printer className="h-4 w-4" />
          Export PDF
        </button>
      </div>

      {/* Report header */}
      <header className="mb-8 border-b-2 border-foreground pb-4">
        <h1 className="text-2xl font-bold">FTSE ESG Gap Report</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {analysis.company_name ?? analysis.company_url}
          {reportDate ? ` — ${new Date(reportDate).toLocaleDateString()}` : ''}
        </p>
      </header>

      {/* Summary */}
      <section className="mb-8 grid grid-cols-4 gap-3 text-center">
        <div className="rounded-lg border px-3 py-3">
          <div className="text-2xl font-bold">{totalIndicators}</div>
          <div className="text-xs text-muted-foreground">Indicators checked</div>
        </div>
        <div className="rounded-lg border px-3 py-3">
          <div className="text-2xl font-bold text-emerald-700">
            {totalIndicators - totalMissing - totalPartial}
          </div>
          <div className="text-xs text-muted-foreground">Found</div>
        </div>
        <div className="rounded-lg border px-3 py-3">
          <div className="text-2xl font-bold text-amber-700">{totalPartial}</div>
          <div className="text-xs text-muted-foreground">Partial</div>
        </div>
        <div className="rounded-lg border px-3 py-3">
          <div className="text-2xl font-bold text-red-700">{totalMissing}</div>
          <div className="text-xs text-muted-foreground">Missing</div>
        </div>
      </section>

      {/* Per-theme gaps */}
      {groups.map((g) => (
        <section key={g.theme} className="mb-7 break-inside-avoid-page">
          <h2 className="mb-2 border-b pb-1 text-base font-semibold">
            {g.theme}
            <span className="ml-2 text-xs font-normal text-muted-foreground">
              {g.pillar} — {g.total} indicators, {g.missing.length} missing, {g.partial.length} partial
            </span>
          </h2>

          {g.missing.length === 0 && g.partial.length === 0 ? (
            <p className="text-sm text-emerald-700">No gaps in this theme.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-muted-foreground">
                  <th className="w-20 py-1 pr-2 font-medium">Code</th>
                  <th className="py-1 pr-2 font-medium">Indicator</th>
                  <th className="w-16 py-1 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {[...g.missing, ...g.partial].map((r) => (
                  <tr key={r.id} className="border-t align-top">
                    <td className="py-1.5 pr-2 font-mono text-xs">
                      {r.ftse_indicators.indicator_code}
                    </td>
                    <td className="py-1.5 pr-2">
                      {r.ftse_indicators.indicator_name}
                      {r.status === 'partial' && missingSubparts(r).length > 0 && (
                        <ul className="mt-1 list-inside list-disc text-xs text-muted-foreground">
                          {missingSubparts(r).map(([code, text]) => (
                            <li key={code}>{text || code}</li>
                          ))}
                        </ul>
                      )}
                    </td>
                    <td className={`py-1.5 text-xs font-semibold ${r.status === 'missing' ? 'text-red-700' : 'text-amber-700'}`}>
                      {r.status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      ))}

      <footer className="mt-10 border-t pt-3 text-xs text-muted-foreground">
        Generated by FTSE ESG Analyzer (esg.ohmai.me) — pre-assessment based on
        publicly disclosed website content; not an official FTSE Russell rating.
      </footer>
    </div>
  );
}
