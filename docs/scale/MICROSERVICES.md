# SME Toolkit - Microservices Architecture

**Purpose:** Extract monolithic backend into independently scalable services

---

## Service Boundaries

### Current Monolith Structure
```
sme-toolkit-backend/
├── app/
│   ├── agents/          # AI agents
│   ├── api/v1/          # All endpoints
│   ├── providers/       # AI providers
│   ├── services/        # Business logic
│   ├── tools/           # AI tools
│   └── database.py      # All models
```

### Target Microservices Architecture
```
services/
├── auth-service/           # Authentication & authorization
├── billing-service/        # Tokens, subscriptions, payments
├── ai-orchestration-service/  # AI provider routing, agents
├── profile-service/        # User, business, social profiles
├── crm-service/            # Leads, tasks, marketplace
├── analytics-service/      # Scoring, metrics, insights
└── gateway-service/        # API gateway, rate limiting
```

---

## 1. Auth Service

**Port:** 8001
**Database:** Shared (users, subscriptions)

### Responsibilities
- JWT token generation and validation
- User authentication (email/password, OAuth)
- Session management
- API key management for external access

### Endpoints
```
POST   /auth/login
POST   /auth/register
POST   /auth/logout
POST   /auth/refresh
POST   /auth/api-keys
GET    /auth/verify
```

### Models
- UserSubscription
- UserProfile (subset)

### Migration Strategy
1. Extract auth endpoints to separate service
2. Implement token validation middleware in gateway
3. Add service-to-service authentication

---

## 2. Billing Service

**Port:** 8002
**Database:** Dedicated (tokens, transactions)

### Responsibilities
- Token account management
- Transaction processing
- Subscription billing (Stripe integration)
- Usage quota tracking
- Payment webhooks

### Endpoints
```
GET    /billing/balance
POST   /billing/purchase
GET    /billing/transactions
GET    /billing/usage
POST   /billing/subscribe
POST   /webhooks/stripe
```

### Models
- TokenAccount
- TokenTransaction
- UsageQuota
- TokenPackage
- ProviderCostRate

### Events Published
- `token.purchased`
- `token.consumed`
- `quota.exceeded`
- `subscription.created`
- `subscription.cancelled`

---

## 3. AI Orchestration Service

**Port:** 8003
**Database:** Minimal (provider configs)

### Responsibilities
- Multi-provider AI routing
- Fallback chain management
- Rate limiting per provider
- Agent orchestration (LangGraph)
- Circuit breaker management

### Endpoints
```
POST   /ai/text/generate
POST   /ai/image/generate
POST   /ai/video/generate
POST   /ai/agents/execute
GET    /ai/providers/status
GET    /ai/models/available
```

### Models
- ProviderCostRate
- ModelPreference

### Events Published
- `ai.request.started`
- `ai.request.completed`
- `ai.request.failed`
- `provider.fallback`

### Queue Integration
- Consumes: `ai_llm`, `ai_image`, `ai_video` queues
- Publishes: `token.consumed` events

---

## 4. Profile Service

**Port:** 8004
**Database:** Dedicated (profiles, social)

### Responsibilities
- User profile management
- Business profile management
- Social media connections
- Profile insights generation
- Privacy settings

### Endpoints
```
GET    /profiles/user
PUT    /profiles/user
GET    /profiles/business
PUT    /profiles/business
GET    /profiles/social
POST   /profiles/social
DELETE /profiles/social/{id}
POST   /profiles/social/sync
GET    /profiles/insights
```

### Models
- UserProfile
- BusinessProfile
- SocialMediaProfile
- UserActivityLog
- PrivacySetting
- ProfileInsight

---

## 5. CRM Service

**Port:** 8005
**Database:** Dedicated (leads, sales)

### Responsibilities
- Lead management
- Lead scoring
- Sales task automation
- Marketplace integration (Shopee, Lazada)
- Follow-up rules

### Endpoints
```
GET    /crm/leads
POST   /crm/leads
PUT    /crm/leads/{id}
DELETE /crm/leads/{id}
POST   /crm/leads/{id}/score
GET    /crm/tasks
POST   /crm/tasks
GET    /crm/marketplace/connections
POST   /crm/marketplace/auth/{platform}
GET    /crm/sales/transactions
```

### Models
- Lead
- LeadInteraction
- SalesTask
- FollowUpRule
- SalesTransaction
- MarketplaceCredential

### Events Published
- `lead.created`
- `lead.scored`
- `task.created`
- `marketplace.synced`

---

## 6. Analytics Service

**Port:** 8006
**Database:** Dedicated (analytics, scores)

