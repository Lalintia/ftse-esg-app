'use client';

import { useEffect, useState } from 'react';
import { Loader2, Globe, Brain, BarChart3, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnalysisProgressProps {
  status: string;
  pagesCrawled: number;
  statusMessage: string | null;
}

const steps = [
  { key: 'pending', label: 'Initializing', icon: Loader2, description: 'Setting up analysis pipeline' },
  { key: 'crawling', label: 'Crawling', icon: Globe, description: 'Reading web pages' },
  { key: 'analyzing', label: 'Analysing', icon: Brain, description: 'Evaluating ESG indicators' },
  { key: 'scoring', label: 'Scoring', icon: BarChart3, description: 'Computing scores' },
  { key: 'completed', label: 'Complete', icon: CheckCircle2, description: 'Analysis finished' },
];

const statusProgress: Record<string, number> = {
  pending: 5,
  crawling: 30,
  analyzing: 60,
  scoring: 85,
  completed: 100,
  failed: 0,
};

export const AnalysisProgress = ({ status, pagesCrawled, statusMessage }: AnalysisProgressProps) => {
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
      <div role="alert" className="flex flex-col items-center gap-6 py-20">
        <div className="flex h-16 w-16 items-center justify-center rounded-full border-2 border-red-300 bg-red-50">
          <span className="text-xl font-bold text-red-600">!</span>
        </div>
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-700">Analysis Failed</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Something went wrong. Please try again.
          </p>
        </div>
      </div>
    );
  }

  const currentStepIndex = steps.findIndex((s) => s.key === status);

  return (
    <div className="flex flex-col items-center gap-10 py-20">
      {/* Spinner */}
      <div className="relative flex h-20 w-20 items-center justify-center">
        <div className="absolute inset-0 animate-ping rounded-full bg-foreground/5" />
        <div className="relative flex h-14 w-14 items-center justify-center rounded-full border-2 border-foreground/10">
          {status === 'completed' ? (
            <CheckCircle2 className="h-7 w-7 text-foreground" />
          ) : (
            <Loader2 className="h-7 w-7 animate-spin text-foreground" />
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full max-w-sm space-y-2">
        <div
          className="h-1 w-full overflow-hidden rounded-full bg-muted"
          role="progressbar"
          aria-valuenow={animatedProgress}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Analysis progress: ${animatedProgress}%`}
        >
          <div
            className="h-full rounded-full bg-foreground transition-all duration-700 ease-out"
            style={{ width: `${animatedProgress}%` }}
          />
        </div>
        <div className="flex justify-between text-[11px] text-muted-foreground">
          <span>{animatedProgress}%</span>
          {pagesCrawled > 0 && <span>{pagesCrawled} pages</span>}
        </div>
        {statusMessage && (
          <p aria-live="polite" aria-atomic="true" className="mt-2 text-center text-xs text-muted-foreground animate-pulse">
            {statusMessage}
          </p>
        )}
      </div>

      {/* Steps */}
      <div className="w-full max-w-xs space-y-2">
        {steps.map((step, index) => {
          const isActive = step.key === status;
          const isDone = index < currentStepIndex;
          const Icon = step.icon;

          return (
            <div
              key={step.key}
              className={cn(
                'flex items-center gap-3 rounded-lg px-4 py-2.5 transition-all',
                isActive && 'bg-foreground/5',
                isDone && 'opacity-50',
                !isActive && !isDone && 'opacity-20',
              )}
            >
              <Icon
                className={cn(
                  'h-4 w-4 shrink-0',
                  isActive && 'animate-pulse text-foreground',
                  isDone && 'text-foreground',
                )}
              />
              <div className="flex-1">
                <p className="text-sm font-medium">{step.label}</p>
              </div>
              {isDone && (
                <CheckCircle2 className="h-3.5 w-3.5 text-foreground/60" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
