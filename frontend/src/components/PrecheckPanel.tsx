'use client';

import type { PrecheckResponse } from '@/lib/types';

interface PrecheckPanelProps {
  result: PrecheckResponse;
}

const PILLAR_ORDER = ['Environmental', 'Social', 'Governance'];

const PILLAR_COLORS: Record<string, string> = {
  Environmental: 'text-emerald-700',
  Social: 'text-sky-700',
  Governance: 'text-violet-700',
};

export function PrecheckPanel({ result }: PrecheckPanelProps) {
  const byPillar = PILLAR_ORDER.map((pillar) => ({
    pillar,
    themes: result.themes.filter((t) => t.pillar === pillar),
  })).filter((g) => g.themes.length > 0);

  return (
    <div className="animate-fade-up rounded-lg border bg-card p-6" aria-live="polite">
      <div className="mb-1 text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground">
        Pre-check result
      </div>
      <div className="mb-4 text-sm">
        <span className="font-semibold">{result.subsector_name}</span>
        <span className="text-muted-foreground">
          {' '}({result.subsector_code}
          {result.auto_detected ? ' · auto-detected' : ''})
        </span>
      </div>

      <div className="mb-5 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg border px-3 py-3">
          <div className="text-2xl font-bold">{result.total_themes}</div>
          <div className="text-xs text-muted-foreground">Themes</div>
        </div>
        <div className="rounded-lg border px-3 py-3">
          <div className="text-2xl font-bold">{result.total_indicators}</div>
          <div className="text-xs text-muted-foreground">Indicators</div>
        </div>
        <div className="rounded-lg border px-3 py-3">
          <div className="text-2xl font-bold">{result.total_sub_indicators}</div>
          <div className="text-xs text-muted-foreground">Sub-indicators</div>
        </div>
      </div>

      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-xs uppercase tracking-wide text-muted-foreground">
            <th className="py-2 pr-2 font-medium">Theme</th>
            <th className="py-2 pr-2 font-medium">Exposure</th>
            <th className="py-2 pr-2 text-right font-medium">Indicators</th>
            <th className="py-2 text-right font-medium">Sub-indicators</th>
          </tr>
        </thead>
        <tbody>
          {byPillar.map((group) => (
            <PillarRows key={group.pillar} pillar={group.pillar} themes={group.themes} />
          ))}
        </tbody>
      </table>

      <p className="mt-4 text-xs text-muted-foreground">
        Themes marked “theme-level” apply to this industry but carry no
        checkable indicators — FTSE assigns them a minimum score.
      </p>
    </div>
  );
}

function PillarRows({
  pillar,
  themes,
}: {
  pillar: string;
  themes: PrecheckResponse['themes'];
}) {
  return (
    <>
      <tr>
        <td colSpan={4} className={`pt-3 pb-1 text-xs font-semibold uppercase tracking-wide ${PILLAR_COLORS[pillar] ?? ''}`}>
          {pillar}
        </td>
      </tr>
      {themes.map((t) => (
        <tr key={t.theme_name} className="border-b border-dashed last:border-0">
          <td className="py-1.5 pr-2">
            {t.theme_name}
            {t.zero_indicator && (
              <span className="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] text-amber-800">
                theme-level
              </span>
            )}
          </td>
          <td className="py-1.5 pr-2 text-muted-foreground">{t.exposure}</td>
          <td className="py-1.5 pr-2 text-right tabular-nums">{t.indicator_count}</td>
          <td className="py-1.5 text-right tabular-nums">{t.subpart_count}</td>
        </tr>
      ))}
    </>
  );
}
