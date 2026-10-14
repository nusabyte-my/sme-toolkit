# Strategy Advisor API Documentation

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.sme-toolkit.com/api/v1
```

## Authentication

All API endpoints require authentication via JWT token:

```bash
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Strategy Advisor Endpoints

#### Analyze Strategy

Perform comprehensive strategy analysis using multiple advisors.

```http
POST /api/v1/strategy-advisor/analyze
```

**Request Body:**
```json
{
  "business_profile_id": "string (required)",
  "analysis_type": "comprehensive|quick|goal_focused|growth_focused|costing_focused|suggestion_focused",
  "include_goals": "boolean (default: true)",
  "include_growth": "boolean (default: true)",
  "include_costing": "boolean (default: true)",
  "include_suggestions": "boolean (default: true)"
}
```

**Response:**
```json
{
  "analysis_id": "string",
  "results": {
    "goals": {...},
    "growth": {...},
    "costing": {...},
    "suggestions": {...}
  },
  "scores": {
    "business_health": {...},
    "growth_potential": {...},
    "financial_stability": {...},
    "market_position": {...},
    "operational_efficiency": {...},
    "innovation_readiness": {...}
  },
  "insights": [...],
  "created_at": "ISO 8601 datetime"
}
```

#### Get Analysis

Retrieve a specific analysis by ID.

```http
GET /api/v1/strategy-advisor/analysis/{analysis_id}
```

**Response:**
```json
{
  "analysis_id": "string",
  "business_profile_id": "string",
  "analysis_type": "string",
  "results": {...},
  "scores": {...},
  "insights": [...],
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

#### Create Goal

Create a new SMART goal.

```http
POST /api/v1/strategy-advisor/goals
```

**Request Body:**
```json
{
  "business_profile_id": "string (required)",
  "title": "string (required)",
  "description": "string",
  "category": "financial|operational|market|innovation",
  "target_value": "number",
  "current_value": "number",
  "deadline": "ISO 8601 date",
  "priority": "high|medium|low",
  "smart_criteria": {
    "specific": "string",
    "measurable": "string",
    "achievable": "string",
    "relevant": "string",
    "time_bound": "string"
  },
  "bmc_alignment": {
    "aligned_blocks": ["string"],
    "alignment_score": "number (0-1)",
    "gaps": ["string"]
  },
  "milestones": [
    {
      "milestone": "string",
      "target_date": "ISO 8601 date",
      "metrics": ["string"]
    }
  ],
  "success_metrics": ["string"],
  "required_resources": ["string"],
  "potential_obstacles": ["string"]
}
```

**Response:**
```json
{
  "id": "string",
  "business_profile_id": "string",
  "title": "string",
  "description": "string",
  "category": "string",
  "target_value": "number",
  "current_value": "number",
  "deadline": "ISO 8601 date",
  "priority": "string",
  "status": "draft|in_progress|completed|on_hold",
  "smart_criteria": {...},
  "bmc_alignment": {...},
  "milestones": [...],
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

#### Get Goals

Retrieve all goals for a business profile.

```http
GET /api/v1/strategy-advisor/goals?business_profile_id={profile_id}
```

**Query Parameters:**
- `business_profile_id` (required): Business profile ID
- `category` (optional): Filter by category
- `status` (optional): Filter by status
- `priority` (optional): Filter by priority
- `limit` (optional): Number of results to return
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "goals": [...],
  "total": "number",
  "limit": "number",
  "offset": "number"
}
```

#### Update Goal

Update an existing goal.

```http
PUT /api/v1/strategy-advisor/goals/{goal_id}
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "current_value": "number",
  "status": "draft|in_progress|completed|on_hold",
  "priority": "high|medium|low",
  "milestones": [...]
}
```

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "current_value": "number",
  "status": "string",
  "priority": "string",
  "updated_at": "ISO 8601 datetime"
}
```

#### Delete Goal

Delete a goal.

```http
DELETE /api/v1/strategy-advisor/goals/{goal_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Goal deleted successfully"
}
```

#### Create Growth Plan

Create a new growth plan.

```http
POST /api/v1/strategy-advisor/growth-plans
```

