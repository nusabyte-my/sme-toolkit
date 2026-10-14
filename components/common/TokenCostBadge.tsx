import React from 'react';
import { Coins } from 'lucide-react';

interface TokenCostBadgeProps {
  cost: number;
  balance: number;
}

const TokenCostBadge: React.FC<TokenCostBadgeProps> = ({ cost, balance }) => {
  const sufficient = balance >= cost;

  return (
    <div className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full ${sufficient ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}`}>
      <Coins className="w-3.5 h-3.5" />
      <span>{cost} tokens</span>
      {!sufficient && (
        <span className="text-[10px]">(insufficient)</span>
      )}
    </div>
  );
};

export default TokenCostBadge;
