'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Clock, ExternalLink, Leaf, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { SubsectorSelect } from '@/components/SubsectorSelect';
import { createAnalysis, fetchSubsectors, getAnalyses } from '@/lib/api';
import type { AnalysisListItem, SubsectorItem } from '@/lib/types';

export default function HomePage() {
  const router = useRouter();
  const [url, setUrl] = useState('');
  const [subsectorCode, setSubsectorCode] = useState('');
  const [subsectors, setSubsectors] = useState<SubsectorItem[]>([]);
  const [recentAnalyses, setRecentAnalyses] = useState<AnalysisListItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingSubsectors, setIsLoadingSubsectors] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [subsectorData, analysesData] = await Promise.all([
        fetchSubsectors(),
        getAnalyses(5),
      ]);
      setSubsectors(subsectorData);
      setRecentAnalyses(analysesData.analyses);
    } catch {
      setError('Failed to load data. Make sure the backend is running.');
    } finally {
      setIsLoadingSubsectors(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!url.trim()) {
      setError('Please enter a company website URL.');
      return;
    }
    if (!subsectorCode) {
      setError('Please select an ICB subsector.');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await createAnalysis(url.trim(), subsectorCode);
      router.push(`/analysis/${result.analysis_id}`);
    } catch {
      setError('Failed to start analysis. Please check the URL and try again.');
      setIsSubmitting(false);
    }
  };

  const formatDate = (dateStr: string): string => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const statusColor: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    crawling: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    analyzing: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
    scoring: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400',
    completed: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
    failed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Hero */}
      <div className="mb-12 text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-primary/5 px-4 py-1.5 text-sm font-medium text-primary">
          <Sparkles className="h-4 w-4" />
          AI-Powered ESG Analysis
        </div>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          FTSE ESG{' '}
          <span className="bg-gradient-to-r from-emerald-600 to-teal-500 bg-clip-text text-transparent">
            Analyzer
          </span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
          Analyze any company website against FTSE Russell ESG indicators and
          IFRS S1/S2 sustainability standards. Get instant gap analysis with
          actionable recommendations.
        </p>
      </div>

      {/* Analysis Form */}
      <Card className="mb-12 border-2 shadow-lg">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-xl">
            <Leaf className="h-5 w-5 text-primary" />
            Start New Analysis
          </CardTitle>
          <CardDescription>
            Enter a company website URL and select the ICB subsector to begin.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="url" className="text-sm font-medium">
                Company Website URL
              </label>
              <Input
                id="url"
                type="url"
                placeholder="https://www.example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isSubmitting}
                className="h-11"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                ICB Subsector
              </label>
              <SubsectorSelect
                subsectors={subsectors}
                value={subsectorCode}
                onChange={setSubsectorCode}
                disabled={isSubmitting || isLoadingSubsectors}
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}

            <Button
              type="submit"
              size="lg"
              disabled={isSubmitting}
              className="w-full text-base"
            >
              {isSubmitting ? (
                <>Analyzing...</>
              ) : (
                <>
                  Analyze Website
                  <ArrowRight className="ml-2 h-5 w-5" />
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Recent Analyses */}
      {recentAnalyses.length > 0 && (
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <Clock className="h-5 w-5 text-muted-foreground" />
              Recent Analyses
            </h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/history')}
              className="text-muted-foreground"
            >
              View all
              <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
          <Separator className="mb-4" />
          <div className="space-y-3">
            {recentAnalyses.map((analysis) => (
              <Card
                key={analysis.id}
                className="cursor-pointer transition-all hover:border-primary/30 hover:shadow-md"
                onClick={() => router.push(`/analysis/${analysis.id}`)}
              >
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <ExternalLink className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">
                        {analysis.company_name ?? new URL(analysis.company_url).hostname}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(analysis.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {analysis.overall_score !== null && (
                      <span className="text-lg font-bold text-primary">
                        {analysis.overall_score.toFixed(1)}
                      </span>
                    )}
                    <Badge
                      variant="outline"
                      className={statusColor[analysis.status] ?? ''}
                    >
                      {analysis.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