**Request Body:**
```json
{
  "business_profile_id": "string (required)",
  "title": "string (required)",
  "timeframe": "string (e.g., '6 months')",
  "target_metrics": {
    "revenue_growth": "string (e.g., '50%')",
    "customer_acquisition": "string (e.g., '200 new customers')",
    "market_penetration": "string (e.g., '5%')"
  },
  "growth_opportunities": [
    {
      "id": "string",
      "title": "string",
      "type": "market_expansion|product_innovation|channel_optimization",
      "potential_revenue_impact": "string",
      "confidence_score": "number (0-1)",
      "required_investment": "number",
      "expected_roi": "string",
      "time_to_market": "string",
      "key_actions": ["string"],
      "risks": ["string"],
      "mitigation_strategies": ["string"]
    }
  ],
  "growth_channels": [
    {
      "channel": "string",
      "priority": "high|medium|low",
      "expected_impact": "string",
      "budget_allocation": "number",
      "tactics": ["string"]
    }
  ],
  "implementation_roadmap": [
    {
      "phase": "string",
      "duration": "string",
      "objectives": ["string"],
      "deliverables": ["string"],
      "success_criteria": ["string"]
    }
  ],
  "resource_requirements": {
    "team": ["string"],
    "budget": "number",
    "tools": ["string"]
  },
  "risk_assessment": {
    "high_risks": [...],
    "medium_risks": [...],
    "low_risks": [...]
  }
}
```

