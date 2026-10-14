import type {
  Goal,
  GoalAnalysis,
  GrowthPlan,
  CostingAnalysis,
  BusinessSuggestions,
  AnalyticsDashboard,
  AllScores,
  ScoreHistory,
  OrchestrationJob,
  StrategyAnalysisRequest,
  StrategyAnalysisResponse,
} from '../types';

import { apiCall } from './apiClient';

// ==================== Goal Advisor API ====================

export const createGoals = async (
  businessProfileId: string,
  businessContext: string,
  existingGoals?: Goal[]
): Promise<{ goals: Goal[]; goal_analysis: GoalAnalysis }> => {
  return apiCall('/api/v1/strategy-advisor/goals', 'POST', {
    business_profile_id: businessProfileId,
    business_context: businessContext,
    existing_goals: existingGoals,
  });
};

export const getGoals = async (businessProfileId: string): Promise<Goal[]> => {
  const response = await apiCall<{ goals: Goal[] }>(
    `/api/v1/strategy-advisor/goals?business_profile_id=${businessProfileId}`,
    'GET'
  );
  return response.goals;
};

export const updateGoal = async (
  goalId: string,
  updates: Partial<Goal>
): Promise<Goal> => {
  return apiCall(`/api/v1/strategy-advisor/goals/${goalId}`, 'PUT', updates);
};

export const deleteGoal = async (goalId: string): Promise<void> => {
  await apiCall(`/api/v1/strategy-advisor/goals/${goalId}`, 'DELETE');
};

// ==================== Growth Plan Advisor API ====================

export const createGrowthPlan = async (
  businessProfileId: string,
  businessContext: string,
  timeframe: string = '6 months'
): Promise<GrowthPlan> => {
  const response = await apiCall<{ growth_plan: GrowthPlan }>(
    '/api/v1/strategy-advisor/growth-plans',
    'POST',
    {
      business_profile_id: businessProfileId,
      business_context: businessContext,
      timeframe,
    }
  );
  return response.growth_plan;
};

export const getGrowthPlans = async (businessProfileId: string): Promise<GrowthPlan[]> => {
  const response = await apiCall<{ growth_plans: GrowthPlan[] }>(
    `/api/v1/strategy-advisor/growth-plans?business_profile_id=${businessProfileId}`,
    'GET'
  );
  return response.growth_plans;
};

export const getGrowthPlan = async (planId: string): Promise<GrowthPlan> => {
  const response = await apiCall<{ growth_plan: GrowthPlan }>(
    `/api/v1/strategy-advisor/growth-plans/${planId}`,
    'GET'
  );
  return response.growth_plan;
};

// ==================== Costing Advisor API ====================

export const analyzeCosting = async (
  businessProfileId: string,
  costData: any,
  marketData?: any
): Promise<CostingAnalysis> => {
  const response = await apiCall<{ costing_analysis: CostingAnalysis }>(
    '/api/v1/strategy-advisor/costing/analyze',
    'POST',
    {
      business_profile_id: businessProfileId,
      cost_data: costData,
      market_data: marketData,
    }
  );
  return response.costing_analysis;
};

export const getCostingAnalysis = async (analysisId: string): Promise<CostingAnalysis> => {
  const response = await apiCall<{ costing_analysis: CostingAnalysis }>(
    `/api/v1/strategy-advisor/costing/${analysisId}`,
    'GET'
  );
  return response.costing_analysis;
};

// ==================== Business Suggestion API ====================

export const getBusinessSuggestions = async (
  businessProfileId: string,
  businessContext: string,
  suggestionTypes?: string[]
): Promise<BusinessSuggestions> => {
  const response = await apiCall<{ business_suggestions: BusinessSuggestions }>(
    '/api/v1/strategy-advisor/suggestions',
    'POST',
    {
      business_profile_id: businessProfileId,
      business_context: businessContext,
      suggestion_types: suggestionTypes,
    }
  );
  return response.business_suggestions;
};

export const getSuggestions = async (businessProfileId: string): Promise<BusinessSuggestions> => {
  const response = await apiCall<{ business_suggestions: BusinessSuggestions }>(
    `/api/v1/strategy-advisor/suggestions?business_profile_id=${businessProfileId}`,
    'GET'
  );
  return response.business_suggestions;
};

// ==================== Analytics API ====================

export const getAnalyticsDashboard = async (
  businessProfileId: string,
  timeRange: string = '30d'
): Promise<AnalyticsDashboard> => {
  return apiCall(
    `/api/v1/analytics/dashboard?business_profile_id=${businessProfileId}&time_range=${timeRange}`,
    'GET'
  );
};

