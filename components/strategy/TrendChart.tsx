/**
 * TrendChart Component
 * Displays trend data with area and line charts
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React from 'react';
import { cn } from '../../utils/cn';

interface TrendDataPoint {
  date: string;
  value: number;
}

interface TrendChartProps {
  data: TrendDataPoint[];
  height?: number;
  showGrid?: boolean;
  showTooltip?: boolean;
  color?: string;
  className?: string;
  label?: string;
}

export const TrendChart: React.FC<TrendChartProps> = ({
  data,
  height = 200,
  showGrid = true,
  showTooltip = true,
  color = '#1863d6',
  className,
  label,
}) => {
  if (!data || data.length === 0) {
    return (
      <div className={cn('flex items-center justify-center', className)} style={{ height }}>
        <span className="text-[#94a3b8]">No data available</span>
      </div>
    );
  }

  const padding = 20;
  const chartWidth = 100 - padding * 2;
  const chartHeight = height - padding * 2;

  const values = data.map((d) => d.value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const valueRange = maxValue - minValue || 1;

  const points = data.map((point, index) => {
    const x = padding + (index / (data.length - 1)) * chartWidth;
    const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
    return `${x},${y}`;
  });

  const areaPoints = [
    `${padding},${padding + chartHeight}`,
    ...points,
    `${padding + chartWidth},${padding + chartHeight}`,
  ].join(' ');

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!showTooltip) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const index = Math.round(((x - padding) / chartWidth) * (data.length - 1));
    if (index >= 0 && index < data.length) {
      const point = data[index];
      // You could implement a tooltip here
      console.log('Point:', point);
    }
  };

  return (
    <div className={cn('w-full', className)}>
      {label && (
        <div className="text-sm font-medium text-slate-700 mb-2">{label}</div>
      )}
      <svg
        width="100%"
        height={height}
        viewBox={`0 0 100 ${height}`}
        preserveAspectRatio="none"
        onMouseMove={handleMouseMove}
        className="overflow-visible"
      >
        {/* Grid lines */}
        {showGrid && (
          <>
            <line
              x1={padding}
              y1={padding}
              x2={padding + chartWidth}
              y2={padding}
              stroke="#e5e7eb"
              strokeWidth="0.5"
            />
            <line
              x1={padding}
              y1={padding + chartHeight / 2}
              x2={padding + chartWidth}
              y2={padding + chartHeight / 2}
              stroke="#e5e7eb"
              strokeWidth="0.5"
            />
            <line
              x1={padding}
              y1={padding + chartHeight}
              x2={padding + chartWidth}
              y2={padding + chartHeight}
              stroke="#e5e7eb"
              strokeWidth="0.5"
            />
          </>
        )}

        {/* Area fill */}
        <polygon
          points={areaPoints}
          fill={color}
          fillOpacity="0.1"
        />

        {/* Line */}
        <polyline
          points={points.join(' ')}
          fill="none"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {data.map((point, index) => {
          const x = padding + (index / (data.length - 1)) * chartWidth;
          const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
          return (
            <circle
              key={index}
              cx={x}
              cy={y}
              r="1.5"
              fill={color}
              className="hover:r-2 transition-all cursor-pointer"
            />
          );
        })}
      </svg>

      {/* X-axis labels */}
      <div className="flex justify-between text-xs text-slate-500 mt-1 px-1">
        <span>{data[0].date}</span>
        <span>{data[Math.floor(data.length / 2)].date}</span>
        <span>{data[data.length - 1].date}</span>
      </div>
    </div>
  );
};
