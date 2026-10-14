/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Growth score hero & canvas metrics */
import React from 'react';
import {
  TrendingUp,
  Target,
  Briefcase,
  Zap,
  ArrowRight,
  LayoutGrid
} from 'lucide-react';
import { GrowthScore, AppView } from '../../types';

interface GrowthScoreHeroProps {
  score: GrowthScore | null;
  onNavigate?: (view: AppView) => void;
}

const GrowthScoreHero: React.FC<GrowthScoreHeroProps> = ({ score, onNavigate }) => {
  if (!score) {
    return (
      <div className="bg-card rounded-2xl p-8 text-center border border-border shadow-sm">
        <LayoutGrid className="w-12 h-12 text-primary mx-auto mb-4" />
        <h3 className="text-xl font-bold font-display text-foreground mb-2">No Growth Score Yet</h3>
        <p className="text-muted-foreground mb-4 max-w-md mx-auto">
          Complete your Business Model Canvas to generate your verified growth score and performance insights.
        </p>
        {onNavigate && (
          <button
            onClick={() => onNavigate(AppView.BMC_HUB)}
            className="inline-flex items-center px-5 py-2.5 bg-gradient-cta text-white font-semibold rounded-xl transition-all shadow-brand hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring active:scale-95"
          >
            Build Business Canvas
            <ArrowRight className="w-4 h-4 ml-2" />
          </button>
        )}
      </div>
    );
  }

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-rainbow-emerald';
    if (grade.startsWith('B')) return 'text-rainbow-cyan';
    if (grade.startsWith('C')) return 'text-rainbow-amber';
    return 'text-destructive';
  };

  const getScoreColor = (scoreValue: number) => {
    if (scoreValue >= 80) return 'stroke-rainbow-emerald';
    if (scoreValue >= 60) return 'stroke-rainbow-cyan';
    if (scoreValue >= 40) return 'stroke-rainbow-amber';
    return 'stroke-destructive';
  };

  const componentIcons = {
    bmc_quality: LayoutGrid,
    strategy_alignment: Target,
    market_readiness: TrendingUp,
    execution_capability: Zap
  };

  const componentLabels = {
    bmc_quality: 'Canvas Quality',
    strategy_alignment: 'Strategy',
    market_readiness: 'Market Readiness',
    execution_capability: 'Execution'
  };

  // Calculate stroke-dasharray for circular progress
  const circumference = 2 * Math.PI * 54; // radius = 54
  const strokeDashoffset = circumference - (score.overall_score / 100) * circumference;

  return (
    <div className="bg-gradient-hero-band rounded-2xl p-6 text-white overflow-hidden relative shadow-brand-lg border border-white/10">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-accent/10 rounded-full blur-2xl translate-y-1/2 -translate-x-1/2 pointer-events-none" />

      <div className="relative flex flex-col lg:flex-row items-center justify-between gap-6">
        {/* Left side - Score display */}
        <div className="flex items-center gap-6">
          {/* Circular Progress in cyan / emerald */}
          <div className="relative flex-shrink-0">
            <svg className="w-32 h-32 -rotate-90">
              {/* Background circle */}
              <circle
                cx="64"
                cy="64"
                r="54"
                fill="none"
                stroke="rgba(255,255,255,0.15)"
                strokeWidth="8"
              />
              {/* Progress circle */}
              <circle
                cx="64"
                cy="64"
                r="54"
                fill="none"
                className={getScoreColor(score.overall_score)}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                style={{ transition: 'stroke-dashoffset 1s ease-out' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold font-display text-white">{Math.round(score.overall_score)}</span>
              <span className="text-xs font-mono text-violet-200/80">of 100</span>
            </div>
          </div>

          {/* Score info */}
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-base text-violet-200/90 font-medium">Growth Score</span>
              <span className={`text-2xl font-bold font-display ${getGradeColor(score.grade)}`}>
                {score.grade}
              </span>
            </div>
            <p className="text-violet-200/90 max-w-md text-sm leading-relaxed">
              {score.summary}
            </p>
            {onNavigate && (
              <button
                onClick={() => onNavigate(AppView.BMC_HUB)}
                className="mt-3 inline-flex items-center text-sm font-semibold text-white/95 hover:text-white transition-colors group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-lg px-2 py-1 -ml-2"
              >
                Improve canvas score
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
              </button>
            )}
          </div>
        </div>

        {/* Right side - Component scores in glass on dark */}
        <div className="grid grid-cols-2 gap-3 w-full lg:w-auto">
          {Object.entries(score.components).map(([key, component]) => {
            const Icon = componentIcons[key as keyof typeof componentIcons] || Briefcase;
            const label = componentLabels[key as keyof typeof componentLabels] || key;
            const isWeakArea = score.improvement_priorities?.includes(key);

            return (
              <div
                key={key}
                className={`p-3 rounded-xl backdrop-blur-md transition-all duration-300 ${
                  isWeakArea ? 'bg-white/10 border border-rainbow-amber/50 shadow-sm' : 'bg-white/10 border border-white/20 hover:bg-white/15'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Icon className="w-4 h-4 text-violet-200" />
                  <span className="text-xs text-violet-200/90 font-medium truncate">{label}</span>
                  {isWeakArea && (
                    <span className="text-xs text-rainbow-amber font-bold">!</span>
                  )}
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-xl font-bold font-display text-white">{Math.round(component.score)}</span>
                  <span className="text-xs font-mono text-violet-200/70">/ 100</span>
                </div>
                <div className="mt-1 h-1.5 bg-white/20 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      component.score >= 80 ? 'bg-rainbow-emerald' :
                      component.score >= 60 ? 'bg-rainbow-cyan' :
                      component.score >= 40 ? 'bg-rainbow-amber' : 'bg-destructive'
                    }`}
                    style={{ width: `${component.score}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Improvement priorities */}
      {score.improvement_priorities && score.improvement_priorities.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/15">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="text-violet-200/80 text-xs font-mono uppercase tracking-wider">Priority focus areas:</span>
            {score.improvement_priorities.map((priority) => (
              <span
                key={priority}
                className="px-2.5 py-1 bg-rainbow-amber/20 border border-rainbow-amber/40 text-rainbow-amber rounded-lg text-xs font-semibold"
              >
                {componentLabels[priority as keyof typeof componentLabels] || priority}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GrowthScoreHero;
