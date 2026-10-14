import React from 'react';
import { Lock, Sparkles, ArrowUpRight } from 'lucide-react';
import { useTokens, SUBSCRIPTION_TIERS } from '../../hooks/useTokens';

interface TokenGateProps {
  feature: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showUpgradePrompt?: boolean;
  onUpgrade?: () => void;
}

const formatFeatureName = (feature: string): string => {
  const names: Record<string, string> = {
    dashboard: 'Dashboard',
    bmc: 'Business Model Canvas',
    leads: 'Lead CRM',
    copywriter: 'AI Copywriter',
    visual_studio: 'Visual Studio',
    ideation: 'Ideation',
    video_studio: 'Video Studio',
    strategy: 'Strategy Advisor',
    api_access: 'API Access',
    white_label: 'White Label',
    priority_support: 'Priority Support',
  };
  return names[feature] || feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const findUpgradeTier = (feature: string, currentTier: string): string | null => {
  const tierOrder = ['free', 'sme', 'business', 'enterprise'];
  const currentIdx = tierOrder.indexOf(currentTier.toLowerCase());

  for (let i = currentIdx + 1; i < tierOrder.length; i++) {
    const tier = tierOrder[i];
    const tierInfo = SUBSCRIPTION_TIERS[tier];
    if (tierInfo && tierInfo.features.includes(feature)) {
      return tier;
    }
  }
  return null;
};

const tierLabels: Record<string, string> = {
  free: 'Free',
  sme: 'SME',
  business: 'Business',
  enterprise: 'Enterprise',
};

export const TokenGate: React.FC<TokenGateProps> = ({
  feature,
  children,
  fallback,
  showUpgradePrompt = true,
  onUpgrade,
}) => {
  const { hasFeatureAccess, balance, fetchBalance } = useTokens();
  const hasAccess = hasFeatureAccess(feature);

  if (hasAccess) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  if (!showUpgradePrompt) {
    return null;
  }

  const upgradeTier = findUpgradeTier(feature, balance.tier);
  const upgradeName = upgradeTier ? tierLabels[upgradeTier] || upgradeTier : 'higher';

  return (
    <div className="relative">
      <div className="filter blur-sm opacity-50 pointer-events-none select-none">
        {children}
      </div>

      <div className="absolute inset-0 flex items-center justify-center bg-black/5 backdrop-blur-[2px] rounded-lg">
        <div className="backdrop-blur-sm bg-white/95 rounded-xl shadow-lg border border-slate-200 p-6 max-w-sm text-center">
          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-6 h-6 text-primary" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            Feature Locked
          </h3>
          <p className="text-sm text-slate-500 mb-4">
            {formatFeatureName(feature)} requires a{' '}
            <span className="font-medium text-primary">
              {upgradeName} plan
            </span>
          </p>
          <button
            onClick={() => {
              // No billing backend yet: tier upgrade is instant + local until Stripe checkout exists.
              if (onUpgrade) {
                onUpgrade();
              } else {
                // Fallback path used when host doesn't pass onUpgrade
                // eslint-disable-next-line no-console
                console.info(`Upgrade requested: ${upgradeTier}`);
              }
            }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary to-accent text-white rounded-lg hover:shadow-md focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary transition-all text-sm font-medium"
          >
            <Sparkles className="w-4 h-4" />
            Upgrade to {upgradeName}
            <ArrowUpRight className="w-4 h-4" />
          </button>
          <p className="text-xs text-slate-400 mt-3">
            Token balance: {balance.balance.toLocaleString()} ·
            <button
              onClick={() => fetchBalance()}
              className="underline hover:text-primary ml-1 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            >
              Refresh
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export const useTokenCheck = (feature: string) => {
  const { hasFeatureAccess, balance } = useTokens();
  const hasAccess = hasFeatureAccess(feature);
  const upgradeTier = findUpgradeTier(feature, balance.tier);

  return {
    hasAccess,
    currentTier: balance.tier,
    upgradeToTier: upgradeTier,
    upgradeToName: upgradeTier ? tierLabels[upgradeTier] || upgradeTier : null,
  };
};

export const UpgradeBadge: React.FC<{ feature: string }> = ({ feature }) => {
  const { hasAccess, upgradeToName } = useTokenCheck(feature);

  if (hasAccess) return null;

  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-primary to-accent text-white text-xs font-medium rounded-full">
      <Sparkles className="w-3 h-3" />
      {upgradeToName || 'Pro'}
    </span>
  );
};

export default TokenGate;
