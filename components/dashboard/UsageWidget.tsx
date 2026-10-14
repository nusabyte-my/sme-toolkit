/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Usage widget & tier meter */
import React from 'react';
import { MessageSquare, Image, Video, RefreshCw, Sparkles, ArrowUpRight } from 'lucide-react';
import { useTier } from '../../contexts/TierContext';

interface UsageBarProps {
  icon: React.ReactNode;
  label: string;
  used: number;
  limit: number;
  barColorClass: string;
  textColorClass: string;
}

const UsageBar: React.FC<UsageBarProps> = ({ icon, label, used, limit, barColorClass, textColorClass }) => {
  const percentage = limit > 0 ? Math.min((used / limit) * 100, 100) : 0;
  const isNearLimit = percentage >= 80;
  const isAtLimit = percentage >= 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-lg ${textColorClass} bg-muted/60 flex items-center justify-center`}>
            {icon}
          </div>
          <span className="text-sm font-medium text-foreground">{label}</span>
        </div>
        <span className={`text-sm font-mono font-semibold ${isAtLimit ? 'text-destructive' : isNearLimit ? 'text-warning' : 'text-muted-foreground'}`}>
          {limit === 0 ? 'Not available' : `${used.toLocaleString()} / ${limit.toLocaleString()}`}
        </span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            isAtLimit ? 'bg-destructive' : isNearLimit ? 'bg-warning' : barColorClass
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export const UsageWidget: React.FC = () => {
  const { tier, tierName, usage, limits, loading, refreshUsage, allTiers } = useTier();

  // Find next tier for upgrade
  const tierOrder = ['free', 'sme', 'business', 'enterprise'];
  const currentIndex = tierOrder.indexOf(tier);
  const nextTier = currentIndex < tierOrder.length - 1
    ? allTiers.find(t => t.id === tierOrder[currentIndex + 1])
    : null;

  return (
    <div className="backdrop-blur-sm bg-card/90 rounded-2xl border border-border p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold font-display text-foreground">Daily Usage</h3>
          <p className="text-sm text-muted-foreground">
            Current plan: <span className="font-semibold text-primary capitalize">{tierName || tier}</span>
          </p>
        </div>
        <button
          onClick={() => refreshUsage()}
          disabled={loading}
          aria-label="Refresh usage limits"
          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          title="Refresh usage"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Usage Bars - Rotate rainbow accents */}
      <div className="space-y-5">
        <UsageBar
          icon={<MessageSquare className="w-4 h-4 text-rainbow-cyan" />}
          label="AI Requests"
          used={usage?.llm.used ?? 0}
          limit={usage?.llm.limit ?? limits.daily_llm_requests}
          barColorClass="bg-rainbow-cyan"
          textColorClass="text-rainbow-cyan"
        />
        <UsageBar
          icon={<Image className="w-4 h-4 text-primary" />}
          label="Image Generation"
          used={usage?.image.used ?? 0}
          limit={usage?.image.limit ?? limits.daily_image_requests}
          barColorClass="bg-primary"
          textColorClass="text-primary"
        />
        <UsageBar
          icon={<Video className="w-4 h-4 text-rainbow-pink" />}
          label="Video Generation"
          used={usage?.video.used ?? 0}
          limit={usage?.video.limit ?? limits.daily_video_requests}
          barColorClass="bg-rainbow-pink"
          textColorClass="text-rainbow-pink"
        />
      </div>

      {/* Upgrade CTA */}
      {nextTier && (
        <div className="mt-6 pt-4 border-t border-border">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <p className="text-sm text-foreground">
                Need more? Upgrade to{' '}
                <span className="font-semibold text-primary">{nextTier.name}</span>
              </p>
              <p className="text-xs text-muted-foreground font-mono mt-0.5">
                {nextTier.daily_llm_requests} requests, {nextTier.daily_image_requests} images,{' '}
                {nextTier.daily_video_requests} videos/day
              </p>
            </div>
            <button className="inline-flex items-center justify-center gap-1.5 px-4 py-2 bg-gradient-cta text-white text-sm font-semibold rounded-xl hover:opacity-95 transition-all shadow-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring active:scale-95 flex-shrink-0">
              <Sparkles className="w-4 h-4" />
              ${nextTier.price}/mo
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Reset time */}
      <div className="mt-4 text-center">
        <p className="text-xs text-muted-foreground font-mono">
          Usage resets daily at midnight UTC
        </p>
      </div>
    </div>
  );
};

/**
 * Compact usage indicator for headers/navbars
 */
export const UsageIndicator: React.FC = () => {
  const { usage, limits, tier } = useTier();

  const llmPercentage = limits.daily_llm_requests > 0
    ? ((usage?.llm.used ?? 0) / limits.daily_llm_requests) * 100
    : 0;

  const isLow = llmPercentage >= 80;

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1.5 px-2 py-1 bg-muted rounded-lg border border-border">
        <MessageSquare className={`w-3.5 h-3.5 ${isLow ? 'text-warning' : 'text-muted-foreground'}`} />
        <span className={`text-xs font-mono font-medium ${isLow ? 'text-warning font-bold' : 'text-foreground'}`}>
          {usage?.llm.remaining ?? limits.daily_llm_requests} left
        </span>
      </div>
      <span className="text-xs text-muted-foreground capitalize font-medium">{tier}</span>
    </div>
  );
};

export default UsageWidget;