### Responsibilities
- Business scoring
- Growth plan generation
- Analytics aggregation
- Dashboard data
- Trend analysis

### Endpoints
```
GET    /analytics/dashboard
GET    /analytics/scores/{type}
POST   /analytics/scores/calculate
GET    /analytics/growth-plans
POST   /analytics/growth-plans
GET    /analytics/trends
POST   /analytics/costing/analyze
```

### Models
- ScoreRecord
- AnalyticsMetric
- GrowthPlan
- CostingAnalysis
- Goal
- Suggestion

### Events Consumed
- `user.activity`
- `lead.scored`
- `token.consumed`

---

## 7. Gateway Service

**Port:** 8000 (public)

### Responsibilities
- Request routing
- Rate limiting
- Authentication validation
- Request/response transformation
- Circuit breaker (service level)
- API versioning

### Configuration
```yaml
routes:
  - path: /auth/*
    service: auth-service:8001
  - path: /billing/*
    service: billing-service:8002
  - path: /ai/*
    service: ai-orchestration-service:8003
  - path: /profiles/*
    service: profile-service:8004
  - path: /crm/*
    service: crm-service:8005
  - path: /analytics/*
    service: analytics-service:8006
```

---

## Inter-Service Communication

### Synchronous (REST)
- Gateway -> Services
- Auth validation requests
- Token balance checks

### Asynchronous (Event Bus)
```
                    ┌─────────────────┐
                    │   Event Bus     │
                    │   (Redis)       │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│    Billing    │   │ AI Orchestr.  │   │   Analytics   │
│   Service     │   │   Service     │   │   Service     │
└───────────────┘   └───────────────┘   └───────────────┘
        │                    │                    │
        │ token.consumed     │ ai.request.*      │ user.activity
        │ subscription.*     │ provider.*        │ lead.scored
        └────────────────────┴────────────────────┘
```

### Event Schema
```json
{
  "event_id": "uuid",
  "event_type": "token.consumed",
  "timestamp": "2026-05-23T17:00:00Z",
  "source": "ai-orchestration-service",
  "data": {
    "user_id": "user-123",
    "tokens": 100,
    "service_type": "image_generation",
    "operation_id": "op-456"
  },
  "correlation_id": "req-789"
}
```

---

## Database Separation

### Shared Database (Read-Only Replicas)
- UserSubscription (auth + billing reference)

### Dedicated Databases
| Service | Database | Size Estimate |
|---------|----------|---------------|
| Auth | sme_auth | ~100 MB |
| Billing | sme_billing | ~500 MB |
| AI Orchestration | sme_ai | ~50 MB |
| Profile | sme_profiles | ~200 MB |
| CRM | sme_crm | ~1 GB |
| Analytics | sme_analytics | ~2 GB |

### Migration Path
1. Create new databases
2. Copy data with zero downtime
3. Update service connection strings
4. Verify data integrity
5. Decommission old tables

---

## Deployment Architecture

### Kubernetes Namespace per Environment
```
sme-toolkit-dev/
sme-toolkit-staging/
sme-toolkit-prod/
```

### Service Deployment Template
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: billing-service
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: billing
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

### Horizontal Pod Autoscaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-orchestration-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-orchestration-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Migration Timeline

### Phase 1: Foundation (Week 1-2)
- [ ] Set up gateway service
- [ ] Extract auth service
- [ ] Implement service mesh (optional: Istio/Linkerd)

### Phase 2: Core Services (Week 3-4)
- [ ] Extract billing service
- [ ] Extract profile service
- [ ] Set up event bus

### Phase 3: Feature Services (Week 5-6)
- [ ] Extract AI orchestration service
- [ ] Extract CRM service
- [ ] Extract analytics service

### Phase 4: Optimization (Week 7-8)
- [ ] Database migration
- [ ] Load testing
- [ ] Performance tuning
- [ ] Documentation

---

## Rollback Strategy

1. **Feature Flags**: Toggle between monolith and microservice
2. **Traffic Shifting**: Gradual percentage-based routing
3. **Database Backups**: Point-in-time recovery enabled
4. **Service Versioning**: Maintain backward compatibility

---

## Monitoring per Service

| Service | Key Metrics |
|---------|-------------|
| Auth | Login success rate, token validation latency |
| Billing | Payment success rate, token balance accuracy |
| AI Orchestration | Provider latency, fallback rate, token consumption |
| Profile | Profile update latency, sync success rate |
| CRM | Lead processing time, scoring latency |
| Analytics | Score calculation time, dashboard load time |
| Gateway | Request rate, routing latency, error rate |
