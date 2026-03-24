'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { FtseResultItem, IfrsResultItem, StatusType } from '@/lib/types';

const statusBadgeConfig: Record<StatusType, { label: string; className: string }> = {
  found: { label: 'Found', className: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' },
  partial: { label: 'Partial', className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' },
  missing: { label: 'Missing', className: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' },
};

const StatusBadge = ({ status }: { status: StatusType }) => {
  const config = statusBadgeConfig[status];
  return (
    <Badge variant="outline" className={cn('text-xs font-medium', config.className)}>
      {config.label}
    </Badge>
  );
};

interface FtseGapTableProps {
  results: FtseResultItem[];
}

interface GroupedFtse {
  themeName: string;
  pillar: string;
  items: FtseResultItem[];
  found: number;
  partial: number;
  missing: number;
}

export const FtseGapTable = ({ results }: FtseGapTableProps) => {
  const [expandedThemes, setExpandedThemes] = useState<Set<string>>(new Set());

  const grouped = results.reduce<Record<string, GroupedFtse>>((acc, item) => {
    const theme = item.ftse_indicators.ftse_themes.theme_name;
    if (!acc[theme]) {
      acc[theme] = {
        themeName: theme,
        pillar: item.ftse_indicators.ftse_themes.pillar,
        items: [],
        found: 0,
        partial: 0,
        missing: 0,
      };
    }
    acc[theme].items.push(item);
    acc[theme][item.status]++;
    return acc;
  }, {});

  const themes = Object.values(grouped).sort((a, b) =>
    a.pillar.localeCompare(b.pillar) || a.themeName.localeCompare(b.themeName),
  );

  const toggleTheme = (themeName: string) => {
    setExpandedThemes((prev) => {
      const next = new Set(prev);
      if (next.has(themeName)) {
        next.delete(themeName);
      } else {
        next.add(themeName);
      }
      return next;
    });
  };

  const pillarColor: Record<string, string> = {
    Environmental: 'text-emerald-600 dark:text-emerald-400',
    Social: 'text-blue-600 dark:text-blue-400',
    Governance: 'text-purple-600 dark:text-purple-400',
  };

  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[300px]">Theme / Indicator</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead className="w-[80px]">Score</TableHead>
            <TableHead>Evidence</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {themes.map((theme) => {
            const isExpanded = expandedThemes.has(theme.themeName);
            return (
              <TableRowGroup key={theme.themeName}>
                <TableRow
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => toggleTheme(theme.themeName)}
                >
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span className={pillarColor[theme.pillar] ?? ''}>
                        {theme.pillar}
                      </span>
                      <span className="text-muted-foreground">/</span>
                      <span>{theme.themeName}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1 text-xs">
                      <span className="text-emerald-600">{theme.found}</span>
                      <span className="text-muted-foreground">/</span>
                      <span className="text-yellow-600">{theme.partial}</span>
                      <span className="text-muted-foreground">/</span>
                      <span className="text-red-600">{theme.missing}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {theme.items.length} indicators
                  </TableCell>
                  <TableCell />
                </TableRow>
                {isExpanded &&
                  theme.items.map((item) => (
                    <TableRow key={item.id} className="bg-muted/20">
                      <TableCell className="pl-12 text-sm">
                        <span className="font-mono text-xs text-muted-foreground mr-2">
                          {item.ftse_indicators.indicator_code}
                        </span>
                        {item.ftse_indicators.indicator_name}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={item.status} />
                      </TableCell>
                      <TableCell className="text-sm">
                        {item.score !== null ? item.score.toFixed(1) : '-'}
                      </TableCell>
                      <TableCell className="max-w-xs truncate text-sm text-muted-foreground">
                        {item.evidence ?? '-'}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableRowGroup>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

const TableRowGroup = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>;
};

interface IfrsGapTableProps {
  results: IfrsResultItem[];
}

interface GroupedIfrs {
  chapter: string;
  standard: string;
  items: IfrsResultItem[];
  found: number;
  partial: number;
  missing: number;
}

export const IfrsGapTable = ({ results }: IfrsGapTableProps) => {
  const [expandedChapters, setExpandedChapters] = useState<Set<string>>(new Set());

  const grouped = results.reduce<Record<string, GroupedIfrs>>((acc, item) => {
    const key = `${item.ifrs_requirements.standard} - ${item.ifrs_requirements.chapter}`;
    if (!acc[key]) {
      acc[key] = {
        chapter: item.ifrs_requirements.chapter,
        standard: item.ifrs_requirements.standard,
        items: [],
        found: 0,
        partial: 0,
        missing: 0,
      };
    }
    acc[key].items.push(item);
    acc[key][item.status]++;
    return acc;
  }, {});

  const chapters = Object.values(grouped).sort((a, b) =>
    a.standard.localeCompare(b.standard) || a.chapter.localeCompare(b.chapter),
  );

  const toggleChapter = (key: string) => {
    setExpandedChapters((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[300px]">Chapter / Requirement</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead className="w-[100px]">Mandatory</TableHead>
            <TableHead>Evidence</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {chapters.map((chapter) => {
            const key = `${chapter.standard} - ${chapter.chapter}`;
            const isExpanded = expandedChapters.has(key);
            return (
              <TableRowGroup key={key}>
                <TableRow
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => toggleChapter(key)}
                >
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      )}
                      <Badge variant="outline" className="text-xs">
                        {chapter.standard}
                      </Badge>
                      <span>{chapter.chapter}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1 text-xs">
                      <span className="text-emerald-600">{chapter.found}</span>
                      <span className="text-muted-foreground">/</span>
                      <span className="text-yellow-600">{chapter.partial}</span>
                      <span className="text-muted-foreground">/</span>
                      <span className="text-red-600">{chapter.missing}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {chapter.items.length} items
                  </TableCell>
                  <TableCell />
                </TableRow>
                {isExpanded &&
                  chapter.items.map((item) => (
                    <TableRow key={item.id} className="bg-muted/20">
                      <TableCell className="pl-12 text-sm">
                        <span className="font-mono text-xs text-muted-foreground mr-2">
                          {item.ifrs_requirements.paragraph_ref}
                        </span>
                        {item.ifrs_requirements.requirement_text.length > 120
                          ? `${item.ifrs_requirements.requirement_text.slice(0, 120)}...`
                          : item.ifrs_requirements.requirement_text}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={item.status} />
                      </TableCell>
                      <TableCell className="text-sm">
                        {item.ifrs_requirements.is_mandatory ? (
                          <Badge variant="outline" className="bg-red-50 text-red-700 text-xs dark:bg-red-900/20 dark:text-red-400">
                            Required
                          </Badge>
                        ) : (
                          <span className="text-muted-foreground text-xs">Optional</span>
                        )}
                      </TableCell>
                      <TableCell className="max-w-xs truncate text-sm text-muted-foreground">
                        {item.evidence ?? '-'}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableRowGroup>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};
