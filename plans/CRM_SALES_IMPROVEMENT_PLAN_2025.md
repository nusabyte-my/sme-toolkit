# CRM & Sales Dashboard Improvement Plan 2025

## Executive Summary

This document outlines a comprehensive improvement plan for the SME Toolkit's Lead CRM and Sales Dashboard, focusing on AI-powered lead management, unified sales analytics, and automated workflow orchestration.

## Current State Analysis

### Existing Components

**LeadManager.tsx** - Basic lead management interface
- Manual lead entry
- Heuristic-based lead scoring (status + engagement)
- AI analysis via Gemini (analyzeLead)
- Email generation (generateMarketingCopy)
- Basic table view with search
- No interaction history tracking
- No pipeline visualization
- No follow-up automation

**SalesTracker.tsx** - E-commerce sales tracking
- Marketplace connections (Shopee, Lazada, TikTok)
- Transaction sync
- Basic metrics (revenue, orders, AOV)
- Transaction table
- No analytics/forecasting
- No integration with lead data
- No customer insights

**Backend Infrastructure**
- Lead CRUD operations via FastAPI
- LeadAgent (LangGraph) for scoring/email/analysis
- LeadInteraction model (unused in frontend)
- CSV import/export
- No workflow automation

### Pain Points Identified

1. **Disconnected Systems**: Leads and sales operate independently with no data flow
2. **Basic Scoring**: Lead scoring is heuristic and ignores business profile context
3. **No Pipeline Visibility**: Missing Kanban board for lead stages
4. **No Interaction Tracking**: LeadInteraction model exists but unused
5. **No Follow-up Automation**: No automated reminders or task scheduling
6. **Limited Analytics**: No forecasting, trend analysis, or predictive insights
7. **No Customer Journey**: Missing 360-degree customer view
8. **Poor Segmentation**: Limited filtering and lead qualification workflows
9. **No Task Management**: Sales activities lack task tracking
10. **No ROI Tracking**: Unable to measure lead-to-customer conversion ROI

---

## Improvement Plan

### Domain 1: Lead Management Workflow

#### 1.1 Unified Lead Pipeline
**Objective**: Visual Kanban board with intelligent stage transitions

**Components**:
```
LeadKanbanBoard.tsx
├── PipelineColumn (New, Contacted, Qualified, Proposal, Won, Lost)
│   ├── LeadCard
│   │   ├── LeadScoreBadge
│   │   ├── AIInsightsSummary
│   │   ├── LastInteraction
│   │   └── QuickActions
├── DragAndDrop (react-beautiful-dnd or dnd-kit)
└── StageMetrics
```

**Features**:
- Drag-and-drop lead movement between stages
- Stage-specific metrics (conversion rates, time in stage)
- AI-powered stage recommendations
- Bulk actions (assign, tag, move)
- Custom pipeline stages per business type

**Data Flow**:
- Lead stage changes trigger LeadInteraction records
- Stage transitions update lead score automatically
- Business profile influences stage transitions (industry-specific pipelines)

#### 1.2 Profile-Integrated Lead Scoring
**Objective**: AI scoring that considers business profile context

**Scoring Algorithm**:
```typescript
interface LeadScoreFactors {
  demographics: number;  // 20% - industry, company size, role
  engagement: number;    // 25% - interactions, response time
  intent: number;        // 25% - expressed needs, budget, timeline
  fit: number;           // 30% - ICP alignment from business profile
}

interface BusinessProfile {
  idealCustomerProfile: {
    industries: string[];
    companySizes: string[];
    roles: string[];
    painPoints: string[];
  };
  products: Product[];
  marketSegments: string[];
}
```

**Implementation**:
- Extend LeadAgent to use BusinessProfile data
- Calculate ICP alignment score
- Dynamic scoring based on business stage
- Score history tracking for trend analysis