**Response:**
```json
{
  "id": "string",
  "business_profile_id": "string",
  "title": "string",
  "timeframe": "string",
  "plan_data": {...},
  "status": "draft|active|completed|archived",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

#### Get Growth Plans

Retrieve all growth plans for a business profile.

```http
GET /api/v1/strategy-advisor/growth-plans?business_profile_id={profile_id}
```

**Response:**
```json
{
  "growth_plans": [...],
  "total": "number"
}
```

#### Analyze Costing

Perform costing and pricing analysis.

```http
POST /api/v1/strategy-advisor/costing/analyze
```

**Request Body:**
```json
{
  "business_profile_id": "string (required)",
  "fixed_costs": {
    "rent": "number",
    "salaries": "number",
    "software": "number",
    "insurance": "number",
    "utilities": "number"
  },
  "variable_costs": {
    "materials": "number",
    "shipping": "number",
    "commissions": "number",
    "labor": "number",
    "marketing": "number"
  },
  "current_price": "number",
  "units_sold": "number",
  "competitor_pricing": [
    {
      "competitor": "string",
      "price": "number"
    }
  ]
}
```

**Response:**
```json
{
  "analysis_id": "string",
  "business_profile_id": "string",
  "cost_structure": {
    "fixed_costs": {
      "total": "number",
      "breakdown": [...]
    },
    "variable_costs": {
      "total": "number",
      "breakdown": [...]
    },
    "total_monthly_cost": "number",
    "cost_per_unit": "number"
  },
  "pricing_strategies": [
    {
      "strategy": "value_based|competitive|cost_plus|penetration",
      "recommended_price": "number",
      "rationale": "string",
      "expected_margin": "number",
      "market_position": "premium|mid_market|budget",
      "target_customers": "string"
    }
  ],
  "optimization_opportunities": [
    {
      "area": "string",
      "current_cost": "number",
      "potential_savings": "number",
      "savings_percentage": "number",
      "actions": ["string"],
      "implementation_effort": "low|medium|high",
      "time_to_impact": "string"
    }
  ],
  "break_even_analysis": {
    "current_price": "number",
    "break_even_units": "number",
    "break_even_revenue": "number",
    "margin_of_safety": "number",
    "sensitivity_analysis": {
      "price_increase_10%": {
        "new_break_even": "number",
        "additional_profit": "number"
      }
    }
  },
  "cost_benchmarks": {
    "industry_average": {...},
    "performance": "above_average|average|below_average"
  },
  "created_at": "ISO 8601 datetime"
}
```

#### Get Costing Analysis

Retrieve a specific costing analysis.

```http
GET /api/v1/strategy-advisor/costing/{analysis_id}
```

**Response:**
```json
{
  "analysis_id": "string",
  "business_profile_id": "string",
  "cost_structure": {...},
  "pricing_strategies": [...],
  "optimization_opportunities": [...],
  "break_even_analysis": {...},
  "created_at": "ISO 8601 datetime"
}
```

#### Get Suggestions

Generate business suggestions.

```http
POST /api/v1/strategy-advisor/suggestions
```

**Request Body:**
```json
{
  "business_profile_id": "string (required)",
  "suggestion_types": ["new_opportunities", "partnerships", "market_expansions", "innovation_suggestions"],
  "focus_areas": ["string"],
  "constraints": {
    "max_investment": "number",
    "time_horizon": "string",
    "risk_tolerance": "low|medium|high"
  }
}
```

**Response:**
```json
{
  "business_suggestions": {
    "new_opportunities": [
      {
        "id": "string",
        "title": "string",
        "type": "new_revenue_stream|product_expansion|service_expansion",
        "description": "string",
        "potential_revenue": "number",
        "investment_required": "number",
        "time_to_market": "string",
        "feasibility_score": "number (0-1)",
        "alignment_with_current_business": "number (0-1)",
        "key_advantages": ["string"],
        "implementation_steps": ["string"],
        "risks": ["string"],
        "success_probability": "number (0-1)"
      }
    ],
    "partnership_opportunities": [
      {
        "id": "string",
        "title": "string",
        "type": "strategic_partnership|distribution_partnership|technology_partnership",
        "partner_type": "string",
        "potential_benefits": ["string"],
        "required_commitment": "string",
        "estimated_value": "number",
        "alignment_score": "number (0-1)"
      }
    ],
    "market_expansions": [
      {
        "id": "string",
        "title": "string",
        "type": "market_expansion",
        "target_market": "string",
        "market_size": "number",
        "growth_rate": "string",
        "entry_strategy": "string",
        "required_investments": ["string"],
        "competitive_advantage": "string",
        "timeline": "string",
        "potential_revenue": "number"
      }
    ],
    "innovation_suggestions": [
      {
        "id": "string",
        "title": "string",
        "type": "product_innovation|process_improvement|technology_adoption",
        "description": "string",
        "development_effort": "low|medium|high",
        "potential_impact": "string",
        "required_resources": ["string"],
        "competitive_advantage": "string"
      }
    ]
  },
  "prioritized_recommendations": [
    {
      "rank": "number",
      "suggestion_id": "string",
      "reason": "string",
      "expected_value": "number"
    }
  ],
  "created_at": "ISO 8601 datetime"
}
```

### Analytics Endpoints

#### Get Dashboard Data

Get comprehensive dashboard data.

```http
GET /api/v1/analytics/dashboard?business_profile_id={profile_id}&time_range={range}
```

**Query Parameters:**
- `business_profile_id` (required): Business profile ID
- `time_range` (optional): Time range (e.g., '7d', '30d', '90d', '1y')

**Response:**
```json
{
  "metrics": {
    "revenue": {
      "current": "number",
      "previous": "number",
      "trend": "up|down|stable",
      "change_percentage": "number"
    },
    "customers": {...},
    "conversion_rate": {...},
    "average_order_value": {...}
  },
  "trends": {
    "revenue": [...],
    "customers": [...],
    "conversion_rate": [...]
  },
  "benchmarks": {
    "industry": {...},
    "your_performance": {...}
  },
  "alerts": [...]
}
```

#### Get Metrics

Get specific metrics.

```http
GET /api/v1/analytics/metrics?business_profile_id={profile_id}&metric_names={names}&time_range={range}
```

**Query Parameters:**
- `business_profile_id` (required): Business profile ID
- `metric_names` (required): Comma-separated metric names
- `time_range` (optional): Time range

**Response:**
```json
{
  "metrics": {
    "metric_name": {
      "current": "number",
      "previous": "number",
      "trend": "up|down|stable",
      "historical": [...]
    }
  }
}
```

#### Get Trends

Get trend analysis for a metric.

```http
GET /api/v1/analytics/trends?business_profile_id={profile_id}&metric_name={name}&time_range={range}
```

**Response:**
```json
{
  "metric": "string",
  "time_range": "string",
  "historical_data": [
    {
      "date": "ISO 8601 date",
      "value": "number"
    }
  ],
  "trend": {
    "direction": "up|down|stable",
    "rate": "number",
    "confidence": "number (0-1)",
    "forecast": [...]
  },
  "insights": [
    {
      "type": "string",
      "message": "string",
      "severity": "info|warning|critical"
    }
  ]
}
```

#### Get Benchmarks

Get industry benchmarks.

```http
GET /api/v1/analytics/benchmarks?business_profile_id={profile_id}&industry={industry}
```

**Response:**
```json
{
  "industry": "string",
  "benchmarks": {
    "revenue_growth": {...},
    "profit_margin": {...},
    "customer_acquisition_cost": {...},
    "customer_lifetime_value": {...}
  },
  "your_performance": {
    "revenue_growth": {...},
    "profit_margin": {...},
    "customer_acquisition_cost": {...},
    "customer_lifetime_value": {...}
  },
  "comparison": {
    "above_average": ["string"],
    "below_average": ["string"],
    "at_average": ["string"]
  }
}
```

### Scoring Endpoints

#### Get Current Scores

Get current scores for all categories.

```http
GET /api/v1/scoring/current?business_profile_id={profile_id}
```

**Response:**
```json
{
  "scores": {
    "business_health": {
      "overall_score": "number (0-100)",
      "sub_metrics": {
        "financial_health": "number (0-100)",
        "operational_efficiency": "number (0-100)",
        "customer_satisfaction": "number (0-100)",
        "market_position": "number (0-100)",
        "innovation_readiness": "number (0-100)"
      },
      "trend": "up|down|stable",
      "last_updated": "ISO 8601 datetime"
    },
    "growth_potential": {...},
    "financial_stability": {...},
    "market_position": {...},
    "operational_efficiency": {...},
    "innovation_readiness": {...}
  },
  "overall_score": "number (0-100)",
  "score_level": "excellent|good|fair|poor|critical"
}
```

#### Get Score History

Get historical score data.

```http
GET /api/v1/scoring/history?business_profile_id={profile_id}&score_type={type}&time_range={range}
```

**Query Parameters:**
- `business_profile_id` (required): Business profile ID
- `score_type` (required): Score type (e.g., 'business_health', 'growth_potential')
- `time_range` (optional): Time range

**Response:**
```json
{
  "score_type": "string",
  "time_range": "string",
  "historical_data": [
    {
      "date": "ISO 8601 date",
      "overall_score": "number",
      "sub_metrics": {...}
    }
  ],
  "trend": {
    "direction": "up|down|stable",
    "rate": "number",
    "change": "number"
  }
}
```

#### Get Score Details

Get detailed breakdown of a specific score.

```http
GET /api/v1/scoring/{score_type}?business_profile_id={profile_id}
```

**Response:**
```json
{
  "score_type": "string",
  "overall_score": "number (0-100)",
  "sub_metrics": {
    "metric_name": {
      "score": "number (0-100)",
      "weight": "number (0-1)",
      "value": "number",
      "description": "string"
    }
  },
  "interpretation": {
    "level": "excellent|good|fair|poor|critical",
    "description": "string",
    "recommendations": ["string"]
  },
  "comparison": {
    "industry_average": "number",
    "percentile": "number (0-100)",
    "rank": "string"
  },
  "last_updated": "ISO 8601 datetime"
}
```

#### Recalculate Scores

Trigger score recalculation.

```http
POST /api/v1/scoring/recalculate
```

**Request Body:**
```json
{
  "business_profile_id": "string (required)",
  "score_types": ["business_health", "growth_potential", ...]
}
```

**Response:**
```json
{
  "job_id": "string",
  "status": "pending|processing|completed",
  "estimated_completion": "ISO 8601 datetime"
}
```

#### Get Score Benchmarks

Get score benchmarks.

```http
GET /api/v1/scoring/benchmarks?business_profile_id={profile_id}
```

**Response:**
```json
{
  "benchmarks": {
    "business_health": {
      "industry_average": "number",
      "top_quartile": "number",
      "median": "number",
      "bottom_quartile": "number"
    },
    "growth_potential": {...},
    "financial_stability": {...},
    "market_position": {...},
    "operational_efficiency": {...},
    "innovation_readiness": {...}
  },
  "your_scores": {...},
  "comparison": {
    "above_average": ["string"],
    "below_average": ["string"],
    "at_average": ["string"]
  }
}
```

### Orchestration Endpoints

#### Analyze

Orchestrate analysis across multiple agents.

```http
POST /api/v1/orchestration/analyze
```

**Request Body:**
```json
{
  "business_profile_id": "string (required)",
  "execution_mode": "parallel|sequential|hybrid",
  "agents": ["goal", "growth", "costing", "suggestions"],
  "timeout": "number (seconds)"
}
```

**Response:**
```json
{
  "job_id": "string",
  "status": "pending|processing|completed|failed",
  "agents": [
    {
      "agent": "string",
      "status": "pending|processing|completed|failed",
      "result": {...},
      "execution_time": "number"
    }
  ],
  "aggregated_results": {...},
  "created_at": "ISO 8601 datetime"
}
```

#### Get Status

Get orchestration job status.

```http
GET /api/v1/orchestration/status/{job_id}
```

**Response:**
```json
{
  "job_id": "string",
  "status": "pending|processing|completed|failed",
  "progress": "number (0-100)",
  "agents": [...],
  "aggregated_results": {...},
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "completed_at": "ISO 8601 datetime"
}
```

#### Parallel Execution

Execute agents in parallel.

```http
POST /api/v1/orchestration/parallel
```

**Request Body:**
```json
{
  "business_profile_id": "string (required)",
  "agents": ["goal", "growth", "costing", "suggestions"]
}
```

**Response:**
```json
{
  "job_id": "string",
  "status": "processing",
  "agents": [...],
  "estimated_completion": "ISO 8601 datetime"
}
```

#### Sequential Execution

Execute agents sequentially.

```http
POST /api/v1/orchestration/sequential
```

**Request Body:**
```json
{
  "business_profile_id": "string (required)",
  "agents": ["goal", "growth", "costing", "suggestions"],
  "agent_order": ["goal", "growth", "costing", "suggestions"]
}
```

**Response:**
```json
{
  "job_id": "string",
  "status": "processing",
  "agents": [...],
  "estimated_completion": "ISO 8601 datetime"
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "error": "string",
  "message": "string",
  "details": {...}
}
```

**Common Error Codes:**
- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Invalid or missing token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource doesn't exist
- `422`: Validation Error - Input validation failed
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error
- `503`: Service Unavailable - Service temporarily unavailable

## Rate Limiting

API requests are rate limited:

- **Per User**: 100 requests per minute
- **Per Endpoint**: 50 requests per minute
- **Burst Allowance**: 10 requests per second

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `limit`: Number of items per page (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)

**Response Headers:**
```
X-Total-Count: 150
X-Page-Limit: 20
X-Page-Offset: 0
```

## Webhooks

Webhooks allow real-time notifications:

**Supported Events:**
- `analysis.completed`: Analysis completed
- `goal.created`: Goal created
- `goal.updated`: Goal updated
- `goal.deleted`: Goal deleted
- `score.updated`: Score updated

**Webhook Payload:**
```json
{
  "event": "string",
  "timestamp": "ISO 8601 datetime",
  "data": {...}
}
```

## SDK Examples

### Python

```python
import httpx

client = httpx.AsyncClient(
    base_url="http://localhost:8000/api/v1",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

# Analyze strategy
response = await client.post(
    "/strategy-advisor/analyze",
    json={
        "business_profile_id": "profile-1",
        "analysis_type": "comprehensive"
    }
)
analysis = response.json()

# Get goals
response = await client.get(
    "/strategy-advisor/goals",
    params={"business_profile_id": "profile-1"}
)
goals = response.json()
```

### JavaScript/TypeScript

```typescript
import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});

// Analyze strategy
const analysis = await client.post('/strategy-advisor/analyze', {
  business_profile_id: 'profile-1',
  analysis_type: 'comprehensive'
});

// Get goals
const goals = await client.get('/strategy-advisor/goals', {
  params: { business_profile_id: 'profile-1' }
});
```

## Support

For API support, contact:
- Email: api-support@sme-toolkit.com
- Documentation: https://docs.sme-toolkit.com
- Status Page: https://status.sme-toolkit.com
