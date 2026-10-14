"""Prompts for Costing Advisor Agent"""

COSTING_ADVISOR_PROMPTS = {
    "ANALYZE_COST_STRUCTURE": """Analyze the cost structure for this business:

Financial Data:
{financial_data}

Cost Breakdown:
{cost_breakdown}

Business Model Canvas:
{bmc_data}

Operational Metrics:
{operational_metrics}

Provide comprehensive cost structure analysis:

1. **Fixed Costs Analysis**
   - Total fixed costs per month
   - Breakdown by category:
     * Category name
     * Amount
     * Percentage of total fixed costs
   - Fixed cost trends (increasing, stable, decreasing)
   - Fixed cost efficiency assessment

2. **Variable Costs Analysis**
   - Total variable costs per month
   - Breakdown by category:
     * Category name
     * Amount
     * Percentage of total variable costs
   - Variable cost per unit
   - Variable cost trends
   - Variable cost efficiency assessment

3. **Total Cost Summary**
   - Total monthly costs
   - Cost per unit
   - Cost breakdown percentages
   - Cost trends over time

4. **Cost Structure Assessment**
   - Fixed vs variable cost ratio
   - Cost efficiency score (0-100)
   - Cost competitiveness vs industry
   - Cost optimization opportunities

5. **Cost Drivers**
   - Primary cost drivers
   - Secondary cost drivers
   - Cost driver analysis

6. **Recommendations**
   - Top 3 cost optimization opportunities
   - Cost reduction strategies
   - Cost control measures

Be thorough and data-driven in your analysis.""",

    "DEVELOP_PRICING_STRATEGY": """Develop pricing strategies for this business:

Cost Data:
{cost_data}

Market Pricing Data:
{market_pricing}

Competitor Pricing:
{competitor_pricing}

Business Model Canvas:
{bmc_data}

Value Proposition:
{value_proposition}

Provide 2-3 pricing strategies:

**Strategy 1: Value-Based Pricing**
- Recommended price
- Rationale (why this price based on value)
- Expected margin
- Market position (premium, mid-market, budget)
- Target customers
- Competitive advantage
- Implementation considerations

**Strategy 2: Competitive Pricing**
- Recommended price
- Rationale (how it compares to competitors)
- Expected margin
- Market position
- Target customers
- Competitive positioning
- Implementation considerations

**Strategy 3: Cost-Plus Pricing** (optional)
- Recommended price
- Cost breakdown
- Markup percentage
- Expected margin
- Market position
- Target customers
- Implementation considerations

For each strategy, include:
- Price sensitivity analysis
- Volume projections
- Revenue projections
- Risk assessment
- Implementation timeline

Provide final recommendation with:
- Recommended strategy
- Justification
- Expected outcomes
- Implementation steps""",

    "IDENTIFY_OPTIMIZATION_OPPORTUNITIES": """Identify cost optimization opportunities:

Cost Data:
{cost_data}

Operational Data:
{operational_data}

Industry Benchmarks:
{industry_benchmarks}

Business Processes:
{business_processes}

Identify 5-8 optimization opportunities with:

1. **Opportunity Details**
   - Area (procurement, operations, marketing, technology, etc.)
   - Current cost
   - Potential savings
   - Savings percentage
   - Implementation effort (low, medium, high)
   - Time to impact

2. **Actions Required**
   - Specific actions to implement (3-5 steps)
   - Resources needed
   - Timeline
   - Dependencies

3. **Impact Analysis**
   - Financial impact
   - Operational impact
   - Risk level
   - ROI estimate

4. **Implementation Considerations**
   - Implementation complexity
   - Change management requirements
   - Training needs
   - Technology requirements

5. **Prioritization**
   - Priority score (0-100)
   - Quick win potential
   - Strategic importance
   - Resource requirements

Prioritize opportunities by:
- Potential savings
- Implementation effort
- Time to impact
- Strategic importance
- Risk level

Be specific and actionable in your recommendations.""",

    "BREAK_EVEN_ANALYSIS": """Perform break-even analysis:

Cost Data:
{cost_data}

Pricing Data:
{pricing}

Revenue Data:
{revenue_data}

Provide comprehensive break-even analysis:

1. **Current Break-Even Point**
   - Break-even units
   - Break-even revenue
   - Break-even timeframe
   - Current volume vs break-even

2. **Cost Structure Analysis**
   - Fixed costs
   - Variable costs per unit
   - Contribution margin
   - Contribution margin ratio

3. **Break-Even Scenarios**
   - Current price break-even
   - Price increase scenarios:
     * +5% price increase
     * +10% price increase
     * +15% price increase
   - Price decrease scenarios:
     * -5% price decrease
     * -10% price decrease

4. **Margin of Safety**
   - Current margin of safety
   - Margin of safety percentage
   - Safety assessment (adequate, low, critical)

5. **Sensitivity Analysis**
   - Price sensitivity
   - Cost sensitivity
   - Volume sensitivity
   - Combined sensitivity scenarios

6. **Profitability Analysis**
   - Profit at current volume
   - Profit at break-even
   - Profit at target volume
   - Profit projections

7. **Recommendations**
   - Pricing recommendations
   - Cost reduction opportunities
   - Volume improvement strategies
   - Risk mitigation

Provide clear, actionable insights.""",

    "CALCULATE_PROFITABILITY_METRICS": """Calculate profitability metrics:

Financial Data:
{financial_data}

Revenue Data:
{revenue_data}

Cost Data:
{cost_data}

Business Model Canvas:
{bmc_data}

Provide comprehensive profitability analysis:

1. **Gross Profitability**
   - Gross profit
   - Gross profit margin
   - Gross profit trend
   - Industry comparison

2. **Operating Profitability**
   - Operating profit
   - Operating profit margin
   - Operating profit trend
   - Industry comparison

3. **Net Profitability**
   - Net profit
   - Net profit margin
   - Net profit trend
   - Industry comparison

4. **Profitability Ratios**
   - Return on sales
   - Return on assets
   - Return on investment
   - Return on equity

5. **Unit Economics**
   - Revenue per unit
   - Cost per unit
   - Profit per unit
   - Contribution margin per unit

6. **Customer Economics**
   - Revenue per customer
   - Cost per customer
   - Profit per customer
   - Customer lifetime value

7. **Profitability Trends**
   - Monthly/quarterly trends
   - Year-over-year comparison
   - Trend analysis
   - Forecast

8. **Profitability Assessment**
   - Overall profitability score (0-100)
   - Strengths
   - Weaknesses
   - Improvement opportunities

9. **Recommendations**
   - Top 3 profitability improvement strategies
   - Cost optimization priorities
   - Revenue enhancement opportunities
   - Strategic recommendations

Be thorough and provide actionable insights."""
}
