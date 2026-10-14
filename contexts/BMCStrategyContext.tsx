import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import {
  BusinessCanvasData,
  GrowthScore,
  FullAnalysisResult,
  ChatSession
} from '../types';

import { authenticatedFetch } from '../services/apiClient';

interface BMCStrategyContextType {
  // Data
  bmcData: BusinessCanvasData | null;
  growthScore: GrowthScore | null;
  analysisResult: FullAnalysisResult | null;
  chatSession: ChatSession | null;

  // Loading states
  isAnalyzing: boolean;
  isLoadingScore: boolean;

  // Actions
  setBMCData: (data: BusinessCanvasData) => void;
  setChatSession: (session: ChatSession | null) => void;
  runFullAnalysis: (bmcData: BusinessCanvasData) => Promise<FullAnalysisResult>;
  refreshGrowthScore: () => Promise<void>;
  clearData: () => void;
}

const BMCStrategyContext = createContext<BMCStrategyContextType | null>(null);

interface BMCStrategyProviderProps {
  children: ReactNode;
}

export const BMCStrategyProvider: React.FC<BMCStrategyProviderProps> = ({ children }) => {
  const [bmcData, setBMCDataState] = useState<BusinessCanvasData | null>(null);
  const [growthScore, setGrowthScore] = useState<GrowthScore | null>(null);
  const [analysisResult, setAnalysisResult] = useState<FullAnalysisResult | null>(null);
  const [chatSession, setChatSession] = useState<ChatSession | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingScore, setIsLoadingScore] = useState(false);


  const setBMCData = useCallback((data: BusinessCanvasData) => {
    setBMCDataState(data);
  }, []);

  const runFullAnalysis = useCallback(async (canvas: BusinessCanvasData): Promise<FullAnalysisResult> => {
    setIsAnalyzing(true);
    try {
      const response = await authenticatedFetch('/api/v1/bmc/analyze', 'POST', {
        bmc_data: canvas,
        business_context: chatSession?.extracted_context,
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const result: FullAnalysisResult = await response.json();

      setAnalysisResult(result);
      if (result.growth_score) {
        setGrowthScore(result.growth_score);
      }

      return result;
    } catch (error) {
      console.error('Full analysis failed:', error);
      const errorResult: FullAnalysisResult = {
        success: false,
        error: error instanceof Error ? error.message : 'Analysis failed'
      };
      return errorResult;
    } finally {
      setIsAnalyzing(false);
    }
  }, [chatSession]);

  const refreshGrowthScore = useCallback(async () => {
    if (!bmcData) return;

    setIsLoadingScore(true);
    try {
      const result = await runFullAnalysis(bmcData);
      if (result.growth_score) {
        setGrowthScore(result.growth_score);
      }
    } finally {
      setIsLoadingScore(false);
    }
  }, [bmcData, runFullAnalysis]);

  const clearData = useCallback(() => {
    setBMCDataState(null);
    setGrowthScore(null);
    setAnalysisResult(null);
    setChatSession(null);
  }, []);

  const value: BMCStrategyContextType = {
    bmcData,
    growthScore,
    analysisResult,
    chatSession,
    isAnalyzing,
    isLoadingScore,
    setBMCData,
    setChatSession,
    runFullAnalysis,
    refreshGrowthScore,
    clearData
  };

  return (
    <BMCStrategyContext.Provider value={value}>
      {children}
    </BMCStrategyContext.Provider>
  );
};

export const useBMCStrategy = (): BMCStrategyContextType => {
  const context = useContext(BMCStrategyContext);
  if (!context) {
    throw new Error('useBMCStrategy must be used within a BMCStrategyProvider');
  }
  return context;
};

export default BMCStrategyContext;
