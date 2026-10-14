/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · KPI overview & rainbow metric metrics */
import React from 'react';
import { TrendingUp, TrendingDown, Users, FileText, Target, Activity } from 'lucide-react';
import { Card } from '../ui';

interface KPISOverviewProps {
  className?: string;
}

interface StatItemProps {
  label: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down';
  icon: React.ReactNode;
  iconBgClass: string;
  iconTextClass: string;
}

const StatItem: React.FC<StatItemProps> = ({ label, value, change, trend, icon, iconBgClass, iconTextClass }) => (
  <div className="flex items-center gap-4 p-4 rounded-xl hover:bg-muted/40 transition-colors cursor-default group border border-transparent hover:border-border/60">
    <div className={`p-3 rounded-xl ${iconBgClass} ${iconTextClass} group-hover:scale-105 transition-transform flex items-center justify-center flex-shrink-0`}>
      {icon}
    </div>
    <div className="min-w-0">
      <p className="text-xs font-mono font-semibold text-muted-foreground uppercase tracking-wider">{label}</p>
      <div className="flex items-baseline gap-2 mt-0.5">
        <span className="text-2xl font-bold font-display text-foreground">{value}</span>
        {change !== undefined && (
          <div className={`flex items-center text-xs font-semibold ${trend === 'up' ? 'text-rainbow-emerald' : 'text-destructive'}`}>
            {trend === 'up' ? <TrendingUp className="w-3.5 h-3.5 mr-0.5" /> : <TrendingDown className="w-3.5 h-3.5 mr-0.5" />}
            {change}%
          </div>
        )}
      </div>
    </div>
  </div>
);

const KPISOverview: React.FC<KPISOverviewProps> = ({ className = '' }) => {
  const kpiData = {
    leadConversion: {
      rate: 3.4,
      change: 0.8,
      trend: 'up' as const
    },
    contentGeneration: {
      total: 42,
      change: 12.5,
      trend: 'up' as const
    },
    engagementScore: {
      score: 7.8,
      change: 0.3,
      trend: 'up' as const
    },
    activeProjects: {
      total: 8
    }
  };

  return (
    <Card className={`p-2 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 divide-y md:divide-y-0 md:divide-x divide-border/50 bg-card border-border shadow-sm rounded-2xl ${className}`}>
      <StatItem
        label="Conversion Rate"
        value={`${kpiData.leadConversion.rate}%`}
        change={kpiData.leadConversion.change}
        trend={kpiData.leadConversion.trend}
        icon={<Users className="w-5 h-5" />}
        iconBgClass="bg-rainbow-violet/10"
        iconTextClass="text-rainbow-violet"
      />
      <StatItem
        label="Content Created"
        value={kpiData.contentGeneration.total}
        change={kpiData.contentGeneration.change}
        trend={kpiData.contentGeneration.trend}
        icon={<FileText className="w-5 h-5" />}
        iconBgClass="bg-rainbow-cyan/10"
        iconTextClass="text-rainbow-cyan"
      />
      <StatItem
        label="Engagement Score"
        value={kpiData.engagementScore.score}
        change={kpiData.engagementScore.change}
        trend={kpiData.engagementScore.trend}
        icon={<Target className="w-5 h-5" />}
        iconBgClass="bg-rainbow-pink/10"
        iconTextClass="text-rainbow-pink"
      />
      <StatItem
        label="Active Projects"
        value={kpiData.activeProjects.total}
        icon={<Activity className="w-5 h-5" />}
        iconBgClass="bg-rainbow-emerald/10"
        iconTextClass="text-rainbow-emerald"
      />
    </Card>
  );
};

export default KPISOverview;
