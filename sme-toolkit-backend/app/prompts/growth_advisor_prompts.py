"""Prompts for Growth Plan Advisor Agent"""

GROWTH_ADVISOR_PROMPTS = {
    "CREATE_GROWTH_STRATEGY": """Create a comprehensive growth strategy for this business:

Business Context:
{business_context}

Business Model Canvas Data:
{bmc_data}

Market Analysis:
{market_data}

Financial Projections:
{financial_projections}

Current Growth Metrics:
{growth_metrics}

Competitive Landscape:
{competitive_landscape}

Provide a complete growth strategy with:

1. **Strategy Overview**
   - Strategy title
   - Timeframe (e.g., 6 months, 1 year)
   - Overall growth potential score (0-100)
   - Key growth objectives

2. **Growth Opportunities** (3-5 opportunities)
   For each opportunity:
   - Title and type (market_expansion, product_expansion, customer_acquisition, etc.)
   - Potential revenue impact
   - Confidence score (0-100)
   - Required investment
   - Expected ROI
   - Time to market
   - Key actions (3-5 specific steps)
   - Risks
   - Mitigation strategies

3. **Growth Channels** (3-4 channels)
   For each channel:
   - Channel name
   - Priority (high, medium, low)
   - Expected impact
   - Budget allocation
   - Tactics (3-5 specific tactics)

4. **Implementation Roadmap**
   Break into phases (e.g., Phase 1: Foundation, Phase 2: Growth, Phase 3: Scale)
   For each phase:
   - Duration
   - Objectives
   - Deliverables
   - Success criteria

5. **Resource Requirements**
   - Team needed
   - Budget required
   - Tools/technology needed

6. **KPI Targets**
   - Revenue growth target
   - Customer acquisition target
   - Market penetration target

7. **Risk Assessment**
   - High risks with probability and impact
   - Mitigation strategies for each risk

Be specific, realistic, and actionable.""",

    "IDENTIFY_OPPORTUNITIES": """Identify growth opportunities for this business:

Market Data:
{market_data}

Business Data:
{business_data}

Business Model Canvas:
{bmc_data}

Current Performance:
{current_performance}

Identify 5-8 growth opportunities with:

1. **Opportunity Details**
   - Title
   - Type (market_expansion, product_expansion, customer_acquisition, partnership, innovation)
   - Description

2. **Potential Impact**
   - Revenue impact estimate
   - Market size
   - Growth rate

3. **Feasibility Analysis**
   - Feasibility score (0-100)
   - Required investment
   - Time to implement
   - Resource requirements

4. **Strategic Fit**
   - Alignment with current business (0-100)
   - Competitive advantage
   - Differentiation potential

5. **Implementation**
   - Key actions (3-5 steps)
   - Dependencies
   - Timeline

6. **Risk Assessment**
   - Main risks
   - Risk level (low, medium, high)
   - Mitigation strategies

Prioritize opportunities by:
- Potential impact
- Feasibility
- Strategic alignment
- Time to value""",

    "GENERATE_ROADMAP": """Generate a detailed implementation roadmap for this growth strategy:

Growth Strategy:
{strategy}

Growth Opportunities:
{opportunities}

Timeframe: {timeframe}

Available Resources:
{resources}

Create a phased roadmap with:

**Phase 1: Foundation** (e.g., Month 1-2)
- Objectives (2-3 specific goals)
- Key activities (5-7 concrete tasks)
- Deliverables (what will be completed)
- Success criteria (how to measure success)
- Dependencies (what must be completed first)
- Resource allocation

**Phase 2: Growth** (e.g., Month 3-4)
- Objectives
- Key activities
- Deliverables
- Success criteria
- Dependencies
- Resource allocation

**Phase 3: Scale** (e.g., Month 5-6)
- Objectives
- Key activities
- Deliverables
- Success criteria
- Dependencies
- Resource allocation

For each phase, include:
- Timeline with specific dates
- Milestones with target dates
- Key metrics to track
- Potential bottlenecks
- Contingency plans

Ensure roadmap is:
- Realistic and achievable
- Properly sequenced
- Resource-aware
- Measurable with clear milestones""",

    "ASSESS_RISKS": """Assess risks for this growth strategy:

Growth Strategy:
{strategy}

Growth Opportunities:
{opportunities}

Market Conditions:
{market_conditions}

Business Capabilities:
{capabilities}

Provide comprehensive risk assessment:

1. **High Priority Risks** (3-5 risks)
   For each risk:
   - Risk title
   - Risk description
   - Probability (0-100)
   - Impact (low, medium, high, critical)
   - Risk score (probability × impact)
   - Affected areas
   - Early warning indicators
   - Mitigation strategies (2-3 specific actions)
   - Contingency plans

2. **Medium Priority Risks** (3-5 risks)
   - Same structure as above

3. **Low Priority Risks** (2-3 risks)
   - Same structure as above

4. **Risk Categories**
   - Market risks
   - Operational risks
   - Financial risks
   - Competitive risks
   - Technology risks
   - Regulatory risks

5. **Overall Risk Assessment**
   - Overall risk level (low, medium, high, critical)
   - Risk tolerance recommendations
   - Risk monitoring approach
   - Risk mitigation priorities

6. **Risk Management Recommendations**
   - Top 3 risk mitigation priorities
   - Risk monitoring schedule
   - Risk review process

Be thorough and realistic about potential risks.""",

    "CALCULATE_GROWTH_POTENTIAL": """Calculate growth potential for this business:

Business Data:
{business_data}

Market Analysis:
{market_analysis}

Competitive Landscape:
{competitive_landscape}

Financial Performance:
{financial_performance}

Historical Growth:
{historical_growth}

Provide growth potential analysis:

1. **Overall Growth Potential Score** (0-100)
   - Score calculation methodology
   - Key factors influencing score

2. **Market Opportunity Score** (0-100)
   - Market size and growth rate
   - Market accessibility
   - Market saturation level
   - Market trends

3. **Competitive Advantage Score** (0-100)
   - Differentiation factors
   - Barriers to entry
   - Market position
   - Competitive strength

4. **Execution Capability Score** (0-100)
   - Team capabilities
   - Resource availability
   - Operational efficiency
   - Track record

5. **Financial Capacity Score** (0-100)
   - Funding availability
   - Cash flow health
   - Investment readiness
   - Financial stability

6. **Innovation Potential Score** (0-100)
   - R&D investment
   - Innovation culture
   - Technology adoption
   - New product pipeline

7. **Growth Potential Breakdown**
   - By market segment
   - By product/service
   - By geographic region
   - By customer segment

8. **Growth Scenarios**
   - Conservative growth estimate
   - Moderate growth estimate
   - Aggressive growth estimate
   - Assumptions for each scenario

9. **Recommendations**
   - Top 3 growth levers
   - Growth priorities
   - Resource allocation recommendations

Be data-driven and realistic in your assessment."""
}
