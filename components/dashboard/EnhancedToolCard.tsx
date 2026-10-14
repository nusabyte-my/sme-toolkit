/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Enhanced tool card 8-state atom */
import React from 'react';
import { ArrowRight, MoreHorizontal, Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';
import { Card, Badge } from '../ui';
import { cn } from '../../utils/cn';

interface ToolUsageStats {
  totalUses: number;
  thisMonth: number;
  trend: 'up' | 'down' | 'neutral';
}

interface QuickAction {
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  color: string;
}

interface ProgressIndicator {
  current: number;
  total: number;
  label: string;
}

interface EnhancedToolCardProps {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: 'royal' | 'midnight' | 'dark' | 'baby' | 'emerald' | 'amber' | 'pink' | 'cyan' | 'indigo' | 'purple' | 'slate';
  usageStats?: ToolUsageStats;
  quickActions?: QuickAction[];
  progress?: ProgressIndicator;
  disabled?: boolean;
  loading?: boolean;
  error?: string;
  success?: boolean;
  onClick: () => void;
  className?: string;
}

const colorClasses: Record<string, { bg: string; bgLight: string; text: string; border: string; ring: string; progress: string }> = {
  royal: {
    bg: 'bg-rainbow-blue',
    bgLight: 'bg-rainbow-blue/10',
    text: 'text-rainbow-blue',
    border: 'border-rainbow-blue/40',
    ring: 'ring-rainbow-blue/20',
    progress: 'bg-rainbow-blue'
  },
  emerald: {
    bg: 'bg-rainbow-emerald',
    bgLight: 'bg-rainbow-emerald/10',
    text: 'text-rainbow-emerald',
    border: 'border-rainbow-emerald/40',
    ring: 'ring-rainbow-emerald/20',
    progress: 'bg-rainbow-emerald'
  },
  amber: {
    bg: 'bg-rainbow-amber',
    bgLight: 'bg-rainbow-amber/10',
    text: 'text-rainbow-amber',
    border: 'border-rainbow-amber/40',
    ring: 'ring-rainbow-amber/20',
    progress: 'bg-rainbow-amber'
  },
  dark: {
    bg: 'bg-primary-900',
    bgLight: 'bg-primary/10',
    text: 'text-primary',
    border: 'border-primary/40',
    ring: 'ring-primary/20',
    progress: 'bg-primary'
  },
  pink: {
    bg: 'bg-rainbow-pink',
    bgLight: 'bg-rainbow-pink/10',
    text: 'text-rainbow-pink',
    border: 'border-rainbow-pink/40',
    ring: 'ring-rainbow-pink/20',
    progress: 'bg-rainbow-pink'
  },
  cyan: {
    bg: 'bg-rainbow-cyan',
    bgLight: 'bg-rainbow-cyan/10',
    text: 'text-rainbow-cyan',
    border: 'border-rainbow-cyan/40',
    ring: 'ring-rainbow-cyan/20',
    progress: 'bg-rainbow-cyan'
  },
  midnight: {
    bg: 'bg-primary-800',
    bgLight: 'bg-primary/15',
    text: 'text-primary',
    border: 'border-primary/40',
    ring: 'ring-primary/20',
    progress: 'bg-primary'
  },
  baby: {
    bg: 'bg-rainbow-cyan',
    bgLight: 'bg-rainbow-cyan/10',
    text: 'text-rainbow-cyan',
    border: 'border-rainbow-cyan/40',
    ring: 'ring-rainbow-cyan/20',
    progress: 'bg-rainbow-cyan'
  },
  indigo: {
    bg: 'bg-primary',
    bgLight: 'bg-primary/10',
    text: 'text-primary',
    border: 'border-primary/40',
    ring: 'ring-primary/20',
    progress: 'bg-primary'
  },
  purple: {
    bg: 'bg-primary',
    bgLight: 'bg-primary/10',
    text: 'text-primary',
    border: 'border-primary/40',
    ring: 'ring-primary/20',
    progress: 'bg-primary'
  },
  slate: {
    bg: 'bg-muted-foreground',
    bgLight: 'bg-muted',
    text: 'text-muted-foreground',
    border: 'border-border',
    ring: 'ring-border/40',
    progress: 'bg-muted-foreground'
  }
};

const EnhancedToolCard: React.FC<EnhancedToolCardProps> = ({
  id,
  title,
  description,
  icon,
  color,
  usageStats,
  progress,
  disabled = false,
  loading = false,
  error,
  success = false,
  onClick,
  className
}) => {
  const colors = colorClasses[color] || colorClasses.indigo;

  return (
    <Card 
      data-tool-id={id}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label={`Open ${title}`}
      aria-disabled={disabled}
      aria-busy={loading}
      onKeyDown={(e) => {
        if (!disabled && !loading && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
      onClick={() => {
        if (!disabled && !loading) {
          onClick();
        }
      }}
      className={cn(
        'group relative bg-card text-card-foreground rounded-xl p-4 cursor-pointer overflow-hidden border transition-all duration-200 shadow-xs select-none',
        // 8-state interactive discipline
        // Hover
        !disabled && !loading && 'hover:-translate-y-0.5 hover:shadow-brand hover:border-primary/40',
        // Focus-visible
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        // Active
        !disabled && !loading && 'active:translate-y-0 active:scale-[0.99]',
        // Disabled
        disabled && 'opacity-40 cursor-not-allowed pointer-events-none',
        // Error
        error && 'border-destructive ring-1 ring-destructive/30',
        // Success
        success && 'border-rainbow-emerald ring-1 ring-rainbow-emerald/30',
        className
      )}
    >
      <div className="flex justify-between items-start mb-3">
        <div className={`p-2 rounded-lg ${colors.bgLight} ${colors.text} ring-1 ${colors.ring} transition-all duration-200 group-hover:scale-105`}>
          {icon}
        </div>
        <div className="flex items-center gap-1.5">
          {loading && (
            <Loader2 className="w-4 h-4 text-primary animate-spin" />
          )}
          {error && (
            <AlertTriangle className="w-4 h-4 text-destructive" />
          )}
          {success && (
            <CheckCircle2 className="w-4 h-4 text-rainbow-emerald" />
          )}
          <button 
            type="button"
            onClick={(e) => e.stopPropagation()}
            aria-label="Tool options"
            className="text-muted-foreground/60 hover:text-foreground transition-colors p-1 rounded focus-visible:ring-2 focus-visible:ring-ring"
          >
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mb-4">
        <h3 className={`font-bold font-display text-foreground text-sm mb-1 group-hover:${colors.text} transition-colors`}>
          {title}
        </h3>
        <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
          {error ? error : description}
        </p>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-border/50">
        <div className="flex items-center gap-2">
          {usageStats && (
            <Badge
              variant="default"
              size="sm"
              className="bg-muted text-muted-foreground border border-border/60 font-mono transition-colors group-hover:bg-primary/10 group-hover:text-primary group-hover:border-primary/30"
            >
              {usageStats.totalUses} uses
            </Badge>
          )}
        </div>
        
        <div className={`w-6 h-6 rounded-full ${colors.bgLight} flex items-center justify-center ${colors.text} transition-all group-hover:${colors.bg} group-hover:text-white group-hover:translate-x-0.5`}>
          <ArrowRight className="w-3 h-3" />
        </div>
      </div>

      {progress && (
        <div className="absolute bottom-0 left-0 w-full h-1 bg-muted">
          <div 
            className={`h-full ${colors.progress} transition-all duration-500`} 
            style={{ width: `${(progress.current / progress.total) * 100}%` }}
          />
        </div>
      )}
    </Card>
  );
};

export default EnhancedToolCard;
