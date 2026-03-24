'use client';

import { useEffect, useState } from 'react';
import { Loader2, Globe, Brain, BarChart3, CheckCircle2 } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface AnalysisProgressProps {
  status: string;
  pagesCrawled: number;
}

const steps = [
  { key: 'pending', label: 'Initializing...', icon: Loader2, description: 'Setting up the analysis pipeline' },
  { key: 'crawling', label: 'Crawling Website', icon: Globe, description: 'Discovering and reading web pages' },
  { key: 'analyzing', label: 'AI Analysis', icon: Brain, description: 'Evaluating ESG indicators with AI' },
  { key: 'scoring', label: 'Calculating Scores', icon: BarChart3, description: 'Computing FTSE & IFRS scores' },
  { key: 'completed', label: 'Complete', icon: CheckCircle2, description: 'Analysis finished successfully' },
];

const statusProgress: Record<string, number> = {
  pending: 5,
  crawling: 30,
  analyzing: 60,
  scoring: 85,
  completed: 100,
  failed: 0,
};

export const AnalysisProgress = ({ status, pagesCrawled }: AnalysisProgressProps) => {
  const [animatedProgress, setAnimatedProgress] = useState(0);
  const targetProgress = statusProgress[status] ?? 0;

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedProgress(targetProgress);
    }, 100);
    return () => clearTimeout(timer);
  }, [targetProgress]);

  if (status === 'failed') {
    return (
      <div className="flex flex-col items-center gap-6 py-16">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
          <span className="text-3xl">!</span>
        </div>
        <div className="text-center">
          <h3 className="text-xl font-semibold text-red-600 dark:text-red-400">
            Analysis Failed
          </h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Something went wrong during the analysis. Please try again.
          </p>
        </div>
      </div>
    );
  }

  const currentStepIndex = steps.findIndex((s) => s.key === status);

  return (
    <div className="flex flex-col items-center gap-8 py-16">
      <div className="relative flex h-24 w-24 items-center justify-center">
        <div className="absolute inset-0 animate-ping rounded-full bg-primary/10" />
        <div className="absolute inset-2 animate-pulse rounded-full bg-primary/20" />
        <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
          {status === 'completed' ? (
            <CheckCircle2 className="h-8 w-8 text-primary" />
          ) : (
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          )}
        </div>
      </div>

      <div className="w-full max-w-md space-y-3">
        <Progress value={animatedProgress} className="h-2" />
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>{animatedProgress}%</span>
          {pagesCrawled > 0 && <span>{pagesCrawled} pages crawled</span>}
        </div>
      </div>

      <div className="w-full max-w-sm space-y-3">
        {steps.map((step, index) => {
          const isActive = step.key === status;
          const isDone = index < currentStepIndex;
          const Icon = step.icon;

          return (
            <div
              key={step.key}
              className={cn(
                'flex items-center gap-3 rounded-lg px-4 py-3 transition-all',
                isActive && 'bg-primary/5 ring-1 ring-primary/20',
                isDone && 'opacity-60',
                !isActive && !isDone && 'opacity-30',
              )}
            >
              <Icon
                className={cn(
                  'h-5 w-5 shrink-0',
                  isActive && 'text-primary animate-pulse',
                  isDone && 'text-primary',
                )}
              />
              <div>
                <p className={cn('text-sm font-medium', isActive && 'text-primary')}>
                  {step.label}
                </p>
                <p className="text-xs text-muted-foreground">{step.description}</p>
              </div>
              {isDone && (
                <CheckCircle2 className="ml-auto h-4 w-4 text-primary" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
