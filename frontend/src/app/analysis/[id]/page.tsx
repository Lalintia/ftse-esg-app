'use client';

import { useEffect, useState, useCallback, use } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  Download,
  ExternalLink,
  Globe,
  MapPin,
  Shield,
  TreePine,
  Users,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { ScoreCard } from '@/components/ScoreCard';
import { PillarChart } from '@/components/PillarChart';
import { FtseGapTable, IfrsGapTable } from '@/components/GapTable';
import { AnalysisProgress } from '@/components/AnalysisProgress';
import { getAnalysis } from '@/lib/api';
import type { AnalysisDetail, PriorityType } from '@/lib/types';

const POLL_INTERVAL_MS = 5000;
const IN_PROGRESS_STATUSES = new Set(['pending', 'crawling', 'analyzing', 'scoring']);

export default function AnalysisDashboard({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [data, setData] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  if (error) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-12">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600">Error</h2>
          <p className="mt-2 text-muted-foreground">{error}</p>
          <Link href="/">
            <Button variant="outline" className="mt-6">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-12">
        <div className="flex items-center justify-center py-24">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      </div>
    );
  }

  const { analysis, ftse_results, ifrs_results, sitemap_recommendations } = data;
  const isInProgress = IN_PROGRESS_STATUSES.has(analysis.status);

  if (isInProgress) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12">
        <Link href="/" className="mb-8 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
          Back to Home
        </Link>
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Analyzing Website</CardTitle>
            <CardDescription>
              {analysis.company_name ?? analysis.company_url}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AnalysisProgress
              status={analysis.status}
              pagesCrawled={analysis.pages_crawled}
            />
          </CardContent>
        </Card>
      </div>
    );
  }

  const priorityBadge: Record<PriorityType, string> = {
    high: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    low: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  };

  const companyDisplayName = analysis.company_name ?? new URL(analysis.company_url).hostname;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Link href="/" className="mb-3 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Link>
          <h1 className="text-3xl font-bold tracking-tight">{companyDisplayName}</h1>
          <div className="mt-2 flex items-center gap-3 text-sm text-muted-foreground">
            <a
              href={analysis.company_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 hover:text-foreground"
            >
              <Globe className="h-4 w-4" />
              {analysis.company_url}
              <ExternalLink className="h-3 w-3" />
            </a>
            <span>{analysis.pages_crawled} pages crawled</span>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={() => {
            /* PDF export placeholder */
          }}
        >
          <Download className="mr-2 h-4 w-4" />
          Export PDF
        </Button>
      </div>

      {/* Score Overview */}
      <div className="mb-8 grid gap-6 md:grid-cols-2">
        {/* Overall + Pillar Scores */}
        <Card>
          <CardHeader>
            <CardTitle>ESG Score Overview</CardTitle>
            <CardDescription>FTSE Russell scoring methodology (0-5 scale)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center gap-6">
              <ScoreCard
                score={analysis.overall_score ?? 0}
                label="Overall ESG Score"
                subtitle="out of 5.0"
                size="lg"
              />
              <Separator />
              <div className="grid w-full grid-cols-3 gap-4">
                <div className="flex flex-col items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900/30">
                    <TreePine className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <ScoreCard
                    score={analysis.environmental_score ?? 0}
                    label="Environmental"
                    size="sm"
                  />
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
                    <Users className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                  </div>
                  <ScoreCard
                    score={analysis.social_score ?? 0}
                    label="Social"
                    size="sm"
                  />
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/30">
                    <Shield className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                  </div>
                  <ScoreCard
                    score={analysis.governance_score ?? 0}
                    label="Governance"
                    size="sm"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Radar + IFRS */}
        <Card>
          <CardHeader>
            <CardTitle>Pillar Analysis</CardTitle>
            <CardDescription>ESG pillar scores and IFRS compliance</CardDescription>
          </CardHeader>
          <CardContent>
            <PillarChart
              environmental={analysis.environmental_score ?? 0}
              social={analysis.social_score ?? 0}
              governance={analysis.governance_score ?? 0}
            />
            <Separator className="my-4" />
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-4 text-center">
                <p className="text-sm font-medium text-muted-foreground">IFRS S1</p>
                <p className="mt-1 text-2xl font-bold text-primary">
                  {analysis.ifrs_s1_score !== null
                    ? `${Math.min(analysis.ifrs_s1_score, 100).toFixed(0)}%`
                    : 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground">Compliance</p>
              </div>
              <div className="rounded-lg border p-4 text-center">
                <p className="text-sm font-medium text-muted-foreground">IFRS S2</p>
                <p className="mt-1 text-2xl font-bold text-primary">
                  {analysis.ifrs_s2_score !== null
                    ? `${Math.min(analysis.ifrs_s2_score, 100).toFixed(0)}%`
                    : 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground">Compliance</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Results Tabs */}
      <Tabs defaultValue="ftse" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="ftse">
            FTSE Results
            {ftse_results.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {ftse_results.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="ifrs">
            IFRS Results
            {ifrs_results.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {ifrs_results.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="sitemap">
            Sitemap
            {sitemap_recommendations.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {sitemap_recommendations.length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="ftse">
          {ftse_results.length > 0 ? (
            <FtseGapTable results={ftse_results} />
          ) : (
            <EmptyState message="No FTSE indicator results available." />
          )}
        </TabsContent>

        <TabsContent value="ifrs">
          {ifrs_results.length > 0 ? (
            <IfrsGapTable results={ifrs_results} />
          ) : (
            <EmptyState message="No IFRS requirement results available." />
          )}
        </TabsContent>

        <TabsContent value="sitemap">
          {sitemap_recommendations.length > 0 ? (
            <div className="space-y-3">
              {sitemap_recommendations.map((item) => (
                <Card key={item.id}>
                  <CardContent className="flex items-start gap-4 p-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                      <MapPin className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold">{item.page_title}</h4>
                        <Badge
                          variant="outline"
                          className={priorityBadge[item.priority]}
                        >
                          {item.priority}
                        </Badge>
                      </div>
                      {item.page_path && (
                        <p className="mt-1 font-mono text-sm text-muted-foreground">
                          {item.page_path}
                        </p>
                      )}
                      <p className="mt-2 text-sm text-muted-foreground">
                        {item.reason}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <EmptyState message="No sitemap recommendations available." />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

const EmptyState = ({ message }: { message: string }) => (
  <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
    <p className="text-sm text-muted-foreground">{message}</p>
  </div>
);