**Backend Changes**:
```python
# Enhanced LeadAgent with profile integration
class LeadAgent(BaseAgent):
    async def score_lead_with_profile(
        self, 
        lead: Dict, 
        profile: BusinessProfile
    ) -> Dict:
        # Calculate ICP alignment
        icp_score = self._calculate_icp_alignment(lead, profile)
        
        # Combine with engagement metrics
        engagement_score = self._calculate_engagement(lead)
        
        # Weighted scoring
        final_score = (
            icp_score * 0.40 +
            engagement_score * 0.35 +
            intent_score * 0.25
        )
        
        return {
            "score": final_score,
            "factors": {
                "icp_alignment": icp_score,
                "engagement": engagement_score,
                "intent": intent_score
            },
            "recommendations": self._generate_recommendations(lead, profile)
        }
```

#### 1.3 Interaction History & Timeline
**Objective**: Complete interaction history for each lead

**Components**:
```
LeadDetailView.tsx
├── LeadHeader (score, status, owner)
├── InteractionTimeline
│   ├── EmailInteraction
│   ├── CallInteraction
│   ├── MeetingInteraction
│   └── NoteInteraction
├── AIInsightsPanel
└── QuickActions (schedule, email, call)
```

**Features**:
- Chronological interaction timeline
- Rich interaction types (email, call, meeting, note, task)
- AI-generated interaction summaries
- Next action recommendations
- Interaction outcome tracking

**Backend Integration**:
```python
# New endpoints in leads.py
@router.post("/{lead_id}/interactions")
async def add_interaction(
    lead_id: str,
    interaction: InteractionCreate,
    db: AsyncSession = Depends(get_db)
):
    # Create interaction record
    # Update lead score based on interaction
    # Trigger follow-up task if needed
    pass

@router.get("/{lead_id}/timeline")
async def get_lead_timeline(lead_id: str, db: AsyncSession = Depends(get_db)):
    # Get all interactions with lead
    # Include AI insights for each interaction
    pass
```

#### 1.4 Automated Follow-up System
**Objective**: AI-powered follow-up scheduling and reminders

**Components**:
```
FollowUpSystem.tsx
├── FollowUpQueue
├── FollowUpScheduler
├── FollowUpTemplates
└── ReminderNotifications
```

**Features**:
- AI-recommended follow-up timing
- Template-based follow-up emails
- Escalation rules for unresponsive leads
- Integration with calendar (Google/Outlook)
- SMS reminders for critical follow-ups

**Backend Logic**:
```python
class FollowUpAgent(BaseAgent):
    async def schedule_follow_up(
        self, 
        lead: Lead, 
        last_interaction: LeadInteraction
    ) -> Dict:
        # Analyze lead engagement
        # Determine optimal follow-up timing
        # Generate personalized message
        # Schedule task
        pass
```

---

### Domain 2: Sales Dashboard & Analytics

#### 2.1 Unified Sales Dashboard
**Objective**: Single view of all sales metrics and trends

**Components**:
```
UnifiedSalesDashboard.tsx
├── KPIGrid
│   ├── RevenueCard (total, MRR, YTD)
│   ├── PipelineCard (total value, won, lost)
│   ├── ConversionCard (lead-to-customer, stage-to-stage)
│   └── ForecastCard (AI-predicted revenue)
├── RevenueChart (line chart with trend lines)
├── PipelineFunnel (stage conversion visualization)
├── TopLeads (high-score leads with quick actions)
└── AIInsightsPanel (key opportunities, risks, recommendations)
```

**Key Metrics**:
- Revenue trends (daily, weekly, monthly)
- Pipeline velocity
- Conversion rates by stage
- Average deal size
- Sales cycle length
- Lead source performance
- Product performance

