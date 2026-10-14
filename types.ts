export enum AppView {
  LANDING = 'LANDING',
  ADMIN = 'ADMIN',
  DASHBOARD = 'DASHBOARD',
  AGENT_FORGE = 'AGENT_FORGE',
  AUTOMATIONS = 'AUTOMATIONS',
  BOOKKEEPING = 'BOOKKEEPING',
  HR = 'HR',
  BILLING = 'BILLING',
  CHANNELS = 'CHANNELS',
  ECOMMERCE = 'ECOMMERCE',
  SOCIAL_STUDIO = 'SOCIAL_STUDIO',
  SEO_STUDIO = 'SEO_STUDIO',
  MARKET_RESEARCH = 'MARKET_RESEARCH',
  QUICKWINS = 'QUICKWINS',
  ADS = 'ADS',
  AD_OPTIMIZATION = 'AD_OPTIMIZATION',
  BMC_HUB = 'BMC_HUB',
  LEADS = 'LEADS',
  SALES = 'SALES',
  MARKETING_COPY = 'MARKETING_COPY',
  MARKETING_VISUAL = 'MARKETING_VISUAL',
  MARKETING_VIDEO = 'MARKETING_VIDEO',
  STRATEGY = 'STRATEGY',
  PROFILES = 'PROFILES',
  IDEATION = 'IDEATION',
  PRIVACY = 'PRIVACY',
  TERMS = 'TERMS'
}

export enum SubscriptionTier {
  FREE = 'FREE',
  SME = 'SME',
  SME_PLUS = 'SME_PLUS',
  BUSINESS = 'BUSINESS',
  ENTERPRISE = 'ENTERPRISE'
}

export interface Lead {
  id: string;
  name: string;
  company: string;
  email: string;
  status: 'New' | 'Contacted' | 'Qualified' | 'Proposal' | 'Won' | 'Lost';
  engagement: 'Low' | 'Medium' | 'High';
  notes: string;
  score?: number;
  scoreRationale?: string;
  lastAction?: string;
}

export interface BusinessCanvasData {
  keyPartners: string[];
  keyActivities: string[];
  keyResources: string[];
  valuePropositions: string[];
  customerRelationships: string[];
  channels: string[];
  customerSegments: string[];
  costStructure: string[];
  revenueStreams: string[];
}

export interface GeneratedVideo {
  uri: string;
  expiryTime?: string;
}

// Growth Score Types
export interface ScoreFactor {
  name: string;
  score: number;
  detail: string;
}

export interface ScoreComponent {
  score: number;
  weight: number;
  weighted_score: number;
  factors: ScoreFactor[];
  recommendations: string[];
}

export interface GrowthScore {
  overall_score: number;
  grade: string;
  components: {
    bmc_quality: ScoreComponent;
    strategy_alignment: ScoreComponent;
    market_readiness: ScoreComponent;
    execution_capability: ScoreComponent;
  };
  summary: string;
  improvement_priorities: string[];
  next_steps?: string[];
}

// Business Profile Types
export interface BusinessProfile {
  id: string;
  user_id: string;
  company_name?: string;
  industry?: string;
  business_stage?: string;
  bmc_data?: BusinessCanvasData;
  business_context?: string;
  created_at: string;
  updated_at: string;
}

// Company Goal Types
export interface CompanyGoal {
  id: string;
  title: string;
  description?: string;
  priority: 'high' | 'medium' | 'low';
  progress: number;
  deadline?: string;
  status: 'active' | 'completed' | 'paused';
}

// Chat Types
export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  metadata?: {
    suggestions?: string[];
    extracted_info?: Record<string, unknown>;
  };
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  extracted_context: Record<string, unknown>;
  phase: 'discovery' | 'refinement' | 'confirmation';
  ready_for_wizard: boolean;
  wizard_prefill?: Record<string, string>;
}

// Multi-agent Analysis Results
export interface MarketAnalysis {
  success: boolean;
  market_size?: {
    tam: string;
    sam: string;
    som: string;
  };
  competitive_analysis?: {
    direct_competitors: string[];
    indirect_competitors: string[];
    competitive_advantages: string[];
    threats: string[];
  };
  positioning?: {
    recommended_position: string;
    differentiation_factors: string[];
  };
  market_readiness_score?: number;
  timing_assessment?: string;
  key_market_trends?: string[];
}

export interface FinancialAnalysis {
  success: boolean;
  revenue_analysis?: Record<string, unknown>;
  cost_analysis?: Record<string, unknown>;
  financial_health_score?: number;
  funding_readiness?: string;
  key_metrics?: string[];
  financial_recommendations?: string[];
}

