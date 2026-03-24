'use client';

import { cn } from '@/lib/utils';

interface ScoreCardProps {
  score: number;
  maxScore?: number;
  label: string;
  subtitle?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const getScoreColor = (score: number, maxScore: number): string => {
  const ratio = score / maxScore;
  if (ratio >= 0.7) { return 'text-[#1a5632]'; }
  if (ratio >= 0.5) { return 'text-[#92400e]'; }
  if (ratio >= 0.3) { return 'text-[#b45309]'; }
  return 'text-[#991b1b]';
};

const getStrokeHex = (score: number, maxScore: number): string => {
  const ratio = score / maxScore;
  if (ratio >= 0.7) { return '#1a5632'; }
  if (ratio >= 0.5) { return '#92400e'; }
  if (ratio >= 0.3) { return '#b45309'; }
  return '#991b1b';
};

const sizeConfig = {
  sm: { svgSize: 72, strokeWidth: 5, fontSize: 'text-base', radius: 28 },
  md: { svgSize: 100, strokeWidth: 6, fontSize: 'text-2xl', radius: 40 },
  lg: { svgSize: 140, strokeWidth: 8, fontSize: 'text-4xl', radius: 56 },
  xl: { svgSize: 180, strokeWidth: 8, fontSize: 'text-5xl', radius: 72 },
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
            stroke="#e5e5e0"
            strokeWidth={config.strokeWidth}
          />
          <circle
            cx={config.svgSize / 2}
            cy={config.svgSize / 2}
            r={config.radius}
            fill="none"
            stroke={getStrokeHex(score, maxScore)}
            className="transition-all duration-1000 ease-out"
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn(config.fontSize, 'font-bold tracking-tight', getScoreColor(score, maxScore))}>
            {score.toFixed(1)}
          </span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground">{label}</p>
        {subtitle && (
          <p className="text-[10px] text-muted-foreground/70">{subtitle}</p>
        )}
      </div>
    </div>
  );
};