**Data Integration**:
```typescript
interface UnifiedSalesData {
  leads: Lead[];
  sales: Transaction[];
  interactions: LeadInteraction[];
  businessProfile: BusinessProfile;
}

const aggregateMetrics = (data: UnifiedSalesData) => {
  const leadToRevenue = data.sales.filter(s => 
    data.leads.some(l => l.email === s.customer_email)
  );
  
  const conversionRate = (leadToRevenue.length / data.leads.length) * 100;
  
  return {
    conversionRate,
    pipelineValue: calculatePipelineValue(data.leads),
    revenueTrends: calculateTrends(data.sales),
    // ... more metrics
  };
};
```

#### 2.2 Predictive Sales Forecasting
**Objective**: AI-powered revenue predictions

**Algorithm**:
```typescript
interface ForecastModel {
  historicalRevenue: number[];
  pipelineValue: number;
  seasonalityFactors: number[];
  marketConditions: MarketAnalysis;
  businessGrowthRate: number;
}

const generateForecast = (model: ForecastModel) => {
  // Time series analysis
  // Pipeline probability weighting
  // Seasonal adjustments
  // Market trend integration
  // Confidence intervals
  return {
    predictedRevenue: number,
    confidence: number,
    bestCase: number,
    worstCase: number,
    keyDrivers: string[]
  };
};
```

**Components**:
```
SalesForecast.tsx
├── ForecastChart (line chart with confidence bands)
├── ForecastBreakdown (by product, by source)
├── ScenarioPlanner (what-if analysis)
└── ForecastAccuracy (actual vs predicted)
```

#### 2.3 Customer 360 View
**Objective**: Complete customer journey visualization

**Components**:
```
Customer360View.tsx
├── CustomerProfile (from leads + sales)
├── PurchaseHistory (transaction timeline)
├── EngagementMetrics (email opens, clicks, responses)
├── CustomerHealthScore (churn risk, CLV)
├── CrossSellUpsell (AI recommendations)
└── SupportHistory (if integrated)
```

**Integration Points**:
- Lead data → Sales transactions → Customer profile
- Social media insights → Personalization
- BMC data → Product recommendations
- Strategy goals → Sales targets

---

### Domain 3: Workflow Automation

#### 3.1 Lead Qualification Workflows
**Objective**: Automated lead qualification based on ICP

**Components**:
```
LeadQualificationFlow.tsx
├── ICPDefinitionWizard (from business profile)
├── QualificationRules (customizable scoring rules)
├── AutoQualificationEngine
└── ManualOverride (review borderline cases)
```

**Workflow**:
```
New Lead → ICP Check → Score Calculation → 
Auto-Qualify (score > 80) OR 
Manual Review (score 50-80) OR 
Auto-Disqualify (score < 50)
```

**Rules Engine**:
```typescript
interface QualificationRule {
  id: string;
  name: string;
  condition: (lead: Lead, profile: BusinessProfile) => boolean;
  action: 'qualify' | 'review' | 'disqualify';
  weight: number;
}

const defaultRules: QualificationRule[] = [
  {
    id: 'industry-match',
    name: 'Industry in target segments',
    condition: (lead, profile) => 
      profile.idealCustomerProfile.industries.includes(lead.industry),
    action: 'qualify',
    weight: 0.3
  },
  // ... more rules
];
```

#### 3.2 Task & Activity Management
**Objective**: Centralized task management for sales activities

**Components**:
```
SalesTaskManager.tsx
├── TaskList (filtered by assignee, priority, due date)
├── TaskCalendar (calendar view)
├── TaskTemplates (call scripts, email templates)
├── TaskAutomation (recurring tasks, triggers)
└── TaskAnalytics (completion rates, bottlenecks)
```

**Task Types**:
- Follow-up calls
- Email outreach
- Demo scheduling
- Proposal preparation
- Contract review
- Post-sale check-in

**Automation Triggers**:
```typescript
interface TaskTrigger {
  event: 'lead_created' | 'stage_changed' | 'interaction_added';
  condition: (data: any) => boolean;
  task: SalesTask;
}

const triggers: TaskTrigger[] = [
  {
    event: 'lead_created',
    condition: (lead) => lead.score > 70,
    task: {
      type: 'call',
      title: 'Initial discovery call',
      dueDate: '2 days',
      template: 'discovery_call_script'
    }
  },
  // ... more triggers
];
```

