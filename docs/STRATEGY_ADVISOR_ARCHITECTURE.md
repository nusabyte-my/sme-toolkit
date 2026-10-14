# Strategy Advisor System Architecture

## Overview

The Multi-Agent Strategy Advisor System is a comprehensive business intelligence platform that leverages AI-powered agents to provide strategic insights, growth recommendations, and actionable advice for SMEs (Small and Medium Enterprises).

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Strategy     │  │ Dashboard    │  │ BMC          │ │
│  │ Advisor     │  │ Components   │  │ Components    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Strategy     │  │ Analytics     │  │ Scoring      │ │
│  │ Advisor API │  │ API          │  │ API          │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Service Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Strategy     │  │ Analytics     │  │ Scoring      │ │
│  │ Orchestrator │  │ Service       │  │ Service       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Goal         │  │ Growth        │  │ Costing      │ │
│  │ Service      │  │ Service       │  │ Service       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Suggestion   │  │ Cache         │  │ Monitoring    │ │
│  │ Service      │  │ Service       │  │ Service       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Agent Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Goal         │  │ Growth Plan   │  │ Costing      │ │
│  │ Advisor      │  │ Advisor       │  │ Advisor      │ │
│  │ Agent        │  │ Agent         │  │ Agent        │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Business     │  │ Strategy      │  │ Growth       │ │
│  │ Suggestion   │  │ Agent         │  │ Agent        │ │
│  │ Agent        │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ SQLite       │  │ Cache         │  │ External      │ │
│  │ Database     │  │ (In-memory/  │  │ Services     │ │
│  │              │  │ Redis)        │  │ (Gemini AI)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Layer

**Technology Stack:**
- React 19.2.3
- TypeScript 5.8.2
- Vite 6.2.0
- Tailwind CSS
- Lucide React Icons

**Key Components:**
- `StrategyAdvisor`: Main advisor interface
- `ScoreGauge`: Visual score display
- `TrendChart`: Trend visualization
- `OpportunityCard`: Opportunity display
- `InsightPanel`: Insights display
- `BenchmarkBar`: Benchmark comparison
- `AgentStatus`: Agent status indicator
- `ProgressBar`: Progress tracking
- `MilestoneTimeline`: Milestone visualization

**State Management:**
- `StrategyAdvisorContext`: Global state for advisor data
- React hooks for local state

### 2. API Layer

**Technology Stack:**
- FastAPI 0.109.0+
- Pydantic 2.5.0+
- Async/await patterns
- HTTP/HTTPS

**Key Endpoints:**
- `/api/v1/strategy-advisor/*`: Strategy advisor endpoints
- `/api/v1/analytics/*`: Analytics endpoints
- `/api/v1/scoring/*`: Scoring endpoints
- `/api/v1/orchestration/*`: Orchestration endpoints

### 3. Service Layer

**Core Services:**
- `StrategyOrchestrator`: Coordinates agent execution
- `ScoringService`: Calculates business scores
- `AnalyticsService`: Provides analytics data
- `GoalService`: Manages goals
- `GrowthService`: Manages growth plans
- `CostingService`: Manages costing analysis
- `SuggestionService`: Manages business suggestions
- `CacheService`: Performance optimization
- `MonitoringService`: Logging and metrics

### 4. Agent Layer

**Advisor Agents:**
- `GoalAdvisorAgent`: SMART goal generation
- `GrowthPlanAdvisorAgent`: Growth strategy creation
- `CostingAdvisorAgent`: Cost and pricing analysis
- `BusinessSuggestionAgent`: Opportunity identification

**Supporting Agents:**
- `StrategyAgent`: General strategy advice
- `GrowthAgent`: Growth analysis
- `FinanceAgent`: Financial analysis
- `MarketAgent`: Market analysis

### 5. Data Layer

**Database:**
- SQLite (development/testing)
- PostgreSQL (production recommended)
- SQLAlchemy ORM
- Async sessions

**Cache:**
- In-memory cache (development)
- Redis (production recommended)
- TTL-based expiration

**External Services:**
- Google Gemini AI
- REST APIs for data sources

## Data Flow

### 1. Analysis Request Flow

```
User Request
    ↓
Frontend Component
    ↓
API Call (POST /api/v1/strategy-advisor/analyze)
    ↓
Strategy Orchestrator
    ↓
Load Business Profile (from DB/Cache)
    ↓
Execute Agents (Parallel/Sequential)
    ├─→ Goal Advisor Agent
    ├─→ Growth Plan Advisor Agent
    ├─→ Costing Advisor Agent
    └─→ Business Suggestion Agent
    ↓
Aggregate Results
    ↓
Calculate Scores
    ↓
Generate Insights
    ↓
Store Analysis (DB)
    ↓
Cache Results
    ↓
Return Response
    ↓
Frontend Display
```

### 2. Goal Management Flow

```
User Action (Create/Update/Delete Goal)
    ↓
Frontend Component
    ↓
API Call (POST/PUT/DELETE /api/v1/strategy-advisor/goals)
    ↓
Goal Service
    ↓
Database Operation
    ↓
Cache Update
    ↓
Return Response
    ↓
Frontend Update
```

### 3. Score Calculation Flow

