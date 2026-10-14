import React, { useState } from 'react';
import { Coins, Check, Sparkles, Zap, Star, X, ExternalLink } from 'lucide-react';
import { createCheckoutSession } from '../../services/stripeService';
import { useDialogEscape } from '../common/useDialogEscape';

interface TokenPackage {
  id: string;
  name: string;
  tokens: number;
  price: number;
  bonusTokens: number;
  popular: boolean;
  features: string[];
}

interface TokenPurchaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPurchase: (packageId: string) => void;
  currentTier: string;
}

const TOKEN_PACKAGES: TokenPackage[] = [
  {
    id: 'price_starter_5',
    name: 'Starter',
    tokens: 5000,
    price: 5,
    bonusTokens: 0,
    popular: false,
    features: ['5,000 tokens', 'Valid for 30 days', 'All AI features'],
  },
  {
    id: 'price_growth_20',
    name: 'Growth',
    tokens: 25000,
    price: 20,
    bonusTokens: 2500,
    popular: true,
    features: ['25,000 tokens', '+2,500 bonus (10%)', 'Valid for 60 days', 'Priority processing'],
  },
  {
    id: 'price_pro_70',
    name: 'Professional',
    tokens: 100000,
    price: 70,
    bonusTokens: 15000,
    popular: false,
    features: ['100,000 tokens', '+15,000 bonus (15%)', 'Valid for 90 days', 'Priority processing', 'API access'],
  },
];

export const TokenPurchaseModal: React.FC<TokenPurchaseModalProps> = ({
  isOpen,
  onClose,
  onPurchase,
  currentTier,
}) => {
  const [selectedPackage, setSelectedPackage] = useState<string>('price_growth_20');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useDialogEscape(isOpen, onClose);

  if (!isOpen) return null;

  const handlePurchase = async () => {
    const pkg = TOKEN_PACKAGES.find((p) => p.id === selectedPackage);
    if (!pkg) return;

    setIsProcessing(true);
    setError(null);

    try {
      const { url } = await createCheckoutSession(selectedPackage);
      onPurchase(selectedPackage);
      window.location.href = url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment service unavailable');
      setIsProcessing(false);
    }
  };

  const selected = TOKEN_PACKAGES.find((p) => p.id === selectedPackage);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div role="dialog" aria-modal="true" aria-labelledby="purchase-modal-title" className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-auto">
        <div className="p-6 border-b border-border bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
                <Coins className="w-7 h-7 text-white" />
              </div>
              <div>
                <h2 id="purchase-modal-title" className="text-2xl font-bold text-foreground">Purchase Tokens</h2>
                <p className="text-muted-foreground">Choose a package that fits your needs</p>
              </div>
            </div>
            <button
              onClick={onClose}
              aria-label="Close purchase dialog"
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {TOKEN_PACKAGES.map((pkg) => (
              <div
                key={pkg.id}
                onClick={() => setSelectedPackage(pkg.id)}
                className={`relative p-5 rounded-2xl border-2 cursor-pointer transition-all duration-200 ${
                  selectedPackage === pkg.id
                    ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10'
                    : 'border-border hover:border-primary/50 hover:shadow-md'
                }`}
              >
                {pkg.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-amber-400 to-yellow-500 text-amber-900 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                    <Star className="w-3 h-3" /> MOST POPULAR
                  </div>
                )}

                {selectedPackage === pkg.id && (
                  <div className="absolute top-3 right-3 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                )}

                <div
                  className={`w-12 h-12 rounded-xl mb-4 flex items-center justify-center ${
                    pkg.id.includes('pro')
                      ? 'bg-gradient-to-br from-violet-500 to-purple-600'
                      : pkg.id.includes('growth')
                        ? 'bg-gradient-to-br from-primary to-accent'
                        : 'bg-gradient-to-br from-slate-400 to-slate-500'
                  }`}
                >
                  {pkg.id.includes('pro') ? (
                    <Sparkles className="w-6 h-6 text-white" />
                  ) : (
                    <Zap className="w-6 h-6 text-white" />
                  )}
                </div>

                <h3 className="font-bold text-foreground text-lg mb-1">{pkg.name}</h3>

                <div className="flex items-baseline gap-1 mb-2">
                  <span className="text-3xl font-bold text-primary">
                    {(pkg.tokens / 1000).toFixed(0)}K
                  </span>
                  <span className="text-muted-foreground">tokens</span>
                </div>

                {pkg.bonusTokens > 0 && (
                  <div className="inline-flex items-center gap-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-medium px-2 py-1 rounded-full mb-3">
                    <Sparkles className="w-3 h-3" />
                    +{(pkg.bonusTokens / 1000).toFixed(1)}K bonus
                  </div>
                )}

                <div className="flex items-baseline gap-1 mb-4">
                  <span className="text-2xl font-bold text-foreground">${pkg.price}</span>
                  <span className="text-muted-foreground text-sm">USD</span>
                </div>

                <ul className="space-y-2">
                  {pkg.features.map((feature, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Check className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 border-t border-border bg-muted/30">
          <div className="flex items-center justify-between">
            <div>
              {selected && (
                <div className="flex items-center gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Selected Package</p>
                    <p className="text-lg font-bold text-foreground">{selected.name}</p>
                  </div>
                  <div className="h-10 w-px bg-border" />
                  <div>
                    <p className="text-sm text-muted-foreground">Total Tokens</p>
                    <p className="text-lg font-bold text-primary">
                      {(selected.tokens + selected.bonusTokens).toLocaleString()}
                    </p>
                  </div>
                  <div className="h-10 w-px bg-border" />
                  <div>
                    <p className="text-sm text-muted-foreground">Price</p>
                    <p className="text-lg font-bold text-foreground">${selected.price}</p>
                  </div>
                </div>
              )}
            </div>
            <div className="flex flex-col gap-3">
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                  {error}
                </div>
              )}
              <div className="flex gap-3 justify-end">
                <button
                  onClick={onClose}
                  className="px-6 py-3 border border-border text-foreground rounded-xl font-medium hover:bg-card transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handlePurchase}
                  disabled={isProcessing}
                  className="px-8 py-3 bg-gradient-to-r from-primary to-accent text-white rounded-xl font-medium hover:shadow-lg disabled:opacity-50 transition-all flex items-center gap-2"
                >
                  {isProcessing ? (
                    <>Redirecting to payment...</>
                  ) : (
                    <>
                      <ExternalLink className="w-4 h-4" />
                      Pay ${selected?.price}
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TokenPurchaseModal;
