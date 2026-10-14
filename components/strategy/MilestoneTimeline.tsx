/**
 * MilestoneTimeline Component
 * Displays milestone timeline with status indicators
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React from 'react';
import { CheckCircle2, Circle, Clock } from 'lucide-react';
import { cn } from '../../utils/cn';
import type { Milestone } from '../../types';

interface MilestoneTimelineProps {
  milestones: Milestone[];
  className?: string;
  showProgress?: boolean;
}

export const MilestoneTimeline: React.FC<MilestoneTimelineProps> = ({
  milestones,
  className,
  showProgress = true,
}) => {
  if (!milestones || milestones.length === 0) {
    return (
      <div className={cn('text-center py-8', className)}>
        <span className="text-[#94a3b8]">No milestones defined</span>
      </div>
    );
  }

  const getMilestoneStatus = (targetDate: string): 'completed' | 'in-progress' | 'pending' => {
    const now = new Date();
    const target = new Date(targetDate);
    if (target < now) return 'completed';
    if (target.getTime() - now.getTime() < 30 * 24 * 60 * 60 * 1000) return 'in-progress';
    return 'pending';
  };

  return (
    <div className={cn('space-y-4', className)}>
      {milestones.map((milestone, index) => {
        const status = getMilestoneStatus(milestone.target_date);
        const isLast = index === milestones.length - 1;

        return (
          <div key={index} className="relative">
            {/* Timeline line */}
            {!isLast && (
              <div className="absolute left-4 top-8 w-0.5 h-full bg-[#e2e8f0]" />
            )}

            {/* Milestone item */}
            <div className="flex items-start gap-4">
              {/* Status icon */}
              <div className="relative z-10 flex-shrink-0">
                {status === 'completed' && (
                  <div className="w-8 h-8 rounded-full bg-[#10b981]/10 flex items-center justify-center ring-2 ring-[#10b981]/20">
                    <CheckCircle2 className="w-5 h-5 text-[#10b981]" />
                  </div>
                )}
                {status === 'in-progress' && (
                  <div className="w-8 h-8 rounded-full bg-[#1863d6]/10 flex items-center justify-center ring-2 ring-[#1863d6]/20">
                    <Clock className="w-5 h-5 text-[#1863d6]" />
                  </div>
                )}
                {status === 'pending' && (
                  <div className="w-8 h-8 rounded-full bg-[#94a3b8]/10 flex items-center justify-center ring-2 ring-[#94a3b8]/20">
                    <Circle className="w-5 h-5 text-[#94a3b8]" />
                  </div>
                )}
              </div>

              {/* Milestone content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <h4 className="font-medium text-[#0f172a]">{milestone.milestone}</h4>
                    <p className="text-sm text-[#64748b] mt-1">
                      Target: {new Date(milestone.target_date).toLocaleDateString()}
                    </p>
                  </div>
                  {showProgress && (
                    <span
                      className={cn(
                        'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                        status === 'completed' && 'bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/20',
                        status === 'in-progress' && 'bg-[#1863d6]/10 text-[#1863d6] border border-[#1863d6]/20',
                        status === 'pending' && 'bg-[#94a3b8]/10 text-[#94a3b8] border border-[#94a3b8]/20'
                      )}
                    >
                      {status === 'completed' && 'Completed'}
                      {status === 'in-progress' && 'In Progress'}
                      {status === 'pending' && 'Pending'}
                    </span>
                  )}
                </div>

                {/* Metrics */}
                {milestone.metrics && milestone.metrics.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {milestone.metrics.map((metric, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center px-2 py-1 bg-[#f8fafc] rounded-md text-xs text-[#64748b] border border-[#e2e8f0]"
                      >
                        {metric}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
