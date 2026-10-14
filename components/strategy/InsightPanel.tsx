/**
 * InsightPanel Component
 * Displays AI-generated insights with priority indicators
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React from 'react';
import { Lightbulb, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { cn } from '../../utils/cn';
import type { Insight } from '../../types';

interface InsightPanelProps {
  insights: Insight[];
  className?: string;
  maxInsights?: number;
  showPriority?: boolean;
}

export const InsightPanel: React.FC<InsightPanelProps> = ({
  insights,
  className,
  maxInsights,
  showPriority = true,
}) => {
  if (!insights || insights.length === 0) {
    return (
      <div className={cn('text-center py-8', className)}>
        <Lightbulb className="w-12 h-12 text-[#94a3b8] mx-auto mb-3" />
        <span className="text-[#94a3b8]">No insights available</span>
      </div>
    );
  }

  const displayInsights = maxInsights ? insights.slice(0, maxInsights) : insights;

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'high':
        return 'bg-[#ef4444]/10 text-[#ef4444] border-[#ef4444]/20';
      case 'medium':
        return 'bg-[#f59e0b]/10 text-[#f59e0b] border-[#f59e0b]/20';
      case 'low':
        return 'bg-[#10b981]/10 text-[#10b981] border-[#10b981]/20';
      default:
        return 'bg-[#94a3b8]/10 text-[#64748b] border-[#94a3b8]/20';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="w-4 h-4" />;
      case 'medium':
        return <Info className="w-4 h-4" />;
      case 'low':
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  return (
    <div className={cn('space-y-3', className)}>
      {displayInsights.map((insight, index) => (
        <div
          key={insight.id || index}
          className="backdrop-blur-sm bg-white/80 rounded-lg border border-[#b6cbe1]/30 p-4 hover:shadow-md transition-shadow duration-200"
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Lightbulb className="w-4 h-4 text-[#f59e0b]" />
                <h4 className="font-semibold text-[#0f172a]">{insight.title}</h4>
              </div>
              {showPriority && (
                <span
                  className={cn(
                    'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border',
                    getPriorityColor(insight.priority)
                  )}
                >
                  {getPriorityIcon(insight.priority)}
                  {insight.priority.charAt(0).toUpperCase() + insight.priority.slice(1)} Priority
                </span>
              )}
            </div>
          </div>

          {/* Description */}
          <p className="text-sm text-[#64748b] mb-3">{insight.description}</p>

          {/* Impact */}
          {insight.impact && (
            <div className="mb-3">
              <span className="text-xs text-[#94a3b8]">Expected Impact:</span>
              <span className="ml-2 text-sm font-medium text-[#0f172a]">{insight.impact}</span>
            </div>
          )}

          {/* Actionable Steps */}
          {insight.actionable_steps && insight.actionable_steps.length > 0 && (
            <div className="mt-3 pt-3 border-t border-[#e2e8f0]">
              <p className="text-xs font-medium text-[#334155] mb-2">Actionable Steps:</p>
              <ul className="space-y-1.5">
                {insight.actionable_steps.map((step, idx) => (
                  <li key={idx} className="text-sm text-[#64748b] flex items-start gap-2">
                    <span className="text-[#1863d6] font-medium">{idx + 1}.</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
