'use client';

import { useState, useMemo } from 'react';
import { ChevronDown, ExternalLink, FileText, Globe } from 'lucide-react';
import { cn, normalizeUrl } from '@/lib/utils';
import type { CrawledUrls, SitemapRecommendation, PriorityType, FtseResultItem } from '@/lib/types';
import { parseRecommendationMeta } from '@/lib/types';

interface ThemeBadge {
  theme: string;
  score: number;
  pillar: string;
}

interface TreeChild {
  url: string;
  title: string;
  isEsg?: boolean;
}

interface TreePage {
  url: string;
  title: string;
  isEsg?: boolean;
  children: TreeChild[];
  pdfAttachment?: { filename: string; url: string; chars: number; pages: number };
}

interface DomainGroup {
  domain: string;
  pages: TreePage[];
}

function buildUrlThemeMap(
  ftseResults: FtseResultItem[],
  themeSummaries?: { theme_name: string; pillar: string; score: number }[],
): Map<string, ThemeBadge[]> {
  // Build theme score lookup from theme_summaries (the official 0-5 score)
  const themeScoreLookup = new Map<string, { score: number; pillar: string }>();
  if (themeSummaries) {
    for (const ts of themeSummaries) {
      themeScoreLookup.set(ts.theme_name, { score: ts.score, pillar: ts.pillar });
    }
  }

  // Find which themes are referenced by each URL
  const urlThemes = new Map<string, Set<string>>();
  for (const r of ftseResults) {
    if (!r.source_url || !r.ftse_indicators?.ftse_themes) {
      continue;
    }

    let normalized: string;
    try {
      const parsed = new URL(r.source_url);
      normalized = `${parsed.origin}${parsed.pathname}`.replace(/\/$/, '');
    } catch {
      continue;
    }

    const theme = r.ftse_indicators.ftse_themes.theme_name;
    if (!urlThemes.has(normalized)) {
      urlThemes.set(normalized, new Set());
    }
    urlThemes.get(normalized)!.add(theme);
  }

  // Build badges using theme score (not avg indicator score)
  const result = new Map<string, ThemeBadge[]>();
  for (const [url, themes] of urlThemes) {
    const badges: ThemeBadge[] = [];
    for (const theme of themes) {
      const lookup = themeScoreLookup.get(theme);
      if (lookup) {
        badges.push({ theme, score: lookup.score, pillar: lookup.pillar });
      } else {
        // Fallback: use first indicator's pillar, score 0
        badges.push({ theme, score: 0, pillar: 'Environmental' });
      }
    }
    result.set(url, badges);
  }
  return result;
}

interface RecommendedNode {
  title: string;
  path: string;
  reason: string;
  priority: PriorityType;
  parentSection: string;
}

const LABEL_OVERRIDES: Record<string, string> = {
  indexautobacs: 'Autobacs',
  salesarea: 'Sales Area',
  stationrental: 'Station Rental',
  csrstrategy: 'CSR Strategy',
  csrpriorities: 'CSR Priorities',
  newsptgdetail: 'News Detail',
};