#### 3.3 Sales Playbook Automation
**Objective**: AI-guided sales process based on business type

**Components**:
```
SalesPlaybook.tsx
├── PlaybookSelector (by industry, business stage)
├── StageGuides (step-by-step for each pipeline stage)
├── AIAssistant (real-time suggestions)
├── ScriptLibrary (call scripts, email templates)
└── BestPractices (from top performers)
```

**Playbook Structure**:
```typescript
interface SalesPlaybook {
  id: string;
  businessType: string;
  stages: {
    [stage: string]: {
      objectives: string[];
      actions: PlaybookAction[];
      templates: Template[];
      aiTips: string[];
      metrics: string[];
    };
  };
}

const playbooks: SalesPlaybook[] = [
  {
    id: 'saas-playbook',
    businessType: 'SaaS',
    stages: {
      'discovery': {
        objectives: ['Understand pain points', 'Qualify budget'],
        actions: ['Schedule demo', 'Send case studies'],
        templates: ['discovery_email', 'demo_invite'],
        aiTips: ['Focus on ROI', 'Ask about current solution'],
        metrics: ['conversion_to_demo', 'demo_attendance_rate']
      },
      // ... more stages
    }
  },
  // ... more playbooks
];
```

---

### Domain 4: API & Data Architecture

#### 4.1 Enhanced Lead API
**Objective**: Comprehensive API for all CRM operations

**New Endpoints**:
```python
# Lead Operations
POST   /api/v1/leads                    # Create lead
GET    /api/v1/leads                    # List leads with filters
GET    /api/v1/leads/{id}               # Get lead details
PUT    /api/v1/leads/{id}               # Update lead
DELETE /api/v1/leads/{id}               # Delete lead

# Lead Scoring
POST   /api/v1/leads/{id}/score         # Score single lead
POST   /api/v1/leads/batch-score        # Score multiple leads
GET    /api/v1/leads/{id}/score-history # Score trend

# Interactions
POST   /api/v1/leads/{id}/interactions  # Add interaction
GET    /api/v1/leads/{id}/interactions  # List interactions
GET    /api/v1/leads/{id}/timeline      # Full timeline

# Follow-ups
POST   /api/v1/leads/{id}/follow-up     # Schedule follow-up
GET    /api/v1/leads/follow-up/queue    # Get follow-up queue
PUT    /api/v1/leads/{id}/follow-up     # Update follow-up

# Pipeline
POST   /api/v1/leads/{id}/stage         # Change stage
GET    /api/v1/pipeline/metrics         # Pipeline metrics
GET    /api/v1/pipeline/stages          # Stage definitions

# Tasks
POST   /api/v1/tasks                    # Create task
GET    /api/v1/tasks                    # List tasks
PUT    /api/v1/tasks/{id}               # Update task
GET    /api/v1/tasks/calendar          # Calendar view

# Analytics
GET    /api/v1/analytics/sales          # Sales analytics
GET    /api/v1/analytics/forecast       # Revenue forecast
GET    /api/v1/analytics/conversion     # Conversion rates
GET    /api/v1/analytics/customer-360   # Customer insights
```

#### 4.2 Data Models Enhancement

**Lead Model Extension**:
```python
class Lead(Base):
    # ... existing fields
    
    # New fields
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String)
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    next_follow_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    lead_source: Mapped[Optional[str]] = mapped_column(String)
    lead_campaign: Mapped[Optional[str]] = mapped_column(String)
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Score history
    score_history: Mapped[Optional[list]] = mapped_column(JSON)
    
    # Relationships
    tasks = relationship("SalesTask", back_populates="lead")
```

