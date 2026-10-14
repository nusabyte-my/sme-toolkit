import React, { useState } from 'react';
import {
  Coins, TrendingDown, Zap, Image, Video, Bot, RefreshCw, Plus, ChevronRight
} from 'lucide-react';
import { useTokens, SUBSCRIPTION_TIERS } from '../../hooks/useTokens';

interface UsageBreakdown {
  text_llm: number;
  image_generation: number;
  video_generation: number;
  agent_orchestration: number;
}

interface TokenBalanceWidgetProps {
  userId?: string;
  compact?: boolean;
  onPurchase?: () => void;
}

const computeUsageBreakdown = (usage: { serviceType: string; tokens: number }[]): UsageBreakdown => {
  const breakdown: UsageBreakdown = {
    text_llm: 0,
    image_generation: 0,
    video_generation: 0,
    agent_orchestration: 0,
  };
  usage.forEach((entry) => {
    const key = entry.serviceType as keyof UsageBreakdown;
    if (key in breakdown) {
      breakdown[key] += entry.tokens;
    }
  });
  return breakdown;
};

export const TokenBalanceWidget: React.FC<TokenBalanceWidgetProps> = ({
  userId,
  compact = false,
  onPurchase,
}) => {
  const { balance, usage, loading } = useTokens();
  const [showDetails, setShowDetails] = useState(false);

  const usageBreakdown = computeUsageBreakdown(usage);
  const totalUsed = Object.values(usageBreakdown).reduce((a, b) => a + b, 0);
  const quota = balance.dailyLimit * 30;
  const percentUsed = Math.min((totalUsed / Math.max(quota, 1)) * 100, 100);

  const getUsageColor = () => {
    if (percentUsed >= 90) return 'from-red-500 to-rose-500';
    if (percentUsed >= 70) return 'from-amber-500 to-orange-500';
    return 'from-emerald-500 to-teal-500';
  };

  if (compact) {
    return (
      <div className="flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-primary/5 to-accent/5 rounded-xl border border-primary/10">
        <div className="flex items-center gap-2">
          <Coins className="w-5 h-5 text-primary" />
          <span className="font-bold text-foreground">{balance.balance.toLocaleString()}</span>
          <span className="text-sm text-muted-foreground">tokens</span>
        </div>
        <div className="h-4 w-px bg-border" />
        <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full bg-gradient-to-r ${getUsageColor()} rounded-full transition-all`}
            style={{ width: `${Math.min(percentUsed, 100)}%` }}
          />
        </div>
        <span className="text-xs text-muted-foreground">{percentUsed.toFixed(0)}%</span>
        {onPurchase && (
          <button
            onClick={onPurchase}
            className="p-1.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="bg-card rounded-2xl border border-border shadow-sm overflow-hidden">
      <div className="p-4 border-b border-border bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
              <Coins className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Token Balance</p>
              <p className="text-2xl font-bold text-foreground">
                {loading ? '...' : balance.balance.toLocaleString()}
              </p>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1">
            <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium capitalize">
              {balance.tier}
            </span>
          </div>
        </div>
      </div>

      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-muted-foreground">Estimated Monthly Usage</span>
          <span className="text-sm font-medium text-foreground">
            {totalUsed.toLocaleString()} / {quota.toLocaleString()}
          </span>
        </div>
        <div className="h-3 bg-muted rounded-full overflow-hidden mb-4">
          <div
            className={`h-full bg-gradient-to-r ${getUsageColor()} rounded-full transition-all duration-500`}
            style={{ width: `${Math.min(percentUsed, 100)}%` }}
          />
        </div>

        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-between py-2 text-sm text-muted-foreground hover:text-primary transition-colors"
        >
          <span>Usage Breakdown</span>
          <ChevronRight className={`w-4 h-4 transition-transform ${showDetails ? 'rotate-90' : ''}`} />
        </button>

        {showDetails && (
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <Zap className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                </div>
                <span className="text-sm text-foreground">Text/LLM</span>
              </div>
              <span className="text-sm font-medium">{usageBreakdown.text_llm.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center">
                  <Image className="w-4 h-4 text-pink-600 dark:text-pink-400" />
                </div>
                <span className="text-sm text-foreground">Images</span>
              </div>
              <span className="text-sm font-medium">{usageBreakdown.image_generation.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                  <Video className="w-4 h-4 text-red-600 dark:text-red-400" />
                </div>
                <span className="text-sm text-foreground">Videos</span>
              </div>
              <span className="text-sm font-medium">{usageBreakdown.video_generation.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-violet-600 dark:text-violet-400" />
                </div>
                <span className="text-sm text-foreground">Agents</span>
              </div>
              <span className="text-sm font-medium">{usageBreakdown.agent_orchestration.toLocaleString()}</span>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-border bg-muted/30">
        <div className="flex gap-2">
          {onPurchase && (
            <button
              onClick={onPurchase}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-gradient-to-r from-primary to-accent text-white rounded-xl font-medium hover:shadow-lg transition-all"
            >
              <Plus className="w-4 h-4" />
              Buy Tokens
            </button>
          )}
          <button className="px-4 py-2.5 border border-border text-foreground rounded-xl font-medium hover:bg-card transition-colors">
            History
          </button>
        </div>
      </div>

      {percentUsed >= 80 && (
        <div
          className={`px-4 py-3 ${
            percentUsed >= 90
              ? 'bg-error/10 border-t border-error/20'
              : 'bg-warning/10 border-t border-warning/20'
          }`}
        >
          <div className="flex items-center gap-2">
            <TrendingDown
              className={`w-4 h-4 ${percentUsed >= 90 ? 'text-error' : 'text-warning'}`}
            />
            <span className={`text-sm ${percentUsed >= 90 ? 'text-error' : 'text-warning'}`}>
              {percentUsed >= 90
                ? 'Critical: Running low on tokens!'
                : 'Warning: Token usage above 80%'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default TokenBalanceWidget;
