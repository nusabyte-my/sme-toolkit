import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import type {
  Goal,
  GrowthPlan,
  CostingAnalysis,
  BusinessSuggestions,
  AnalyticsDashboard,
  AllScores,
  OrchestrationJob,
  StrategyAnalysisResponse,
} from '../types';

interface StrategyAdvisorState {
  // Goals
  goals: Goal[];
  goalsLoading: boolean;
  goalsError: string | null;

  // Growth Plans
  growthPlans: GrowthPlan[];
  growthPlansLoading: boolean;
  growthPlansError: string | null;

  // Costing
  costingAnalysis: CostingAnalysis | null;
  costingLoading: boolean;
  costingError: string | null;

  // Suggestions
  suggestions: BusinessSuggestions | null;
  suggestionsLoading: boolean;
  suggestionsError: string | null;

  // Analytics
  analytics: AnalyticsDashboard | null;
  analyticsLoading: boolean;
  analyticsError: string | null;

  // Scores
  scores: AllScores | null;
  scoresLoading: boolean;
  scoresError: string | null;

  // Orchestration
  orchestrationJob: OrchestrationJob | null;
  orchestrationLoading: boolean;
  orchestrationError: string | null;

  // Comprehensive Analysis
  comprehensiveAnalysis: StrategyAnalysisResponse | null;
  comprehensiveLoading: boolean;
  comprehensiveError: string | null;
}

interface StrategyAdvisorContextType extends StrategyAdvisorState {
  // Goals Actions
  setGoals: (goals: Goal[]) => void;
  setGoalsLoading: (loading: boolean) => void;
  setGoalsError: (error: string | null) => void;

  // Growth Plans Actions
  setGrowthPlans: (plans: GrowthPlan[]) => void;
  setGrowthPlansLoading: (loading: boolean) => void;
  setGrowthPlansError: (error: string | null) => void;

  // Costing Actions
  setCostingAnalysis: (analysis: CostingAnalysis | null) => void;
  setCostingLoading: (loading: boolean) => void;
  setCostingError: (error: string | null) => void;

  // Suggestions Actions
  setSuggestions: (suggestions: BusinessSuggestions | null) => void;
  setSuggestionsLoading: (loading: boolean) => void;
  setSuggestionsError: (error: string | null) => void;

  // Analytics Actions
  setAnalytics: (analytics: AnalyticsDashboard | null) => void;
  setAnalyticsLoading: (loading: boolean) => void;
  setAnalyticsError: (error: string | null) => void;

  // Scores Actions
  setScores: (scores: AllScores | null) => void;
  setScoresLoading: (loading: boolean) => void;
  setScoresError: (error: string | null) => void;

  // Orchestration Actions
  setOrchestrationJob: (job: OrchestrationJob | null) => void;
  setOrchestrationLoading: (loading: boolean) => void;
  setOrchestrationError: (error: string | null) => void;

  // Comprehensive Analysis Actions
  setComprehensiveAnalysis: (analysis: StrategyAnalysisResponse | null) => void;
  setComprehensiveLoading: (loading: boolean) => void;
  setComprehensiveError: (error: string | null) => void;

  // Reset Actions
  resetGoals: () => void;
  resetGrowthPlans: () => void;
  resetCosting: () => void;
  resetSuggestions: () => void;
  resetAnalytics: () => void;
  resetScores: () => void;
  resetOrchestration: () => void;
  resetComprehensive: () => void;
  resetAll: () => void;
}

const StrategyAdvisorContext = createContext<StrategyAdvisorContextType | undefined>(undefined);

const initialState: StrategyAdvisorState = {
  goals: [],
  goalsLoading: false,
  goalsError: null,

  growthPlans: [],
  growthPlansLoading: false,
  growthPlansError: null,

  costingAnalysis: null,
  costingLoading: false,
  costingError: null,

  suggestions: null,
  suggestionsLoading: false,
  suggestionsError: null,

  analytics: null,
  analyticsLoading: false,
  analyticsError: null,

  scores: null,
  scoresLoading: false,
  scoresError: null,

  orchestrationJob: null,
  orchestrationLoading: false,
  orchestrationError: null,

  comprehensiveAnalysis: null,
  comprehensiveLoading: false,
  comprehensiveError: null,
};