**New Models**:
```python
class SalesTask(Base):
    __tablename__ = "sales_tasks"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    lead_id: Mapped[str] = mapped_column(String, ForeignKey("leads.id"))
    assigned_to: Mapped[str] = mapped_column(String)
    
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    task_type: Mapped[str] = mapped_column(String)  # call, email, meeting, other
    status: Mapped[str] = mapped_column(String)  # pending, in_progress, completed, cancelled
    
    priority: Mapped[str] = mapped_column(String)  # high, medium, low
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Template reference
    template_id: Mapped[Optional[str]] = mapped_column(String)
    template_variables: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Automation
    trigger_type: Mapped[Optional[str]] = mapped_column(String)
    trigger_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    lead = relationship("Lead", back_populates="tasks")

class FollowUpRule(Base):
    __tablename__ = "follow_up_rules"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    business_profile_id: Mapped[str] = mapped_column(String, ForeignKey("business_profiles.id"))
    
    name: Mapped[str] = mapped_column(String)
    trigger_event: Mapped[str] = mapped_column(String)
    trigger_condition: Mapped[Optional[str]] = mapped_column(Text)
    
    delay_hours: Mapped[int] = mapped_column(Integer)
    task_template_id: Mapped[str] = mapped_column(String)
    
    priority: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

#### 4.3 AI Service Integration

**Enhanced LeadAgent**:
```python
class LeadAgent(BaseAgent):
    async def qualify_lead(
        self, 
        lead: Dict, 
        profile: BusinessProfile
    ) -> Dict:
        """Determine if lead matches ICP"""
        prompt = QUALIFICATION_PROMPT.format(
            lead=lead,
            icp=profile.ideal_customer_profile,
            products=profile.products
        )
        result = await self.client.generate_json(prompt)
        return {
            "qualified": result.get("qualified"),
            "score": result.get("score"),
            "reasons": result.get("reasons"),
            "next_actions": result.get("next_actions")
        }
    
    async def predict_conversion(
        self, 
        lead: Lead,
        interactions: List[LeadInteraction]
    ) -> Dict:
        """Predict lead-to-customer conversion probability"""
        prompt = CONVERSION_PREDICTION_PROMPT.format(
            lead=lead.model_dump(),
            interaction_summary=summarize_interactions(interactions)
        )
        result = await self.client.generate_json(prompt)
        return {
            "probability": result.get("probability"),
            "confidence": result.get("confidence"),
            "key_factors": result.get("key_factors"),
            "improvement_suggestions": result.get("suggestions")
        }
    
    async def recommend_next_action(
        self, 
        lead: Lead,
        current_stage: str
    ) -> Dict:
        """AI-recommended next action"""
        prompt = NEXT_ACTION_PROMPT.format(
            lead=lead.model_dump(),
            current_stage=current_stage
        )
        result = await self.client.generate_json(prompt)
        return {
            "action": result.get("action"),
            "channel": result.get("channel"),  # email, call, in-person
            "timing": result.get("timing"),
            "template": result.get("template"),
            "rationale": result.get("rationale")
        }
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Backend**:
- [ ] Extend Lead model with new fields
- [ ] Create SalesTask and FollowUpRule models
- [ ] Implement interaction tracking endpoints
- [ ] Add task management endpoints
- [ ] Enhance LeadAgent with profile integration

**Frontend**:
- [ ] Create LeadDetailView component
- [ ] Build InteractionTimeline component
- [ ] Implement InteractionHistory component
- [ ] Create SalesTaskManager component
- [ ] Build FollowUpScheduler component

**Deliverables**:
- Database migrations deployed
- New API endpoints functional
- Interaction tracking working
- Task management system operational

### Phase 2: Pipeline & Scoring (Weeks 3-4)

**Backend**:
- [ ] Implement profile-based lead scoring
- [ ] Add score history tracking
- [ ] Create qualification rules engine
- [ ] Build pipeline metrics API
- [ ] Implement lead forecasting API

