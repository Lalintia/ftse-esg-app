'use client';

import { cn } from '@/lib/utils';

interface ScoreCardProps {
  score: number;
  maxScore?: number;
  label: string;
  subtitle?: string;
  size?: 'sm' | 'md' | 'lg';
}

const getScoreColor = (score: number, maxScore: number): string => {
  const ratio = score / maxScore;
  if (ratio >= 0.8) { return 'text-emerald-500'; }
  if (ratio >= 0.6) { return 'text-emerald-400'; }
  if (ratio >= 0.4) { return 'text-yellow-500'; }
  if (ratio >= 0.2) { return 'text-orange-500'; }
  return 'text-red-500';
};

const getStrokeColor = (score: number, maxScore: number): string => {
  const ratio = score / maxScore;
  if (ratio >= 0.8) { return 'stroke-emerald-500'; }
  if (ratio >= 0.6) { return 'stroke-emerald-400'; }
  if (ratio >= 0.4) { return 'stroke-yellow-500'; }
  if (ratio >= 0.2) { return 'stroke-orange-500'; }
  return 'stroke-red-500';
};

const sizeConfig = {
  sm: { svgSize: 80, strokeWidth: 6, fontSize: 'text-lg', radius: 32 },
  md: { svgSize: 120, strokeWidth: 8, fontSize: 'text-3xl', radius: 48 },
  lg: { svgSize: 160, strokeWidth: 10, fontSize: 'text-4xl', radius: 64 },
};

export const ScoreCard = ({
  score,
  maxScore = 5,
  label,
  subtitle,
  size = 'md',
}: ScoreCardProps) => {
  const config = sizeConfig[size];
  const circumference = 2 * Math.PI * config.radius;
  const progress = score / maxScore;
  const strokeDashoffset = circumference * (1 - progress);

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: config.svgSize, height: config.svgSize }}>
        <svg
          width={config.svgSize}
          height={config.svgSize}
          viewBox={`0 0 ${config.svgSize} ${config.svgSize}`}
          className="-rotate-90"
        >
          <circle
            cx={config.svgSize / 2}
            cy={config.svgSize / 2}
            r={config.radius}
            fill="none"
            className="stroke-muted"
            strokeWidth={config.strokeWidth}
          />
          <circle
            cx={config.svgSize / 2}
            cy={config.svgSize / 2}
            r={config.radius}
            fill="none"
            className={cn(getStrokeColor(score, maxScore), 'transition-all duration-1000 ease-out')}
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn(config.fontSize, 'font-bold', getScoreColor(score, maxScore))}>
            {score.toFixed(1)}
          </span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-sm font-semibold">{label}</p>
        {subtitle && (
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        )}
      </div>
    </div>
  );
};
