'use client';

import { useMemo } from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
} from 'recharts';

interface PillarChartProps {
  environmental: number;
  social: number;
  governance: number;
}

export const PillarChart = ({
  environmental,
  social,
  governance,
}: PillarChartProps) => {
  const data = useMemo(() => [
    { pillar: 'Environmental', score: environmental, fullMark: 5 },
    { pillar: 'Social', score: social, fullMark: 5 },
    { pillar: 'Governance', score: governance, fullMark: 5 },
  ], [environmental, social, governance]);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart
        outerRadius={100}
        data={data}
      >
        <PolarGrid stroke="#d1d5db" />
        <PolarAngleAxis
          dataKey="pillar"
          tick={{ fontSize: 13, fontWeight: 600, fill: '#1f2937' }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 5]}
          tick={{ fontSize: 11, fill: '#6b7280' }}
          tickCount={6}
        />
        <Radar
          name="Score"
          dataKey="score"
          stroke="#059669"
          fill="#10b981"
          fillOpacity={0.3}
          strokeWidth={2}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
};
