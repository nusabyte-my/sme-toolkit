/**
 * ScoreGauge Component
 * Displays score with circular progress indicator
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React from 'react';
import { cn } from '../../utils/cn';

interface ScoreGaugeProps {
  score: number;
  maxScore?: number;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
  showValue?: boolean;
  className?: string;
  label?: string;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  maxScore = 100,
  size = 120,
  strokeWidth = 8,
  showLabel = true,
  showValue = true,
  className,
  label,
}) => {
  const normalizedScore = Math.min(Math.max(score, 0), maxScore);
  const percentage = (normalizedScore / maxScore) * 100;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  // Determine color based on score
  const getColor = (score: number): string => {
    if (score >= 80) return '#10b981'; // green-500
    if (score >= 60) return '#f59e0b'; // amber-500
    if (score >= 40) return '#f97316'; // orange-500
    return '#ef4444'; // red-500
  };

  const color = getColor(normalizedScore);

  // Determine grade
  const getGrade = (score: number): string => {
    if (score >= 90) return 'A+';
    if (score >= 85) return 'A';
    if (score >= 80) return 'A-';
    if (score >= 75) return 'B+';
    if (score >= 70) return 'B';
    if (score >= 65) return 'B-';
    if (score >= 60) return 'C+';
    if (score >= 55) return 'C';
    if (score >= 50) return 'C-';
    return 'D';
  };

  const grade = getGrade(normalizedScore);

  return (
    <div className={cn('flex flex-col items-center justify-center', className)}>
      <div className="relative" style={{ width: size, height: size }}>
        {/* Background circle */}
        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
          style={{ width: size, height: size }}
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-500 ease-out"
          />
        </svg>
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {showValue && (
            <span className="text-2xl font-bold text-[#0f172a]">
              {Math.round(normalizedScore)}
            </span>
          )}
          {showLabel && (
            <span className="text-xs text-[#94a3b8] mt-1">
              {label || 'Score'}
            </span>
          )}
        </div>
      </div>
      {showValue && (
        <div className="mt-2">
          <span
            className="inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold text-white shadow-lg"
            style={{ backgroundColor: color }}
          >
            {grade}
          </span>
        </div>
      )}
    </div>
  );
};
