export interface BusinessContextInput {
  company_name: string;
  industry: string;
  business_description: string;
  products_services: string;
  target_market: string;
  brand_voice: string;
  goals: string;
  currency: string;
  timezone: string;
  website: string;
  proof_points: string;
  constraints: string;
  logo_data_url?: string;
}
export interface BusinessContext extends BusinessContextInput {
  id: string;
  is_demo?: boolean;
  updated_at: string;
}
export interface SalesSummary {
  days: number;
  currency: string;
  revenue: number;
  previous_revenue: number;
  change_percent: number | null;
  orders: number;
  pending_orders: number;
  refunded_orders: number;
  average_order_value: number;
  excluded_currency_orders: number;
  by_platform: { platform: string; revenue: number; orders: number }[];
  daily: { date: string; revenue: number }[];
  latest_at: string | null;
}
export type AgentKind =
  | "business_review"
  | "marketing"
  | "sales"
  | "operations"
  | "strategy"
  | "ideation"
  | 'copywriting'
  | 'finance_readiness'
  | 'lead_followup'
  | 'fulfilment'
  | 'campaign_planner'
  | 'ad_efficiency'
  | 'creative_qa'
  | 'seo_readiness'
  | 'research_quality'
  | 'execution_coach'
  | 'bookkeeping_review'
  | 'people_review';
export interface AdvisorSkill {
  kind: AgentKind;
  name: string;
  title: string;
  group: string;
  mode: 'rules'|'llm';
  version: string;
  description: string;
  default_objective: string;
  inputs: string[];
  skill_markdown: string;
}
export interface AgentRun {
  id: string;
  kind: AgentKind;
  objective: string;
  status: "needs_review" | "approved" | "dismissed" | "failed";
  output: string;
  error: string | null;
  provider: string;
  context_snapshot: BusinessContext;
  created_at: string;
  skill?: {name:string;version:string;mode:'rules'|'llm'};
  evidence?: {as_of:string;issue_count:number;observations:string[];limits:string[];issues:{source_key:string;title:string;notes:string}[]};
}
export interface Campaign {
  id: string;
  title: string;
  platform: string;
  caption: string;
  scheduled_at: string | null;
  status: "draft" | "approved" | "archived";
  created_at: string;
  updated_at: string;
}
export interface Sale {
  id: string;
  platform: string;
  external_id: string | null;
  amount: number;
  currency: string;
  status: "pending" | "completed" | "refunded" | "cancelled";
  transaction_date: string;
  created_at: string;
}
export interface OwnerOverview {
  context: BusinessContext | null;
  sales: SalesSummary;
  agents: AgentRun[];
  campaigns: Campaign[];
  attention: {
    id: string;
    title: string;
    detail: string;
    view:
      | "profiles"
      | "sales"
      | "agent_forge"
      | "social_studio"
      | "ecommerce"
      | "quickwins"
      | "hr"
      | "bookkeeping";
  }[];
  operations: { employees:number; pending_leave:number; journal_entries:number; enabled_rules:number; latest_automation:{summary:string;status:string}|null };
  capabilities: {
    ai_available: boolean;
    ai_provider: string | null;
    publishing_available: boolean;
    marketplace_sync_available: boolean;
  };
}
