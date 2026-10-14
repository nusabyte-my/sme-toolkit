/**
 * ProgressBar Component
 * Displays progress with customizable colors
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React from 'react';
import { cn } from '../../utils/cn';

interface ProgressBarProps {
  progress: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  showLabel?: boolean;
  showPercentage?: boolean;
  className?: string;
  label?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  max = 100,
  size = 'md',
  color = 'blue',
  showLabel = false,
  showPercentage = true,
  className,
  label,
}) => {
  const normalizedProgress = Math.min(Math.max(progress, 0), max);
  const percentage = (normalizedProgress / max) * 100;

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
  };

  const colorClasses = {
    blue: 'bg-gradient-to-r from-[#1863d6] to-[#151983]',
    green: 'bg-gradient-to-r from-[#10b981] to-[#059669]',
    yellow: 'bg-gradient-to-r from-[#f59e0b] to-[#d97706]',
    red: 'bg-gradient-to-r from-[#ef4444] to-[#dc2626]',
    purple: 'bg-gradient-to-r from-[#9333ea] to-[#7c3aed]',
  };
 
  const bgColorClasses = {
    blue: 'bg-[#1863d6]/10',
    green: 'bg-[#10b981]/10',
    yellow: 'bg-[#f59e0b]/10',
    red: 'bg-[#ef4444]/10',
    purple: 'bg-[#9333ea]/10',
  };

  return (
    <div className={cn('w-full', className)}>
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-1">
          {label && <span className="text-sm font-medium text-[#334155]">{label}</span>}
          {showPercentage && (
            <span className="text-sm text-[#64748b]">{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div className={cn('w-full rounded-full overflow-hidden', bgColorClasses[color], sizeClasses[size])}>
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500 ease-out',
            colorClasses[color]
          )}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={normalizedProgress}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
};
