import { useCallback, useState } from 'react';
import { useTokens } from './useTokens';
import { estimateCost } from '../utils/tokenCosts';
import type { ImageCostParams, VideoCostParams } from '../utils/tokenCosts';

interface UseTokenActionResult {
  execute: <T>(
    serviceType: string,
    action: () => Promise<T>,
    costParams?: ImageCostParams | VideoCostParams
  ) => Promise<{ success: boolean; data?: T; error?: string }>;
  isChecking: boolean;
  lastError: string | null;
}

export function useTokenAction(): UseTokenActionResult {
  const { consumeTokens, hasEnoughTokens, balance } = useTokens();
  const [isChecking, setIsChecking] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);

  const execute = useCallback(async <T>(
    serviceType: string,
    action: () => Promise<T>,
    costParams?: ImageCostParams | VideoCostParams
  ): Promise<{ success: boolean; data?: T; error?: string }> => {
    setIsChecking(true);
    setLastError(null);

    const cost = estimateCost(serviceType, costParams);

    if (!hasEnoughTokens(serviceType as any)) {
      const error = `Not enough tokens. Need ${cost}, have ${balance.balance}`;
      setLastError(error);
      setIsChecking(false);
      return { success: false, error };
    }

    const consumption = await consumeTokens(serviceType as any, costParams);
    if (!consumption.success) {
      setLastError(consumption.error ?? 'Token consumption failed');
      setIsChecking(false);
      return { success: false, error: consumption.error };
    }

    try {
      const data = await action();
      setIsChecking(false);
      return { success: true, data };
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Action failed';
      setLastError(error);
      setIsChecking(false);
      return { success: false, error };
    }
  }, [consumeTokens, hasEnoughTokens, balance.balance]);

  return { execute, isChecking, lastError };
}
