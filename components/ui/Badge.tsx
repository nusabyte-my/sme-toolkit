import React from 'react';
import { cn } from '../../utils/cn';

interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'indigo';
  size?: 'sm' | 'md' | 'lg';
  color?: 'royal' | 'midnight' | 'dark' | 'baby' | 'indigo' | 'emerald' | 'amber' | 'purple' | 'pink' | 'cyan';
  children: React.ReactNode;
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  size = 'md',
  color = 'royal',
  children,
  className
}) => {
  const baseClasses = 'inline-flex items-center font-medium rounded-full transition-all duration-200';
  
  const variantClasses = {
    default: {
      royal: 'bg-[#dbeafe] text-[#1863d6] border border-[#1863d6]/20',
      midnight: 'bg-[#f1f5f9] text-[#001f3d] border border-[#001f3d]/20',
      dark: 'bg-[#e0e7ff] text-[#151983] border border-[#151983]/20',
      baby: 'bg-[#f1f5f9] text-[#64748b] border border-[#b6cbe1]/30',
      indigo: 'bg-indigo-50 text-indigo-700 border border-indigo-500/20',
      emerald: 'bg-emerald-50 text-emerald-700 border border-emerald-500/20',
      amber: 'bg-amber-50 text-amber-700 border border-amber-500/20',
      purple: 'bg-purple-50 text-purple-700 border border-purple-500/20',
      pink: 'bg-pink-50 text-pink-700 border border-pink-500/20',
      cyan: 'bg-cyan-50 text-cyan-700 border border-cyan-500/20'
    },
    success: 'bg-[#d1fae5] text-[#10b981] border border-[#10b981]/20',
    warning: 'bg-[#fef3c7] text-[#f59e0b] border border-[#f59e0b]/20',
    error: 'bg-[#fee2e2] text-[#ef4444] border border-[#ef4444]/20',
    info: 'bg-[#dbeafe] text-[#3b82f6] border border-[#3b82f6]/20',
    indigo: 'bg-indigo-600 text-white border border-indigo-600'
  } as const;
  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm'
  };

  const getVariantClass = () => {
    if (variant === 'default') {
      return variantClasses.default[color];
    }
    return variantClasses[variant];
  };

  return (
    <span
      className={cn(
        baseClasses,
        getVariantClass(),
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  );
};

export default Badge;