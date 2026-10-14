"""Prompts for Business Suggestion Agent"""

BUSINESS_SUGGESTION_PROMPTS = {
    "SUGGEST_OPPORTUNITIES": """Suggest new business opportunities for this business:

Business Context:
{business_context}

Market Data:
{market_data}

Business Model Canvas:
{bmc_data}

Current Capabilities:
{capabilities}

Industry Analysis:
{industry_analysis}

Suggest 5-8 new business opportunities with:

1. **Opportunity Details**
   - Title
   - Type (new_revenue_stream, product_expansion, service_expansion, market_expansion)
   - Description
   - Potential revenue (annual estimate)
   - Investment required
   - Time to market

2. **Feasibility Analysis**
   - Feasibility score (0-100)
   - Alignment with current business (0-100)
   - Resource requirements
   - Technical complexity
   - Market readiness

3. **Strategic Fit**
   - How it leverages existing capabilities
   - Synergies with current business
   - Competitive advantage
   - Differentiation potential

4. **Implementation**
   - Key advantages (3-5 points)
   - Implementation steps (5-7 steps)
   - Timeline
   - Dependencies
   - Resource allocation

5. **Risk Assessment**
   - Main risks (3-5 risks)
   - Risk level (low, medium, high)
   - Mitigation strategies
   - Success probability (0-100)

6. **Market Analysis**
   - Market size
   - Market growth rate
   - Competition level
   - Entry barriers

Prioritize opportunities by:
- Potential revenue
- Feasibility
- Strategic alignment
- Time to value
- Risk level

Be innovative yet realistic in your suggestions.""",

    "IDENTIFY_PARTNERSHIPS": """Identify partnership opportunities for this business:

Business Profile:
{business_profile}

Business Model Canvas:
{bmc_data}

Current Capabilities:
{capabilities}

Market Position:
{market_position}

Identify 4-6 partnership opportunities with:

1. **Partnership Details**
   - Title
   - Type (strategic, distribution, technology, marketing, supply_chain)
   - Partner type (logistics, technology, finance, etc.)
   - Description

2. **Potential Benefits**
   - Specific benefits (3-5 points)
   - Revenue impact
   - Cost savings
   - Market expansion
   - Capability enhancement

3. **Partnership Structure**
   - Required commitment
   - Partnership model
   - Duration
   - Terms overview

4. **Strategic Value**
   - Alignment score (0-100)
   - Strategic importance
   - Competitive advantage
   - Market positioning impact

5. **Implementation**
   - Estimated value (annual)
   - Implementation timeline
   - Key actions (3-5 steps)
   - Resource requirements
   - Success metrics

6. **Risk Assessment**
   - Potential risks (2-3 risks)
   - Risk level
   - Mitigation strategies
   - Exit considerations

7. **Partner Criteria**
   - Ideal partner characteristics
   - Partner requirements
   - Evaluation criteria

Prioritize partnerships by:
- Strategic value
- Potential benefits
- Implementation complexity
- Risk level
- Time to value

Be specific and actionable in your recommendations.""",

    "RECOMMEND_EXPANSION": """Recommend market expansion strategies:

Market Data:
{market_data}

Current Capabilities:
{capabilities}

Business Model Canvas:
{bmc_data}

Competitive Position:
{competitive_position}

Recommend 3-5 market expansion strategies with:

1. **Expansion Details**
   - Title
   - Type (geographic, demographic, vertical, horizontal)
   - Target market
   - Market size
   - Growth rate

2. **Market Analysis**
   - Market characteristics
   - Customer segments
   - Competition level
   - Entry barriers
   - Regulatory considerations

3. **Expansion Strategy**
   - Entry strategy (direct, partnership, acquisition, franchise, etc.)
   - Required investments (3-5 categories)
   - Timeline
   - Phased approach

4. **Competitive Advantage**
   - Existing advantages to leverage
   - Differentiation in new market
   - Value proposition adaptation
   - Market positioning

5. **Implementation**
   - Key actions (5-7 steps)
   - Resource requirements
   - Team needs
   - Technology requirements
   - Marketing approach

6. **Financial Projections**
   - Potential revenue
   - Investment required
   - ROI estimate
   - Break-even timeline
   - Profitability timeline

7. **Risk Assessment**
   - Main risks (3-5 risks)
   - Risk level
   - Mitigation strategies
   - Contingency plans

8. **Success Factors**
   - Critical success factors
   - Key performance indicators
   - Milestones
   - Success criteria

Prioritize expansions by:
- Market potential
- Strategic fit
- Feasibility
- Risk level
- Time to profitability

Be thorough and realistic in your analysis.""",

    "PROPOSE_INNOVATIONS": """Propose innovation ideas for this business:

Business Context:
{business_context}

Market Trends:
{trends}

Current Products/Services:
{current_products}

Customer Feedback:
{customer_feedback}

Competitive Landscape:
{competitive_landscape}

Propose 4-6 innovation ideas with:

1. **Innovation Details**
   - Title
   - Type (product, service, process, business_model, technology)
   - Description
   - Problem it solves
   - Value proposition

2. **Impact Analysis**
   - Potential impact (revenue, efficiency, customer satisfaction)
   - Market differentiation
   - Competitive advantage
   - Customer value

3. **Development Assessment**
   - Development effort (low, medium, high)
   - Technical complexity
   - Required resources (team, technology, budget)
   - Timeline
   - Development phases

4. **Market Fit**
   - Market demand
   - Customer need validation
   - Market readiness
   - Adoption potential

5. **Implementation**
   - Required resources (3-5 categories)
   - Development approach
   - Testing strategy
   - Launch plan
   - Go-to-market strategy

6. **Competitive Advantage**
   - Unique value proposition
   - Differentiation factors
   - Barriers to competition
   - First-mover advantage

7. **Risk Assessment**
   - Development risks
   - Market risks
   - Technology risks
   - Mitigation strategies

8. **Success Metrics**
   - Key success indicators
   - Measurement approach
   - Success criteria
   - ROI metrics

Prioritize innovations by:
- Potential impact
- Feasibility
- Strategic alignment
- Customer value
- Competitive advantage

Be creative yet practical in your suggestions.""",

    "CALCULATE_FEASIBILITY": """Calculate feasibility score for this suggestion:

Suggestion:
{suggestion}

Available Resources:
{resources}

Business Capabilities:
{capabilities}

Market Conditions:
{market_conditions}

Historical Performance:
{historical_performance}

Provide comprehensive feasibility analysis:

1. **Overall Feasibility Score** (0-100)
   - Score calculation methodology
   - Key factors

2. **Resource Feasibility** (0-100)
   - Financial resources
   - Human resources
   - Technical resources
   - Time resources
   - Assessment

3. **Technical Feasibility** (0-100)
   - Technology requirements
   - Technical complexity
   - Existing capabilities
   - Technology gap
   - Assessment

4. **Market Feasibility** (0-100)
   - Market demand
   - Market readiness
   - Competition level
   - Customer acceptance
   - Assessment

5. **Operational Feasibility** (0-100)
   - Process requirements
   - Operational capacity
   - Integration complexity
   - Change management
   - Assessment

6. **Financial Feasibility** (0-100)
   - Investment required
   - ROI potential
   - Cash flow impact
   - Financial risk
   - Assessment

7. **Risk Assessment**
   - Major risks (3-5 risks)
   - Risk level
   - Probability
   - Impact
   - Mitigation strategies

8. **Success Probability** (0-100)
   - Overall probability
   - Key success factors
   - Critical dependencies
   - Success timeline

9. **Recommendations**
   - Feasibility improvement strategies
   - Risk mitigation priorities
   - Implementation approach
   - Alternative approaches if needed

Be thorough and realistic in your assessment."""
}