export const StrategyAdvisorProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<StrategyAdvisorState>(initialState);

  // Goals Actions
  const setGoals = useCallback((goals: Goal[]) => {
    setState((prev) => ({ ...prev, goals }));
  }, []);

  const setGoalsLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, goalsLoading: loading }));
  }, []);

  const setGoalsError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, goalsError: error }));
  }, []);

  // Growth Plans Actions
  const setGrowthPlans = useCallback((plans: GrowthPlan[]) => {
    setState((prev) => ({ ...prev, growthPlans: plans }));
  }, []);

  const setGrowthPlansLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, growthPlansLoading: loading }));
  }, []);

  const setGrowthPlansError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, growthPlansError: error }));
  }, []);

  // Costing Actions
  const setCostingAnalysis = useCallback((analysis: CostingAnalysis | null) => {
    setState((prev) => ({ ...prev, costingAnalysis: analysis }));
  }, []);

  const setCostingLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, costingLoading: loading }));
  }, []);

  const setCostingError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, costingError: error }));
  }, []);

  // Suggestions Actions
  const setSuggestions = useCallback((suggestions: BusinessSuggestions | null) => {
    setState((prev) => ({ ...prev, suggestions }));
  }, []);

  const setSuggestionsLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, suggestionsLoading: loading }));
  }, []);

  const setSuggestionsError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, suggestionsError: error }));
  }, []);

  // Analytics Actions
  const setAnalytics = useCallback((analytics: AnalyticsDashboard | null) => {
    setState((prev) => ({ ...prev, analytics }));
  }, []);

  const setAnalyticsLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, analyticsLoading: loading }));
  }, []);

  const setAnalyticsError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, analyticsError: error }));
  }, []);

  // Scores Actions
  const setScores = useCallback((scores: AllScores | null) => {
    setState((prev) => ({ ...prev, scores }));
  }, []);

  const setScoresLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, scoresLoading: loading }));
  }, []);

  const setScoresError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, scoresError: error }));
  }, []);

  // Orchestration Actions
  const setOrchestrationJob = useCallback((job: OrchestrationJob | null) => {
    setState((prev) => ({ ...prev, orchestrationJob: job }));
  }, []);

  const setOrchestrationLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, orchestrationLoading: loading }));
  }, []);

  const setOrchestrationError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, orchestrationError: error }));
  }, []);

  // Comprehensive Analysis Actions
  const setComprehensiveAnalysis = useCallback((analysis: StrategyAnalysisResponse | null) => {
    setState((prev) => ({ ...prev, comprehensiveAnalysis: analysis }));
  }, []);

  const setComprehensiveLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, comprehensiveLoading: loading }));
  }, []);

  const setComprehensiveError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, comprehensiveError: error }));
  }, []);

  // Reset Actions
  const resetGoals = useCallback(() => {
    setState((prev) => ({
      ...prev,
      goals: [],
      goalsLoading: false,
      goalsError: null,
    }));
  }, []);

  const resetGrowthPlans = useCallback(() => {
    setState((prev) => ({
      ...prev,
      growthPlans: [],
      growthPlansLoading: false,
      growthPlansError: null,
    }));
  }, []);

  const resetCosting = useCallback(() => {
    setState((prev) => ({
      ...prev,
      costingAnalysis: null,
      costingLoading: false,
      costingError: null,
    }));
  }, []);

  const resetSuggestions = useCallback(() => {
    setState((prev) => ({
      ...prev,
      suggestions: null,
      suggestionsLoading: false,
      suggestionsError: null,
    }));
  }, []);

  const resetAnalytics = useCallback(() => {
    setState((prev) => ({
      ...prev,
      analytics: null,
      analyticsLoading: false,
      analyticsError: null,
    }));
  }, []);

  const resetScores = useCallback(() => {
    setState((prev) => ({
      ...prev,
      scores: null,
      scoresLoading: false,
      scoresError: null,
    }));
  }, []);

  const resetOrchestration = useCallback(() => {
    setState((prev) => ({
      ...prev,
      orchestrationJob: null,
      orchestrationLoading: false,
      orchestrationError: null,
    }));
  }, []);

  const resetComprehensive = useCallback(() => {
    setState((prev) => ({
      ...prev,
      comprehensiveAnalysis: null,
      comprehensiveLoading: false,
      comprehensiveError: null,
    }));
  }, []);

  const resetAll = useCallback(() => {
    setState(initialState);
  }, []);

  const contextValue: StrategyAdvisorContextType = {
    ...state,
    setGoals,
    setGoalsLoading,
    setGoalsError,
    setGrowthPlans,
    setGrowthPlansLoading,
    setGrowthPlansError,
    setCostingAnalysis,
    setCostingLoading,
    setCostingError,
    setSuggestions,
    setSuggestionsLoading,
    setSuggestionsError,
    setAnalytics,
    setAnalyticsLoading,
    setAnalyticsError,
    setScores,
    setScoresLoading,
    setScoresError,
    setOrchestrationJob,
    setOrchestrationLoading,
    setOrchestrationError,
    setComprehensiveAnalysis,
    setComprehensiveLoading,
    setComprehensiveError,
    resetGoals,
    resetGrowthPlans,
    resetCosting,
    resetSuggestions,
    resetAnalytics,
    resetScores,
    resetOrchestration,
    resetComprehensive,
    resetAll,
  };

  return (
    <StrategyAdvisorContext.Provider value={contextValue}>
      {children}
    </StrategyAdvisorContext.Provider>
  );
};

export const useStrategyAdvisor = (): StrategyAdvisorContextType => {
  const context = useContext(StrategyAdvisorContext);
  if (context === undefined) {
    throw new Error('useStrategyAdvisor must be used within a StrategyAdvisorProvider');
  }
  return context;
};