export const getMetrics = async (
  businessProfileId: string,
  metricNames: string[],
  timeRange: string = '30d'
): Promise<Record<string, any>> => {
  return apiCall(
    `/api/v1/analytics/metrics?business_profile_id=${businessProfileId}&metric_names=${metricNames.join(',')}&time_range=${timeRange}`,
    'GET'
  );
};

export const getTrends = async (
  businessProfileId: string,
  metricName: string,
  timeRange: string = '90d'
): Promise<{ metric: string; time_range: string; historical_data: any[]; trend: any; insights: string[] }> => {
  return apiCall(
    `/api/v1/analytics/trends?business_profile_id=${businessProfileId}&metric_name=${metricName}&time_range=${timeRange}`,
    'GET'
  );
};

export const getBenchmarks = async (
  businessProfileId: string,
  industry: string
): Promise<Record<string, any>> => {
  return apiCall(
    `/api/v1/analytics/benchmarks?business_profile_id=${businessProfileId}&industry=${industry}`,
    'GET'
  );
};

// ==================== Scoring API ====================

export const getCurrentScores = async (businessProfileId: string): Promise<AllScores> => {
  return apiCall(`/api/v1/scoring/current?business_profile_id=${businessProfileId}`, 'GET');
};

export const getScoreHistory = async (
  businessProfileId: string,
  scoreType: string,
  timeRange: string = '90d'
): Promise<ScoreHistory> => {
  return apiCall(
    `/api/v1/scoring/history?business_profile_id=${businessProfileId}&score_type=${scoreType}&time_range=${timeRange}`,
    'GET'
  );
};

export const getScoreDetails = async (
  businessProfileId: string,
  scoreType: string
): Promise<any> => {
  return apiCall(
    `/api/v1/scoring/${scoreType}?business_profile_id=${businessProfileId}`,
    'GET'
  );
};

export const recalculateScores = async (businessProfileId: string): Promise<AllScores> => {
  return apiCall(`/api/v1/scoring/recalculate`, 'POST', {
    business_profile_id: businessProfileId,
  });
};

export const getScoreBenchmarks = async (
  businessProfileId: string,
  industry: string
): Promise<Record<string, any>> => {
  return apiCall(
    `/api/v1/scoring/benchmarks?business_profile_id=${businessProfileId}&industry=${industry}`,
    'GET'
  );
};

// ==================== Orchestration API ====================

export const analyzeStrategy = async (
  request: StrategyAnalysisRequest
): Promise<StrategyAnalysisResponse> => {
  return apiCall('/api/v1/strategy-advisor/analyze', 'POST', request);
};

export const getAnalysisStatus = async (analysisId: string): Promise<any> => {
  return apiCall(`/api/v1/strategy-advisor/analysis/${analysisId}`, 'GET');
};

export const runOrchestrationJob = async (
  businessProfileId: string,
  agents: string[],
  executionMode: 'parallel' | 'sequential' = 'parallel'
): Promise<OrchestrationJob> => {
  const response = await apiCall<{ job: OrchestrationJob }>(
    '/api/v1/orchestration/analyze',
    'POST',
    {
      business_profile_id: businessProfileId,
      agents,
      execution_mode: executionMode,
    }
  );
  return response.job;
};

export const getJobStatus = async (jobId: string): Promise<OrchestrationJob> => {
  const response = await apiCall<{ job: OrchestrationJob }>(
    `/api/v1/orchestration/status/${jobId}`,
    'GET'
  );
  return response.job;
};

export const runParallelExecution = async (
  businessProfileId: string,
  agents: string[]
): Promise<OrchestrationJob> => {
  const response = await apiCall<{ job: OrchestrationJob }>(
    '/api/v1/orchestration/parallel',
    'POST',
    {
      business_profile_id: businessProfileId,
      agents,
    }
  );
  return response.job;
};

export const runSequentialExecution = async (
  businessProfileId: string,
  agents: string[]
): Promise<OrchestrationJob> => {
  const response = await apiCall<{ job: OrchestrationJob }>(
    '/api/v1/orchestration/sequential',
    'POST',
    {
      business_profile_id: businessProfileId,
      agents,
    }
  );
  return response.job;
};

// ==================== Comprehensive Analysis ====================

export const runComprehensiveAnalysis = async (
  businessProfileId: string,
  businessContext: string,
  config?: Record<string, any>
): Promise<StrategyAnalysisResponse> => {
  return analyzeStrategy({
    business_profile_id: businessProfileId,
    analysis_type: 'comprehensive',
    config: {
      business_context: businessContext,
      ...config,
    },
  });
};

// ==================== Error Handling Helper ====================

export const handleApiError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unexpected error occurred';
};

// ==================== Loading State Helper ====================

export const withLoading = async <T>(
  setLoading: (loading: boolean) => void,
  operation: () => Promise<T>
): Promise<T> => {
  setLoading(true);
  try {
    return await operation();
  } finally {
    setLoading(false);
  }
};