export interface OperationsAnalysis {
  success: boolean;
  operations_assessment?: Record<string, unknown>;
  resource_analysis?: Record<string, unknown>;
  partnership_assessment?: Record<string, unknown>;
  execution_capability_score?: number;
  operational_priorities?: string[];
}

export interface GrowthAnalysis {
  success: boolean;
  growth_opportunities?: Array<{
    opportunity: string;
    potential: string;
    timeframe: string;
    requirements: string[];
  }>;
  scaling_recommendations?: string[];
  growth_score_factors?: Record<string, number>;
  priority_actions?: string[];
}

export interface IdeationResults {
  success: boolean;
  innovation_opportunities?: Array<{
    idea: string;
    category: string;
    impact: string;
    effort: string;
  }>;
  pivot_suggestions?: Array<{
    direction: string;
    rationale: string;
    risks: string[];
  }>;
  feature_ideas?: string[];
  differentiation_strategies?: Array<{
    strategy: string;
    competitive_advantage: string;
  }>;
  creative_experiments?: Array<{
    experiment: string;
    hypothesis: string;
    resources_needed: string;
  }>;
}

export interface ActionItem {
  category: string;
  action: string;
  priority: 'high' | 'medium' | 'low';
}

export interface FullAnalysisResult {
  success: boolean;
  growth_score?: GrowthScore;
  market_analysis?: MarketAnalysis;
  financial_analysis?: FinancialAnalysis;
  operations_analysis?: OperationsAnalysis;
  growth_analysis?: GrowthAnalysis;
  ideation_results?: IdeationResults;
  strategy_recommendations?: string[];
  action_items?: ActionItem[];
  error?: string;
}

// Strategy Advisor Types
export interface SmartCriteria {
  specific: string;
  measurable: string;
  achievable: string;
  relevant: string;
  time_bound: string;
}

export interface BMCAlignment {
  aligned_blocks: string[];
  alignment_score: number;
  gaps: string[];
}

export interface Milestone {
  milestone: string;
  target_date: string;
  metrics: string[];
}

export interface Goal {
  id: string;
  title: string;
  description: string;
  category: string;
  smart_criteria: SmartCriteria;
  bmc_alignment: BMCAlignment;
  priority: 'high' | 'medium' | 'low';
  estimated_completion: string;
  key_milestones: Milestone[];
  required_resources: string[];
  potential_obstacles: string[];
  success_metrics: string[];
}

export interface GoalAnalysis {
  total_goals: number;
  by_category: Record<string, number>;
  alignment_score: number;
  feasibility_score: number;
  recommendations: string[];
}

export interface GrowthOpportunity {
  id: string;
  title: string;
  type: string;
  potential_revenue_impact: string;
  confidence_score: number;
  required_investment: string;
  expected_roi: string;
  time_to_market: string;
  key_actions: string[];
  risks: string[];
  mitigation_strategies: string[];
}

export interface GrowthChannel {
  channel: string;
  priority: 'high' | 'medium' | 'low';
  expected_impact: string;
  budget_allocation: string;
  tactics: string[];
}

export interface RoadmapPhase {
  phase: string;
  duration: string;
  objectives: string[];
  deliverables: string[];
  success_criteria: string[];
}

export interface RiskAssessment {
  risk: string;
  probability: number;
  impact: 'high' | 'medium' | 'low';
  mitigation: string;
}

export interface GrowthPlan {
  plan_id: string;
  title: string;
  timeframe: string;
  overall_growth_potential: number;
  growth_opportunities: GrowthOpportunity[];
  growth_channels: GrowthChannel[];
  implementation_roadmap: RoadmapPhase[];
  resource_requirements: {
    team: string[];
    budget: string;
    tools: string[];
  };
  kpi_targets: Record<string, string>;
  risk_assessment: {
    high_risks: RiskAssessment[];
  };
}

export interface CostBreakdown {
  category: string;
  amount: string;
  percentage: number;
}

export interface CostStructure {
  fixed_costs: {
    total: string;
    breakdown: CostBreakdown[];
  };
  variable_costs: {
    total: string;
    breakdown: CostBreakdown[];
  };
  total_monthly_cost: string;
  cost_per_unit: string;
}

export interface PricingStrategy {
  strategy: string;
  recommended_price: string;
  rationale: string;
  expected_margin: string;
  market_position: string;
  target_customers: string;
}

