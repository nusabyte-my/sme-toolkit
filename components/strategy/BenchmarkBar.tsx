/**
 * BenchmarkBar Component
 * Displays benchmark comparisons with performance indicators
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React from 'react';
import { cn } from '../../utils/cn';
import type { BenchmarkComparison } from '../../types';

interface BenchmarkBarProps {
  benchmark: BenchmarkComparison;
  className?: string;
  showLabels?: boolean;
  height?: number;
}

export const BenchmarkBar: React.FC<BenchmarkBarProps> = ({
  benchmark,
  className,
  showLabels = true,
  height = 24,
}) => {
  const maxValue = Math.max(
    benchmark.your_value,
    benchmark.industry_average,
    benchmark.top_quartile
  );

  const yourWidth = (benchmark.your_value / maxValue) * 100;
  const averageWidth = (benchmark.industry_average / maxValue) * 100;
  const topQuartileWidth = (benchmark.top_quartile / maxValue) * 100;

  const getPerformanceColor = (performance: string): string => {
    switch (performance) {
      case 'above_average':
        return 'bg-[#10b981]';
      case 'average':
        return 'bg-[#1863d6]';
      case 'below_average':
        return 'bg-[#f59e0b]';
      default:
        return 'bg-[#64748b]';
    }
  };

  const getPerformanceLabel = (performance: string): string => {
    switch (performance) {
      case 'above_average':
        return 'Above Average';
      case 'average':
        return 'Average';
      case 'below_average':
        return 'Below Average';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className={cn('w-full', className)}>
      {/* Metric label */}
      {showLabels && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-[#334155]">
            {benchmark.metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </span>
          <span
            className={cn(
              'text-xs font-medium px-2 py-0.5 rounded-full',
              benchmark.performance === 'above_average' && 'bg-[#10b981]/10 text-[#10b981]',
              benchmark.performance === 'average' && 'bg-[#1863d6]/10 text-[#1863d6]',
              benchmark.performance === 'below_average' && 'bg-[#f59e0b]/10 text-[#f59e0b]'
            )}
          >
            {getPerformanceLabel(benchmark.performance)}
          </span>
        </div>
      )}
 
      {/* Bar chart */}
      <div className="relative w-full bg-[#e2e8f0] rounded-full overflow-hidden backdrop-blur-sm" style={{ height }}>
        {/* Top quartile bar */}
        <div
          className="absolute top-0 left-0 h-full bg-[#94a3b8] opacity-30"
          style={{ width: `${topQuartileWidth}%` }}
          title={`Top Quartile: ${benchmark.top_quartile}`}
        />
 
        {/* Industry average bar */}
        <div
          className="absolute top-0 left-0 h-full bg-[#64748b] opacity-50"
          style={{ width: `${averageWidth}%` }}
          title={`Industry Average: ${benchmark.industry_average}`}
        />
 
        {/* Your value bar */}
        <div
          className={cn(
            'absolute top-0 left-0 h-full transition-all duration-500 ease-out',
            getPerformanceColor(benchmark.performance)
          )}
          style={{ width: `${yourWidth}%` }}
          title={`Your Value: ${benchmark.your_value}`}
        />
      </div>

      {/* Legend */}
      {showLabels && (
        <div className="flex items-center gap-4 mt-2 text-xs text-[#94a3b8]">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-[#94a3b8] opacity-30" />
            <span>Top Quartile</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-[#64748b] opacity-50" />
            <span>Industry Avg</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: getPerformanceColor(benchmark.performance) }} />
            <span>Your Value</span>
          </div>
        </div>
      )}

      {/* Values */}
      <div className="flex items-center justify-between mt-1 text-xs text-[#64748b]">
        <span>0</span>
        <span>{Math.round(maxValue)}</span>
      </div>
    </div>
  );
};