function pathToLabel(pathname: string): string {
  const parts = pathname.split('/').filter(Boolean);
  const last = parts[parts.length - 1] || 'Home';

  const override = LABEL_OVERRIDES[last.toLowerCase()];
  if (override) {
    return override;
  }

  return last
    .replace(/[-_]/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function getPageLabel(page: { url: string; title: string }, allTitles: Map<string, number>): string {
  const titleCount = allTitles.get(page.title) || 0;
  if (!page.title || titleCount > 3) {
    try {
      return pathToLabel(new URL(page.url).pathname);
    } catch {
      return page.title || 'Page';
    }
  }
  return page.title;
}

const JUNK_PATH_PATTERNS = [
  /changelang/i,
  /cookiepolicy/i,
  /cookie-policy/i,
  /privacy-?policy/i,
  /^\/menu[a-z]*/i,
];

const JUNK_SECTION_PATTERNS = [
  /^menu/i,
];

const ESG_URL_HINTS = [
  'sustain', 'esg', 'csr', 'governance', 'environment', 'climate',
  'safety', 'human-rights', 'labour', 'labor', 'anti-corruption', 'risk',
  'supply-chain', 'stakeholder', 'diversity', 'employee', 'cybersecurity',
  'materiality', 'whistleblow', 'ethics', 'code-of-conduct',
] as const;

function hasEsgKeyword(url: string): boolean {
  const lower = url.toLowerCase();
  return ESG_URL_HINTS.some((h) => lower.includes(h));
}

function isJunkUrl(pathname: string): boolean {
  return JUNK_PATH_PATTERNS.some((re) => re.test(pathname));
}

function isJunkSection(sectionKey: string): boolean {
  return JUNK_SECTION_PATTERNS.some((re) => re.test(sectionKey));
}

function groupUrlsByDomain(
  crawledUrls: CrawledUrls,
): DomainGroup[] {
  const titleCounts = new Map<string, number>();
  for (const page of crawledUrls.pages) {
    titleCounts.set(page.title, (titleCounts.get(page.title) || 0) + 1);
  }

  const domainMap = new Map<string, Map<string, { url: string; title: string; isEsg?: boolean; children: { url: string; title: string; isEsg?: boolean }[]; _childTitles?: Set<string> }>>();

  // Combine ESG pages + all discovered URLs
  const allPages: { url: string; title: string; isEsg: boolean }[] = [];

  for (const page of crawledUrls.pages) {
    if (page.title.startsWith('PDF:')) { continue; }
    allPages.push({ url: page.url, title: page.title, isEsg: true });
  }

  const addedUrls = new Set(crawledUrls.pages.map((p) => normalizeUrl(p.url)));
  for (const url of crawledUrls.all_discovered) {
    if (addedUrls.has(normalizeUrl(url)) || url.toLowerCase().endsWith('.pdf')) { continue; }
    allPages.push({ url, title: '', isEsg: false });
  }

  for (const page of allPages) {
    try {
      const parsed = new URL(page.url);
      const domain = parsed.hostname;
      const pathParts = parsed.pathname.split('/').filter(Boolean);
      const section = pathParts[0] || '';
      const sectionKey = section || '_root';

      if (isJunkUrl(parsed.pathname) || isJunkSection(sectionKey)) {
        continue;
      }

      const pageLabel = page.title
        ? getPageLabel(page, titleCounts)
        : pathToLabel(parsed.pathname);

      if (!domainMap.has(domain)) {
        domainMap.set(domain, new Map());
      }
      const sections = domainMap.get(domain)!;

      const isInvestorSubdomain = /^(investor|ir)\./i.test(domain);

      if (pathParts.length <= 1) {
        if (!sections.has(sectionKey)) {
          const sectionTitle = sectionKey === '_root'
            ? (isInvestorSubdomain ? 'Investor Relations' : 'Homepage')
            : (isInvestorSubdomain && /^(th|en)$/i.test(section) ? 'Investor Relations' : pathToLabel(section));
          sections.set(sectionKey, {
            url: page.url,
            title: sectionTitle,
            isEsg: page.isEsg,
            children: [],
          });
        }
      } else {
        if (!sections.has(sectionKey)) {
          const sectionTitle = isInvestorSubdomain && /^(th|en)$/i.test(section)
            ? 'Investor Relations'
            : pathToLabel(section);
          sections.set(sectionKey, {
            url: `${parsed.origin}/${section}`,
            title: sectionTitle,
            isEsg: page.isEsg,
            children: [],
          });
        } else if (page.isEsg) {
          sections.get(sectionKey)!.isEsg = true;
        }
        const existing = sections.get(sectionKey)!;
        if (!existing._childTitles) {
          existing._childTitles = new Set(existing.children.map((c) => c.title));
        }
        if (!existing._childTitles.has(pageLabel)) {
          existing._childTitles.add(pageLabel);
          existing.children.push({
            url: page.url,
            title: pageLabel,
            isEsg: page.isEsg,
          });
        }
      }
    } catch {
      continue;
    }
  }

  const pdfsByDomain = new Map<string, Map<string, typeof crawledUrls.pdfs[number]>>();
  for (const pdf of crawledUrls.pdfs) {
    try {
      const parsed = new URL(pdf.url);
      const domain = parsed.hostname;
      const pathParts = parsed.pathname.split('/').filter(Boolean);
      const section = pathParts[0] || '_root';
      if (!pdfsByDomain.has(domain)) {
        pdfsByDomain.set(domain, new Map());
      }
      pdfsByDomain.get(domain)!.set(section, pdf);
    } catch {
      continue;
    }
  }

  const groups: DomainGroup[] = [];
  for (const [domain, sections] of domainMap) {
    const pages = Array.from(sections.values()).map((section) => {
      const domainPdfs = pdfsByDomain.get(domain);
      let pdfAttachment: DomainGroup['pages'][number]['pdfAttachment'];
      if (domainPdfs) {
        for (const [sectionKey, pdf] of domainPdfs) {
          const sectionUrl = new URL(section.url);
          const sectionPath = sectionUrl.pathname.split('/').filter(Boolean)[0] || '_root';
          if (sectionKey === sectionPath) {
            pdfAttachment = { filename: pdf.filename, url: pdf.url, chars: pdf.chars, pages: pdf.pages };
            domainPdfs.delete(sectionKey);
            break;
          }
        }
      }
      return { ...section, pdfAttachment };
    });
    groups.push({ domain, pages });
  }

  // Attach orphan PDFs (from different domains) to the first domain group
  const orphanPdfs: DomainGroup['pages'][number]['pdfAttachment'][] = [];
  for (const [pdfDomain, pdfMap] of pdfsByDomain) {
    if (!domainMap.has(pdfDomain)) {
      for (const [, pdf] of pdfMap) {
        orphanPdfs.push({ filename: pdf.filename, url: pdf.url, chars: pdf.chars, pages: pdf.pages });
      }
    }
  }
  if (orphanPdfs.length > 0 && groups.length > 0) {
    for (const pdf of orphanPdfs) {
      groups[0].pages.push({
        url: pdf!.url,
        title: pdf!.filename.replace(/\.pdf$/i, ''),
        children: [],
        pdfAttachment: pdf,
      });
    }
  }

  return groups;
}

function isSafeHref(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:' || parsed.protocol === 'http:';
  } catch {
    return false;
  }
}

function formatFileSize(chars: number): string {
  const estimatedKb = Math.round(chars / 1024);
  if (estimatedKb > 1024) {
    return `${(estimatedKb / 1024).toFixed(1)} MB`;
  }
  return `${estimatedKb} KB`;
}

const PILLAR_BADGE_COLORS: Record<string, string> = {
  Environmental: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  Social: 'bg-blue-100 text-blue-700 border-blue-200',
  Governance: 'bg-purple-100 text-purple-700 border-purple-200',
};

function TreeNode({ title, isSection, isNew, isDimmed, isEsgHint, priority, children, pdfAttachment, tooltip, themeBadges }: {
  title: string;
  isSection?: boolean;
  isNew?: boolean;
  isDimmed?: boolean;
  isEsgHint?: boolean;
  priority?: PriorityType;
  children?: React.ReactNode;
  pdfAttachment?: { filename: string; url: string; chars: number; pages: number };
  tooltip?: { title: string; path: string; reason: string };
  themeBadges?: ThemeBadge[];
}) {
  const hasBadges = themeBadges && themeBadges.length > 0;
  const showEsgHint = isEsgHint && !hasBadges && !isDimmed && !isNew;

  const nodeClass = cn(
    'inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-all',
    isSection && 'font-semibold px-4 py-2',
    !isNew && !isDimmed && !showEsgHint && 'bg-stone-100 border border-stone-200 text-stone-800',
    !isNew && !isDimmed && !showEsgHint && isSection && 'bg-emerald-50 border-emerald-200 text-emerald-800',
    showEsgHint && 'bg-emerald-50/40 border border-emerald-200/60 text-stone-700',
    showEsgHint && isSection && 'bg-emerald-50/60 border-emerald-200 text-emerald-800',
    isDimmed && 'bg-stone-50/50 border border-stone-100 text-stone-300',
    isNew && priority === 'high' && 'bg-emerald-50/60 border-[1.5px] border-dashed border-emerald-400 text-emerald-700',
    isNew && priority !== 'high' && 'bg-amber-50/60 border-[1.5px] border-dashed border-amber-400 text-amber-700',
  );

  return (
    <div>
      <div className="group relative" tabIndex={tooltip ? 0 : undefined} aria-describedby={tooltip ? `tooltip-${title.replace(/\s+/g, '-')}` : undefined}>
        <span className={nodeClass}>
          {isNew && (
            <span aria-hidden="true" className={cn(
              'h-1.5 w-1.5 rounded-full flex-shrink-0',
              priority === 'high' ? 'bg-emerald-500' : 'bg-amber-500',
            )} />
          )}
          {showEsgHint && (
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 flex-shrink-0" aria-hidden="true" />
          )}
          {title}
          {themeBadges && themeBadges.length > 0 && (
            <span className="inline-flex flex-wrap gap-1 ml-1">
              {themeBadges.map((badge) => (
                <span
                  key={badge.theme}
                  aria-label={`${badge.theme}: score ${badge.score.toFixed(1)} out of 5`}
                  className={cn(
                    'rounded-full border px-1.5 py-0 text-[9px] font-medium leading-4',
                    PILLAR_BADGE_COLORS[badge.pillar] || 'bg-stone-100 text-stone-600 border-stone-200',
                  )}
                >
                  {badge.theme.length > 15 ? badge.theme.slice(0, 13) + '…' : badge.theme} {badge.score.toFixed(1)}
                </span>
              ))}
            </span>
          )}
        </span>
        {tooltip && (
          <div id={`tooltip-${title.replace(/\s+/g, '-')}`} role="tooltip" className="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 w-64 -translate-x-1/2 rounded-lg bg-stone-900 p-3 text-xs text-white opacity-0 shadow-lg transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">
            <p className="font-semibold">{tooltip.title}</p>
            <p className="mt-1 font-mono text-[10px] text-stone-400">{tooltip.path}</p>
            <p className="mt-2 leading-relaxed text-stone-300">{tooltip.reason}</p>
            <span className={cn(
              'mt-2 inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase',
              priority === 'high' ? 'bg-emerald-900/50 text-emerald-300' : 'bg-amber-900/50 text-amber-300',
            )}>
              {priority} priority
            </span>
            <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-stone-900" />
          </div>
        )}
      </div>
      {pdfAttachment && isSafeHref(pdfAttachment.url) && (
        <div className="ml-7 mt-1">
          <a
            href={pdfAttachment.url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${pdfAttachment.filename} (opens in new tab)`}
            className="inline-flex items-center gap-1.5 rounded-md border border-amber-200 bg-amber-50/50 px-2.5 py-1 text-[11px] text-amber-800 hover:bg-amber-100/50"
          >
            <FileText className="h-3 w-3" aria-hidden="true" />
            {pdfAttachment.filename.slice(0, 80)}{pdfAttachment.filename.length > 80 ? '…' : ''}
            <span className="text-stone-400">{pdfAttachment.pages}p</span>
            <ExternalLink className="h-2.5 w-2.5 text-stone-400" aria-hidden="true" />
          </a>
        </div>
      )}
      {children && (
        <ul className="tree-children">
          {children}
        </ul>
      )}
    </div>
  );
}

function DomainSection({ group, isCollapsible, urlThemeMap }: { group: DomainGroup; isCollapsible?: boolean; urlThemeMap?: Map<string, ThemeBadge[]> }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="rounded-lg border border-stone-200 bg-stone-50/30 p-5">
      {isCollapsible ? (
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
          className="flex items-center gap-2 text-xs font-medium cursor-pointer hover:text-stone-700"
        >
          <Globe className="h-3.5 w-3.5 text-stone-400" aria-hidden="true" />
          <span className="font-mono text-stone-500">{group.domain}</span>
          <ChevronDown className={cn('h-3 w-3 text-stone-400 transition-transform', isOpen && 'rotate-180')} aria-hidden="true" />
        </button>
      ) : (
        <div className="flex items-center gap-2 text-xs font-medium">
          <Globe className="h-3.5 w-3.5 text-stone-400" aria-hidden="true" />
          <span className="font-mono text-stone-500">{group.domain}</span>
        </div>
      )}
      {isOpen && (() => {
        const esgPages: TreePage[] = [];
        const otherPages: TreePage[] = [];
        for (const page of group.pages) {
          const isEsg = page.isEsg
            || urlThemeMap?.has(normalizeUrl(page.url))
            || page.children.some((c) => c.isEsg || urlThemeMap?.has(normalizeUrl(c.url)))
            || hasEsgKeyword(page.url);
          (isEsg ? esgPages : otherPages).push(page);
        }

        return (
          <div className="mt-4 space-y-4">
            <div className="flex flex-wrap gap-4">
              {esgPages.map((page) => {
                const sectionBadges = urlThemeMap?.get(normalizeUrl(page.url));
                const sectionHasAnyBadge = !!sectionBadges || page.children.some((c) => urlThemeMap?.has(normalizeUrl(c.url)));
                return (
                  <TreeNode
                    key={page.url}
                    title={page.title}
                    isSection
                    isEsgHint={!sectionHasAnyBadge}
                    pdfAttachment={page.pdfAttachment}
                    themeBadges={sectionBadges}
                  >
                    {page.children.length > 0 && page.children.map((child) => {
                      const childBadges = urlThemeMap?.get(normalizeUrl(child.url));
                      const childIsEsg = child.isEsg || !!childBadges || hasEsgKeyword(child.url);
                      const childDimmed = !childIsEsg;
                      return (
                        <li key={child.url}>
                          <TreeNode title={child.title} isDimmed={childDimmed} isEsgHint={childIsEsg && !childBadges} themeBadges={childBadges} />
                        </li>
                      );
                    })}
                  </TreeNode>
                );
              })}
            </div>
            {otherPages.length > 0 && (
              <OtherPagesGroup pages={otherPages} />
            )}
          </div>
        );
      })()}
    </div>
  );
}

function OtherPagesGroup({ pages }: { pages: TreePage[] }) {
  const [isOpen, setIsOpen] = useState(false);
  const totalChildren = pages.reduce((sum, p) => sum + p.children.length, 0);
  const count = pages.length + totalChildren;

  return (
    <div className="rounded-md border border-stone-100 bg-stone-50/50 px-4 py-2.5">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        className="flex items-center gap-2 text-xs text-stone-400 cursor-pointer hover:text-stone-500"
      >
        <ChevronDown className={cn('h-3 w-3 transition-transform', isOpen && 'rotate-180')} aria-hidden="true" />
        <span>Other pages ({count})</span>
      </button>
      {isOpen && (
        <div className="mt-3 flex flex-wrap gap-2">
          {pages.map((page) => (
            <TreeNode key={page.url} title={page.title} isSection isDimmed>
              {page.children.length > 0 && page.children.map((child) => (
                <li key={child.url}>
                  <TreeNode title={child.title} isDimmed />
                </li>
              ))}
            </TreeNode>
          ))}
        </div>
      )}
    </div>
  );
}

function RecommendedSection({ recommendations }: { recommendations: SitemapRecommendation[] }) {
  const newRecs = recommendations.filter((r) => parseRecommendationMeta(r).type === 'new');

  if (newRecs.length === 0) {
    return null;
  }

  const grouped = new Map<string, SitemapRecommendation[]>();
  for (const rec of newRecs) {
    const path = rec.recommended_page_path || rec.page_path || '/other';
    const section = path.split('/').filter(Boolean)[0] || 'other';
    const sectionTitle = section.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    if (!grouped.has(sectionTitle)) {
      grouped.set(sectionTitle, []);
    }
    grouped.get(sectionTitle)!.push(rec);
  }

  return (
    <div className="rounded-lg border-[1.5px] border-dashed border-emerald-300 bg-emerald-50/20 p-5">
      <div className="flex items-center gap-2 text-xs font-medium text-emerald-600">
        <span aria-hidden="true">✨</span>
        <span>Recommended new sections</span>
      </div>
      <div className="mt-4 flex flex-wrap gap-4">
        {Array.from(grouped).map(([sectionTitle, recs]) => {
          const firstRec = recs[0];
          const sectionPath = firstRec.recommended_page_path || firstRec.page_path || '';
          const topPath = '/' + sectionPath.split('/').filter(Boolean)[0];
          const sectionPriority = firstRec.priority;

          return (
            <TreeNode
              key={sectionTitle}
              title={sectionTitle}
              isSection
              isNew
              priority={sectionPriority}
              tooltip={{
                title: sectionTitle,
                path: topPath,
                reason: `Section covering ${recs.length} recommended page(s).`,
              }}
            >
              {recs.map((rec) => {
                const title = rec.recommended_page_title || rec.page_title || 'Page';
                const path = rec.recommended_page_path || rec.page_path || '';
                return (
                  <li key={rec.id}>
                    <TreeNode
                      title={title}
                      isNew
                      priority={rec.priority}
                      tooltip={{ title, path, reason: rec.reason }}
                    />
                  </li>
                );
              })}
            </TreeNode>
          );
        })}
      </div>
    </div>
  );
}

function EnhancementBadges({ recommendations }: { recommendations: SitemapRecommendation[] }) {
  const enhanceRecs = recommendations.filter((r) => parseRecommendationMeta(r).type === 'enhance');

  if (enhanceRecs.length === 0) {
    return null;
  }

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50/30 p-5">
      <div className="flex items-center gap-2 text-xs font-medium text-amber-700">
        <span aria-hidden="true">📝</span>
        <span>Existing pages that need more data ({enhanceRecs.length})</span>
      </div>
      <div className="mt-3 space-y-2.5">
        {enhanceRecs.map((rec) => {
          const meta = parseRecommendationMeta(rec);
          const title = rec.recommended_page_title || rec.page_title || 'Page';
          return (
            <div key={rec.id} className="rounded-md border border-amber-200 bg-white p-3">
              <div className="flex items-center gap-2 mb-1.5">
                <span className={cn(
                  'rounded-full px-2 py-0.5 text-[10px] font-semibold',
                  rec.priority === 'high' ? 'bg-red-50 text-red-700' : 'bg-amber-50 text-amber-700',
                )}>
                  {rec.priority}
                </span>
                <span className="text-sm font-semibold">{title}</span>
              </div>
              {meta.existing_page_url && isSafeHref(meta.existing_page_url) && (
                <a
                  href={meta.existing_page_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mb-2 inline-flex items-center gap-1 text-[11px] text-emerald-600 hover:underline"
                >
                  <ExternalLink className="h-3 w-3" aria-hidden="true" />
                  View current page
                </a>
              )}
              <p className="text-xs text-muted-foreground leading-relaxed mb-2">{rec.reason}</p>
              {meta.data_to_add.length > 0 && (
                <div>
                  <p className="text-[11px] font-semibold text-stone-600 mb-1">Data to add:</p>
                  <ul className="space-y-0.5">
                    {meta.data_to_add.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-1.5 text-[11px] text-stone-500">
                        <span className="mt-1 h-1 w-1 rounded-full bg-amber-400 flex-shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function WebsiteArchitecture({
  crawledUrls,
  recommendations,
  companyName,
  ftseResults,
  themeSummaries,
}: {
  crawledUrls: CrawledUrls | null | undefined;
  recommendations: SitemapRecommendation[];
  companyName: string;
  ftseResults?: FtseResultItem[];
  themeSummaries?: { theme_name: string; pillar: string; score: number }[];
}) {
  const domainGroups = useMemo(
    () => (crawledUrls ? groupUrlsByDomain(crawledUrls) : []),
    [crawledUrls],
  );

  const urlThemeMap = useMemo(
    () => (ftseResults ? buildUrlThemeMap(ftseResults, themeSummaries) : new Map<string, ThemeBadge[]>()),
    [ftseResults, themeSummaries],
  );

  const recStats = useMemo(() => {
    let enhanceCount = 0;
    let newCount = 0;
    let highCount = 0;
    let medCount = 0;
    for (const r of recommendations) {
      const meta = parseRecommendationMeta(r);
      if (meta.type === 'enhance') { enhanceCount++; } else { newCount++; }
      if (r.priority === 'high') { highCount++; }
      else if (r.priority === 'medium') { medCount++; }
    }
    return { enhanceCount, newCount, highCount, medCount };
  }, [recommendations]);

  if (!crawledUrls) {
    return (
      <div className="rounded-lg border bg-card p-8 text-center text-sm text-muted-foreground">
        Website architecture data not available for this analysis.
      </div>
    );
  }

  const totalExisting = crawledUrls.pages.filter((p) => !p.title.startsWith('PDF:')).length;
  const totalRecommended = recommendations.length;

  return (
    <div className="space-y-6">
      {/* Summary bar */}
      <div className="flex items-center gap-8 rounded-lg border bg-card px-6 py-4">
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold tracking-tight">{totalExisting}</span>
          <span className="text-xs text-muted-foreground">existing pages</span>
        </div>
        <div className="h-8 w-px bg-border" />
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold tracking-tight text-emerald-600">+{totalRecommended}</span>
          <span className="text-xs text-muted-foreground">recommended</span>
        </div>
        <div className="h-8 w-px bg-border" />
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold tracking-tight text-stone-400">{totalExisting + totalRecommended}</span>
          <span className="text-xs text-muted-foreground">total</span>
        </div>
      </div>

      {/* BEFORE */}
      <div className="rounded-xl border-l-4 border-l-stone-300 border border-stone-200 bg-card">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-stone-100 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-stone-500 border border-stone-200">Before</span>
            <span className="text-lg font-bold">Current Website</span>
          </div>
          <span className="font-mono text-xs text-muted-foreground">{totalExisting} pages · {crawledUrls.pdfs.length} PDFs</span>
        </div>
        <div className="p-6">
          <h3 className="mb-5 text-center text-base font-bold">{companyName}</h3>
          <div className="space-y-4">
            {domainGroups.map((group) => (
              <DomainSection key={group.domain} group={group} isCollapsible={domainGroups.length > 1} urlThemeMap={urlThemeMap} />
            ))}
          </div>
        </div>
      </div>

      {/* Transition */}
      <div className="flex items-center gap-5 py-2">
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-emerald-300 to-transparent opacity-30" />
        <div className="flex flex-col items-center gap-1 rounded-xl bg-emerald-50 border border-emerald-200 px-6 py-3">
          <span className="text-lg text-emerald-500">↓</span>
          <span className="text-sm font-bold text-emerald-700">+ {totalRecommended} recommended pages</span>
          <span className="text-xs text-stone-500">
            {recStats.enhanceCount > 0 && <><span className="font-medium">{recStats.enhanceCount}</span> enhance · </>}
            {recStats.newCount > 0 && <><span className="font-medium">{recStats.newCount}</span> new · </>}
            <span className="font-medium">{recStats.highCount}</span> high · <span className="font-medium">{recStats.medCount}</span> medium
          </span>
        </div>
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-emerald-300 to-transparent opacity-30" />
      </div>

      {/* AFTER */}
      <div className="rounded-xl border-l-4 border-l-emerald-500 border border-stone-200 bg-gradient-to-br from-emerald-50/30 to-white">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-emerald-600 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-white">After</span>
            <span className="text-lg font-bold">Recommended Architecture</span>
          </div>
          <span className="font-mono text-xs text-muted-foreground">{totalExisting + totalRecommended} total · +{totalRecommended} new</span>
        </div>
        <div className="p-6">
          <h3 className="mb-5 text-center text-base font-bold">{companyName}</h3>
          <div className="space-y-4">
            {domainGroups.map((group) => (
              <DomainSection key={group.domain} group={group} urlThemeMap={urlThemeMap} />
            ))}
            <EnhancementBadges recommendations={recommendations} />
            <RecommendedSection recommendations={recommendations} />
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-5 rounded-lg bg-stone-50 px-5 py-3 text-xs text-stone-500">
        <span className="font-semibold uppercase tracking-wider text-stone-400">Legend</span>
        <span className="flex items-center gap-2"><span className="h-4 w-6 rounded border border-stone-200 bg-stone-100" /> Existing page</span>
        <span className="flex items-center gap-2"><span className="inline-flex items-center gap-1 h-4 rounded border border-emerald-200/60 bg-emerald-50/40 px-1"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /></span> ESG-related</span>
        <span className="flex items-center gap-2"><span className="h-4 w-6 rounded border border-stone-100 bg-stone-50/50" /> Non-ESG</span>
        <span className="flex items-center gap-2"><span className="h-4 w-6 rounded border-[1.5px] border-dashed border-emerald-400 bg-emerald-50/60" /> Recommended — high</span>
        <span className="flex items-center gap-2"><span className="h-4 w-6 rounded border-[1.5px] border-dashed border-amber-400 bg-amber-50/60" /> Recommended — medium</span>
        <span className="flex items-center gap-2"><span className="h-4 w-6 rounded border border-amber-200 bg-amber-50/50" /> PDF document</span>
      </div>
    </div>
  );
}