export interface OptimizationOpportunity {
  area: string;
  current_cost: string;
  potential_savings: string;
  savings_percentage: number;
  actions: string[];
  implementation_effort: 'low' | 'medium' | 'high';
  time_to_impact: string;
}

export interface BreakEvenAnalysis {
  current_price: string;
  break_even_units: number;
  break_even_revenue: string;
  margin_of_safety: string;
  sensitivity_analysis: Record<string, any>;
}

export interface CostingAnalysis {
  current_cost_structure: CostStructure;
  pricing_strategies: PricingStrategy[];
  optimization_opportunities: OptimizationOpportunity[];
  break_even_analysis: BreakEvenAnalysis;
  cost_benchmarks: {
    industry_average: Record<string, any>;
    performance: string;
  };
}

export interface BusinessOpportunity {
  id: string;
  title: string;
  type: string;
  description: string;
  potential_revenue: string;
  investment_required: string;
  time_to_market: string;
  feasibility_score: number;
  alignment_with_current_business: number;
  key_advantages: string[];
  implementation_steps: string[];
  risks: string[];
  success_probability: number;
}

export interface PartnershipOpportunity {
  id: string;
  title: string;
  type: string;
  partner_type: string;
  potential_benefits: string[];
  required_commitment: string;
  estimated_value: string;
  alignment_score: number;
}

export interface MarketExpansion {
  id: string;
  title: string;
  type: string;
  target_market: string;
  market_size: string;
  growth_rate: string;
  entry_strategy: string;
  required_investments: string[];
  competitive_advantage: string;
  timeline: string;
  potential_revenue: string;
}

export interface InnovationSuggestion {
  id: string;
  title: string;
  type: string;
  description: string;
  development_effort: 'low' | 'medium' | 'high';
  potential_impact: string;
  required_resources: string[];
  competitive_advantage: string;
}

export interface BusinessSuggestions {
  new_opportunities: BusinessOpportunity[];
  partnership_opportunities: PartnershipOpportunity[];
  market_expansions: MarketExpansion[];
  innovation_suggestions: InnovationSuggestion[];
  prioritized_recommendations: Array<{
    rank: number;
    suggestion_id: string;
    reason: string;
    expected_value: string;
  }>;
}

export interface MetricData {
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  change_percentage: number;
}

export interface TrendData {
  date: string;
  value: number;
}

export interface BenchmarkComparison {
  metric: string;
  your_value: number;
  industry_average: number;
  top_quartile: number;
  performance: 'above_average' | 'average' | 'below_average';
}

export interface Insight {
  id: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  actionable_steps: string[];
  impact: string;
}

export interface AnalyticsDashboard {
  metrics: MetricData[];
  trends: Record<string, TrendData[]>;
  benchmarks: BenchmarkComparison[];
  insights: Insight[];
  time_range: string;
}

export interface SubMetric {
  name: string;
  score: number;
  weight: number;
  description: string;
}

export interface ScoreData {
  score_type: string;
  overall_score: number;
  grade: string;
  sub_metrics: SubMetric[];
  trend: 'improving' | 'stable' | 'declining';
  change: number;
  benchmark: number;
  recommendations: string[];
}

export interface ScoreHistory {
  score_type: string;
  history: Array<{
    date: string;
    score: number;
  }>;
}

export interface AllScores {
  business_health: ScoreData;
  growth_potential: ScoreData;
  financial_stability: ScoreData;
  market_position: ScoreData;
  operational_efficiency: ScoreData;
  innovation_readiness: ScoreData;
}

export interface AgentStatus {
  agent_name: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result?: any;
  error?: string;
}

export interface OrchestrationJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  execution_mode: 'parallel' | 'sequential';
  agents: AgentStatus[];
  started_at: string;
  completed_at?: string;
  results?: any;
  error?: string;
}

export interface StrategyAnalysisRequest {
  business_profile_id: string;
  analysis_type: 'comprehensive' | 'goals' | 'growth' | 'costing' | 'suggestions';
  config?: Record<string, any>;
}

export interface StrategyAnalysisResponse {
  analysis_id: string;
  results: {
    goals?: { goals: Goal[]; goal_analysis: GoalAnalysis };
    growth?: GrowthPlan;
    costing?: CostingAnalysis;
    suggestions?: BusinessSuggestions;
  };
  scores?: AllScores;
  insights?: Insight[];
}

// Augment global types to include AIStudio interface methods
// We merge with the global AIStudio interface that is already used by window.aistudio
declare global {
  interface AIStudio {
    hasSelectedApiKey: () => Promise<boolean>;
    openSelectKey: () => Promise<void>;
  }
}