**Frontend**:
- [ ] Build LeadKanbanBoard component
- [ ] Create PipelineColumn components
- [ ] Implement drag-and-drop functionality
- [ ] Build StageMetrics component
- [ ] Create ScoreHistoryChart component

**Deliverables**:
- Kanban board with all stages
- AI-powered lead scoring with profile context
- Pipeline metrics dashboard
- Score trend visualization

### Phase 3: Analytics & Forecasting (Weeks 5-6)

**Backend**:
- [ ] Implement sales analytics aggregation
- [ ] Build forecasting model
- [ ] Create customer 360 view API
- [ ] Add conversion rate analysis
- [ ] Implement trend detection algorithms

**Frontend**:
- [ ] Build UnifiedSalesDashboard component
- [ ] Create SalesForecast component
- [ ] Implement Customer360View component
- [ ] Build RevenueChart component
- [ ] Create PipelineFunnel component

**Deliverables**:
- Unified sales dashboard with all metrics
- AI-powered revenue forecasting
- Customer 360 view
- Interactive charts and visualizations

### Phase 4: Automation & Playbooks (Weeks 7-8)

**Backend**:
- [ ] Implement follow-up automation
- [ ] Build sales playbook system
- [ ] Create task automation triggers
- [ ] Add template management
- [ ] Implement workflow orchestration

**Frontend**:
- [ ] Build SalesPlaybook component
- [ ] Create PlaybookSelector component
- [ ] Implement TaskAutomation component
- [ ] Build TemplateLibrary component
- [ ] Create WorkflowBuilder component

**Deliverables**:
- Automated follow-up system
- Sales playbook with industry-specific guides
- Task automation with triggers
- Template library for emails and calls

### Phase 5: Integration & Polish (Weeks 9-10)

**Integration**:
- [ ] Connect leads to sales transactions
- [ ] Integrate with business profiles
- [ ] Connect to BMC data
- [ ] Integrate with strategy goals
- [ ] Add social media insights

**Polish**:
- [ ] Performance optimization
- [ ] Responsive design
- [ ] Error handling
- [ ] Loading states
- [ ] User testing

**Deliverables**:
- Full integration complete
- Performance optimized
- UI/UX polished
- User feedback incorporated

---

## Success Metrics

### Lead Management
- Lead-to-customer conversion rate: +25%
- Average sales cycle length: -20%
- Lead score accuracy: >85%
- Follow-up compliance: >90%

### Sales Performance
- Revenue forecasting accuracy: ±10%
- Pipeline visibility: 100%
- Sales team productivity: +30%
- Customer retention: +15%

### User Experience
- Task completion time: -40%
- Dashboard load time: <2s
- User satisfaction score: >4.5/5
- Feature adoption rate: >80%

---

## Risk Mitigation

### Technical Risks
- **Performance**: Large lead datasets may slow UI
  - Mitigation: Implement pagination, lazy loading, caching
- **AI Accuracy**: Lead scoring may be inaccurate initially
  - Mitigation: Continuous feedback loop, model retraining
- **Data Consistency**: Sync issues between leads and sales
  - Mitigation: Atomic transactions, data validation

### Business Risks
- **User Adoption**: Complex workflows may overwhelm users
  - Mitigation: Progressive rollout, tutorials, onboarding
- **Feature Creep**: Too many features delay launch
  - Mitigation: Strict MVP scope, phased approach

---

## Conclusion

This improvement plan transforms the basic Lead CRM and Sales Dashboard into a comprehensive, AI-powered sales management platform. The phased approach ensures incremental value delivery while building toward the complete solution.

Key innovations:
- Profile-integrated lead scoring for better qualification
- Unified view connecting leads, interactions, and sales
- AI-powered forecasting and recommendations
- Automated workflows reducing manual effort
- Playbook-driven sales process standardization

The result is a sales system that not only tracks leads and sales but actively guides users to close more deals faster.
