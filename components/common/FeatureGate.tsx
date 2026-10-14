/**
 * FeatureGate Component
 * Displays feature gate with upgrade prompt
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React from 'react';
import { Lock, Sparkles, ArrowUpRight } from 'lucide-react';
import { useTier, TierFeatures } from '../../contexts/TierContext';

interface FeatureGateProps {
  feature: keyof TierFeatures;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showUpgradePrompt?: boolean;
}

/**
 * Feature Gate Component
 *
 * Conditionally renders children based on user's tier access.
 * Shows upgrade prompt when user doesn't have access.
 */
export const FeatureGate: React.FC<FeatureGateProps> = ({
  feature,
  children,
  fallback,
  showUpgradePrompt = true
}) => {
  const { checkFeature, tier, allTiers } = useTier();
  const hasAccess = checkFeature(feature);

  if (hasAccess) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  if (!showUpgradePrompt) {
    return null;
  }

  // Find the lowest tier that has this feature
  const upgradeTier = allTiers.find(t =>
    t.features.includes(feature) && t.id !== tier
  );

  return (
    <div className="relative">
      {/* Blurred content preview */}
      <div className="filter blur-sm opacity-50 pointer-events-none select-none">
        {children}
      </div>

      {/* Upgrade overlay */}
      <div className="absolute inset-0 flex items-center justify-center bg-[#001f3d]/10 backdrop-blur-[2px] rounded-lg">
        <div className="backdrop-blur-sm bg-white/95 rounded-xl shadow-lg border border-[#b6cbe1]/30 p-6 max-w-sm text-center">
          <div className="w-12 h-12 bg-[#1863d6]/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-6 h-6 text-[#1863d6]" />
          </div>
          <h3 className="text-lg font-semibold text-[#0f172a] mb-2">
            Feature Locked
          </h3>
          <p className="text-sm text-[#64748b] mb-4">
            {formatFeatureName(feature)} requires a{' '}
            <span className="font-medium text-[#1863d6]">
              {upgradeTier?.name || 'higher'} plan
            </span>
          </p>
          {upgradeTier && (
            <button className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white rounded-lg hover:shadow-md transition-all text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              Upgrade to {upgradeTier.name}
              <ArrowUpRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Simple feature check hook with inline upgrade prompt
 */
export const useFeatureCheck = (feature: keyof TierFeatures) => {
  const { checkFeature, tier, allTiers } = useTier();
  const hasAccess = checkFeature(feature);

  const upgradeTier = allTiers.find(t =>
    t.features.includes(feature) && t.id !== tier
  );

  return {
    hasAccess,
    currentTier: tier,
    upgradeToTier: upgradeTier?.id,
    upgradeToName: upgradeTier?.name,
    upgradePrice: upgradeTier?.price
  };
};

/**
 * Inline upgrade badge for features
 */
export const UpgradeBadge: React.FC<{ feature: keyof TierFeatures }> = ({ feature }) => {
  const { hasAccess, upgradeToName } = useFeatureCheck(feature);

  if (hasAccess) {
    return null;
  }

  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white text-xs font-medium rounded-full">
      <Sparkles className="w-3 h-3" />
      {upgradeToName || 'Pro'}
    </span>
  );
};

// Helper function to format feature names
function formatFeatureName(feature: string): string {
  const names: Record<string, string> = {
    bmc_basic: 'Business Model Canvas',
    bmc_analysis: 'BMC Analysis',
    lead_scoring: 'Lead Scoring',
    copywriting: 'AI Copywriting',
    strategy_advisor: 'Strategy Advisor',
    growth_score: 'Growth Score',
    visual_studio: 'Visual Studio',
    video_studio: 'Video Studio',
    analytics: 'Analytics Dashboard',
    api_access: 'API Access',
    priority_processing: 'Priority Processing',
    advanced_analytics: 'Advanced Analytics'
  };
  return names[feature] || feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

export default FeatureGate;
