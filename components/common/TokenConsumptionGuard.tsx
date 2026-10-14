import React, { useState } from 'react';
import { Zap, AlertCircle } from 'lucide-react';
import useTokenConsumption, { ServiceType, SERVICE_TOKEN_COSTS } from '../../hooks/useTokenConsumption';
import { useTokens } from '../../hooks/useTokens';
import { cn } from '../../utils/cn';

interface TokenConsumptionGuardProps {
  serviceType: ServiceType;
  onExecute: () => Promise<void>;
  children: React.ReactNode;
  className?: string;
  disabled?: boolean;
  showCost?: boolean;
}

export const TokenConsumptionGuard: React.FC<TokenConsumptionGuardProps> = ({
  serviceType,
  onExecute,
  children,
  className,
  disabled = false,
  showCost = true,
}) => {
  const [executing, setExecuting] = useState(false);
  const { checkAccess } = useTokenConsumption();
  const { balance } = useTokens();
  const cost = SERVICE_TOKEN_COSTS[serviceType];
  const hasEnough = balance.balance >= cost;

  const handleClick = async () => {
    if (executing || disabled) return;
    setExecuting(true);
    await onExecute();
    setExecuting(false);
  };

  const costElement = showCost && (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] font-medium rounded bg-muted text-muted-foreground ml-2">
      <Zap className="w-2.5 h-2.5" />
      {cost}
    </span>
  );

  if (!hasEnough) {
    return (
      <div className="relative group">
        <button
          disabled
          className={cn('opacity-50 cursor-not-allowed', className)}
        >
          {children}
          {costElement}
        </button>
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50">
          <div className="flex items-center gap-2 px-3 py-2 bg-amber-900 text-amber-100 text-xs rounded-lg shadow-lg whitespace-nowrap">
            <AlertCircle className="w-3 h-3" />
            Need {cost} tokens (have {balance.balance})
          </div>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={handleClick}
      disabled={disabled || executing}
      className={cn(executing && 'opacity-70 cursor-wait', className)}
    >
      {children}
      {costElement}
    </button>
  );
};

export default TokenConsumptionGuard;
