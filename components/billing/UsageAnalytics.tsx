import React, { useState, useMemo } from 'react';
import { BarChart3, TrendingUp, TrendingDown, Calendar, Download, Filter, Zap, Image, Video, Bot } from 'lucide-react';
import { useTokens } from '../../hooks/useTokens';

interface UsageDataPoint {
  date: string;
  text_llm: number;
  image_generation: number;
  video_generation: number;
  agent_orchestration: number;
  total: number;
}

interface UsageAnalyticsProps {
  userId?: string;
  period?: 'day' | 'week' | 'month' | 'year';
}

const SERVICE_COLORS = {
  text_llm: { bg: 'bg-blue-500', light: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-600 dark:text-blue-400', icon: Zap },
  image_generation: { bg: 'bg-pink-500', light: 'bg-pink-100 dark:bg-pink-900/30', text: 'text-pink-600 dark:text-pink-400', icon: Image },
  video_generation: { bg: 'bg-red-500', light: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-600 dark:text-red-400', icon: Video },
  agent_orchestration: { bg: 'bg-violet-500', light: 'bg-violet-100 dark:bg-violet-900/30', text: 'text-violet-600 dark:text-violet-400', icon: Bot },
};

const buildDailyData = (usage: { serviceType: string; tokens: number; timestamp: Date }[]): UsageDataPoint[] => {
  const dayMap = new Map<string, UsageDataPoint>();
  const today = new Date();

  for (let i = 29; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const key = date.toISOString().split('T')[0];
    dayMap.set(key, {
      date: key,
      text_llm: 0,
      image_generation: 0,
      video_generation: 0,
      agent_orchestration: 0,
      total: 0,
    });
  }

  usage.forEach((entry) => {
    const key = new Date(entry.timestamp).toISOString().split('T')[0];
    const day = dayMap.get(key);
    if (day) {
      const serviceKey = entry.serviceType as keyof Omit<UsageDataPoint, 'date' | 'total'>;
      if (serviceKey in day) {
        (day as any)[serviceKey] += entry.tokens;
        day.total += entry.tokens;
      }
    }
  });

  return Array.from(dayMap.values());
};

export const UsageAnalytics: React.FC<UsageAnalyticsProps> = ({ userId, period = 'month' }) => {
  const { usage, balance } = useTokens();
  const [selectedPeriod, setSelectedPeriod] = useState(period);
  const [selectedService, setSelectedService] = useState<string | null>(null);

  const data = useMemo(() => buildDailyData(usage), [usage]);

  const totalTokens = data.reduce((sum, d) => sum + d.total, 0);
  const daysWithData = data.filter((d) => d.total > 0).length;
  const avgDaily = daysWithData > 0 ? Math.round(totalTokens / daysWithData) : 0;
  const maxDay = Math.max(...data.map((d) => d.total), 0);
  const nonZeroData = data.filter((d) => d.total > 0);
  const trend =
    nonZeroData.length >= 2
      ? ((nonZeroData[nonZeroData.length - 1].total - nonZeroData[0].total) / Math.max(nonZeroData[0].total, 1)) * 100
      : 0;

  const serviceBreakdown = {
    text_llm: data.reduce((sum, d) => sum + d.text_llm, 0),
    image_generation: data.reduce((sum, d) => sum + d.image_generation, 0),
    video_generation: data.reduce((sum, d) => sum + d.video_generation, 0),
    agent_orchestration: data.reduce((sum, d) => sum + d.agent_orchestration, 0),
  };

  return (
    <div className="bg-card rounded-2xl border border-border shadow-sm overflow-hidden">
      <div className="p-4 border-b border-border bg-gradient-to-r from-muted/50 to-card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Usage Analytics</h3>
              <p className="text-sm text-muted-foreground">Token consumption over time</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {['week', 'month', 'year'].map((p) => (
              <button
                key={p}
                onClick={() => setSelectedPeriod(p as any)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  selectedPeriod === p
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-muted'
                }`}
              >
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </button>
            ))}
            <button className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg">
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 p-4">
        <div className="p-4 rounded-xl bg-gradient-to-br from-indigo-50 dark:from-indigo-950/50 to-violet-50 dark:to-violet-950/50 border border-indigo-100 dark:border-indigo-900/50">
          <p className="text-sm text-muted-foreground mb-1">Total Usage</p>
          <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
            {totalTokens.toLocaleString()}
          </p>
          <p className="text-xs text-muted-foreground">tokens this {selectedPeriod}</p>
        </div>
        <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-50 dark:from-emerald-950/50 to-teal-50 dark:to-teal-950/50 border border-emerald-100 dark:border-emerald-900/50">
          <p className="text-sm text-muted-foreground mb-1">Daily Average</p>
          <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
            {avgDaily.toLocaleString()}
          </p>
          <p className="text-xs text-muted-foreground">tokens per day</p>
        </div>
        <div className="p-4 rounded-xl bg-gradient-to-br from-amber-50 dark:from-amber-950/50 to-orange-50 dark:to-orange-950/50 border border-amber-100 dark:border-amber-900/50">
          <p className="text-sm text-muted-foreground mb-1">Peak Day</p>
          <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
            {maxDay.toLocaleString()}
          </p>
          <p className="text-xs text-muted-foreground">highest usage</p>
        </div>
        <div
          className={`p-4 rounded-xl border ${
            trend >= 0
              ? 'bg-gradient-to-br from-green-50 dark:from-green-950/50 to-emerald-50 dark:to-emerald-950/50 border-green-100 dark:border-green-900/50'
              : 'bg-gradient-to-br from-red-50 dark:from-red-950/50 to-rose-50 dark:to-rose-950/50 border-red-100 dark:border-red-900/50'
          }`}
        >
          <p className="text-sm text-muted-foreground mb-1">Trend</p>
          <div className="flex items-center gap-2">
            {trend >= 0 ? (
              <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-600 dark:text-red-400" />
            )}
            <p
              className={`text-2xl font-bold ${
                trend >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              }`}
            >
              {trend >= 0 ? '+' : ''}
              {trend.toFixed(1)}%
            </p>
          </div>
          <p className="text-xs text-muted-foreground">vs start of period</p>
        </div>
      </div>

      <div className="px-4 pb-4">
        <div className="h-48 bg-muted/50 rounded-xl p-4 flex items-end gap-1">
          {data.slice(-14).map((d, i) => {
            const height = maxDay > 0 ? (d.total / maxDay) * 100 : 0;
            return (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div
                  className="w-full flex flex-col-reverse gap-px rounded-sm overflow-hidden"
                  style={{ height: `${Math.max(height, 2)}%` }}
                >
                  <div
                    className="bg-blue-400 transition-all"
                    style={{ height: `${d.total > 0 ? (d.text_llm / d.total) * 100 : 0}%` }}
                  />
                  <div
                    className="bg-pink-400 transition-all"
                    style={{ height: `${d.total > 0 ? (d.image_generation / d.total) * 100 : 0}%` }}
                  />
                  <div
                    className="bg-red-400 transition-all"
                    style={{ height: `${d.total > 0 ? (d.video_generation / d.total) * 100 : 0}%` }}
                  />
                  <div
                    className="bg-violet-400 transition-all"
                    style={{ height: `${d.total > 0 ? (d.agent_orchestration / d.total) * 100 : 0}%` }}
                  />
                </div>
                <span className="text-[10px] text-muted-foreground">{d.date.split('-')[2]}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="p-4 border-t border-border">
        <h4 className="text-sm font-medium text-foreground mb-3">Breakdown by Service</h4>
        <div className="grid grid-cols-4 gap-3">
          {Object.entries(serviceBreakdown).map(([service, tokens]) => {
            const config = SERVICE_COLORS[service as keyof typeof SERVICE_COLORS];
            const Icon = config.icon;
            const percentage = totalTokens > 0 ? ((tokens / totalTokens) * 100).toFixed(1) : '0';
            return (
              <div key={service} className={`p-3 rounded-xl ${config.light} border border-border`}>
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-8 h-8 rounded-lg ${config.bg} flex items-center justify-center`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-xs font-medium text-muted-foreground capitalize">
                    {service.replace('_', ' ')}
                  </span>
                </div>
                <p className={`text-lg font-bold ${config.text}`}>{tokens.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">{percentage}% of total</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default UsageAnalytics;