```
Score Request
    ↓
Scoring Service
    ↓
Check Cache
    ├─→ Hit: Return cached score
    └─→ Miss: Calculate score
            ↓
        Load Profile Data
        ↓
        Apply Scoring Algorithm
        ↓
        Store in Cache
        ↓
        Store in DB (for history)
    ↓
Return Score
```

## Key Algorithms

### 1. Scoring Algorithms

**Business Health Score:**
```
Business Health = 
  (Financial Health × 0.30) +
  (Operational Efficiency × 0.25) +
  (Customer Satisfaction × 0.20) +
  (Market Position × 0.15) +
  (Innovation Readiness × 0.10)
```

**Growth Potential Score:**
```
Growth Potential = 
  (Market Opportunity × 0.35) +
  (Competitive Advantage × 0.25) +
  (Execution Capability × 0.20) +
  (Financial Capacity × 0.15) +
  (Innovation Potential × 0.05)
```

### 2. Agent Orchestration

**Parallel Execution:**
- Execute all agents simultaneously
- Wait for all to complete
- Aggregate results
- Handle failures gracefully

**Sequential Execution:**
- Execute agents in order
- Pass results between agents
- Each agent can use previous agent's output
- Better for dependent analyses

**Hybrid Execution:**
- Mix of parallel and sequential
- Independent agents run in parallel
- Dependent agents run sequentially
- Optimal for complex scenarios

### 3. Conflict Resolution

**Score Conflicts:**
- Average conflicting scores
- Weight by agent confidence
- Flag for manual review

**Recommendation Conflicts:**
- Merge similar recommendations
- Prioritize by impact
- Remove duplicates
- Rank by feasibility

## Performance Optimizations

### 1. Caching Strategy

**Cache Keys:**
- `score:{profile_id}:{score_type}` - Score data
- `profile:{profile_id}` - Business profile
- `analysis:{analysis_id}` - Analysis results
- `goals:{profile_id}` - Goals list

**TTL Settings:**
- Scores: 5 minutes
- Profiles: 10 minutes
- Analysis: 15 minutes
- Goals: 2 minutes

### 2. Database Optimization

**Indexes:**
- `business_profiles.id` (primary key)
- `company_goals.business_profile_id` (foreign key)
- `score_records.business_profile_id, score_type` (composite)
- `analytics_metrics.business_profile_id, metric_name` (composite)

**Query Optimization:**
- Use eager loading for relationships
- Implement pagination for large datasets
- Use select specific columns
- Avoid N+1 queries

### 3. API Optimization

**Response Optimization:**
- Compress responses
- Use HTTP/2
- Implement connection pooling
- Enable keep-alive

**Rate Limiting:**
- Per-user rate limits
- Per-endpoint rate limits
- Burst allowance
- Sliding window algorithm

## Security Considerations

### 1. Authentication & Authorization

- JWT-based authentication
- Role-based access control
- API key validation
- Session management

### 2. Data Protection

- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF tokens

### 3. API Security

- HTTPS only
- Rate limiting
- Request size limits
- Timeout handling

### 4. Data Privacy

- Encryption at rest
- Encryption in transit
- Data anonymization
- GDPR compliance

## Monitoring & Observability

### 1. Metrics

**Performance Metrics:**
- API response times
- Agent execution times
- Database query times
- Cache hit rates

**Business Metrics:**
- User engagement
- Feature usage
- Analysis frequency
- Success rates

### 2. Logging

**Log Levels:**
- DEBUG: Detailed debugging
- INFO: General information
- WARNING: Potential issues
- ERROR: Errors and failures
- CRITICAL: System failures

**Log Types:**
- Access logs
- Error logs
- Performance logs
- Security logs

### 3. Health Checks

**Endpoints:**
- `/health`: Overall system health
- `/health/db`: Database health
- `/health/cache`: Cache health
- `/health/ai`: AI service health

**Checks:**
- Database connectivity
- Cache availability
- External service status
- Resource utilization

## Deployment Architecture

### Development Environment

```
Local Machine
├── Frontend (Vite dev server)
├── Backend (FastAPI dev server)
├── Database (SQLite file)
└── Cache (In-memory)
```

### Production Environment

```
Load Balancer
├── Frontend Server 1
├── Frontend Server 2
└── Frontend Server 3
        ↓
API Gateway
├── API Server 1
├── API Server 2
└── API Server 3
        ↓
Database Cluster (PostgreSQL)
        ↓
Cache Cluster (Redis)
        ↓
External Services (Gemini AI)
```

## Scalability Considerations

### 1. Horizontal Scaling

- Stateless API servers
- Load balancing
- Auto-scaling groups
- Container orchestration

### 2. Vertical Scaling

- Increase server resources
- Optimize database queries
- Implement caching
- Use connection pooling

### 3. Database Scaling

- Read replicas for analytics
- Write master for transactions
- Connection pooling
- Query optimization

## Future Enhancements

### 1. Planned Features

- Real-time collaboration
- Advanced analytics
- Predictive modeling
- Custom agent creation
- Integration marketplace

### 2. Technical Improvements

- GraphQL API
- WebSocket support
- Event-driven architecture
- Microservices migration

## Conclusion

The Multi-Agent Strategy Advisor System provides a robust, scalable, and maintainable architecture for delivering AI-powered business intelligence to SMEs. The modular design allows for easy extension and maintenance, while the comprehensive testing and monitoring ensure reliability and performance.
