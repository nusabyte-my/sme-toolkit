"""Prompts for Goal Advisor Agent"""

GOAL_ADVISOR_PROMPTS = {
    "GENERATE_SMART_GOALS": """Generate 3-5 SMART goals for this business context:

{business_context}

Business Model Canvas Data:
{bmc_data}

Current Business Metrics:
{metrics}

Resource Constraints:
{resources}

For each goal, provide:
1. **Title**: Clear, concise goal title
2. **Description**: Detailed description of the goal
3. **Category**: financial, operational, market, or innovation
4. **SMART Criteria**:
   - Specific: What exactly will be accomplished?
   - Measurable: How will progress be tracked?
   - Achievable: Is this realistic given current resources?
   - Relevant: How does this align with business objectives?
   - Time-bound: What is the deadline?
5. **Priority**: high, medium, or low
6. **Estimated Completion**: Target completion date
7. **Key Milestones**: 2-4 intermediate milestones with target dates
8. **Required Resources**: Resources needed to achieve the goal
9. **Potential Obstacles**: Possible challenges and how to overcome them
10. **Success Metrics**: How to measure success

Ensure goals are:
- Specific and clearly defined
- Measurable with concrete metrics
- Achievable given current resources
- Relevant to business growth
- Time-bound with clear deadlines
- Aligned with Business Model Canvas elements""",

    "ALIGN_WITH_BMC": """Analyze how this goal aligns with the Business Model Canvas:

Goal: {goal_title}
Description: {goal_description}

Business Model Canvas Data:
{bmc_data}

Provide:
1. **Aligned Blocks**: List of BMC blocks this goal supports (e.g., revenue_streams, customer_segments, value_propositions)
2. **Alignment Score**: 0-100 score indicating how well the goal aligns with the BMC
3. **Alignment Rationale**: Explanation of why this goal aligns with these blocks
4. **Gaps**: Any BMC blocks that are not addressed by this goal
5. **Recommendations**: Suggestions to improve alignment with BMC

Consider:
- How the goal impacts revenue streams
- Which customer segments benefit
- How value propositions are enhanced
- Required key activities and resources
- Channel implications
- Cost structure considerations""",

    "TRACK_PROGRESS": """Analyze progress for this goal:

Goal: {goal_title}
Current Progress: {progress}%
Target Deadline: {deadline}
Milestones: {milestones}
Success Metrics: {success_metrics}
Current Metrics: {current_metrics}

Provide:
1. **Overall Progress Assessment**: On track, ahead, or behind schedule
2. **Milestone Progress**: Status of each milestone
3. **Metric Analysis**: How current metrics compare to targets
4. **Progress Score**: 0-100 score indicating progress quality
5. **Recommendations**: Specific actions to improve progress
6. **Risk Assessment**: Risks to achieving the goal
7. **Adjustment Suggestions**: If behind, suggest realistic adjustments

Be honest about progress while providing constructive feedback.""",

    "RECOMMEND_GOALS": """Generate goal recommendations based on business context:

Business Context:
{business_context}

Business Model Canvas Data:
{bmc_data}

Current Goals:
{current_goals}

Business Stage: {business_stage}
Industry: {industry}

Provide 3-5 goal recommendations with:
1. **Goal Title**: Clear, actionable goal
2. **Description**: What the goal aims to achieve
3. **Category**: financial, operational, market, or innovation
4. **Priority**: high, medium, or low
5. **Rationale**: Why this goal is important for this business
6. **Expected Impact**: Potential business impact
7. **Feasibility**: How achievable is this goal (0-100)
8. **Dependencies**: Other goals or resources this depends on
9. **Timeline**: Suggested timeframe

Focus on:
- Goals that address current business challenges
- Opportunities for growth and improvement
- Goals that complement existing goals
- Priorities based on business stage
- Industry-specific considerations""",

    "CALCULATE_FEASIBILITY": """Calculate feasibility score for this goal:

Goal: {goal_title}
Description: {goal_description}
Required Resources: {required_resources}
Timeline: {timeline}

Available Resources:
{available_resources}

Current Business Metrics:
{metrics}

Historical Goal Performance:
{historical_performance}

Provide:
1. **Feasibility Score**: 0-100 score indicating how achievable this goal is
2. **Resource Analysis**: Assessment of resource availability
3. **Timeline Analysis**: Is the timeline realistic?
4. **Risk Factors**: Key risks that could prevent success
5. **Success Probability**: Estimated probability of success (0-100)
6. **Recommendations**: How to improve feasibility
7. **Alternative Approaches**: If feasibility is low, suggest alternatives

Consider:
- Resource constraints and availability
- Historical performance on similar goals
- Market conditions and external factors
- Team capacity and capabilities
- Financial constraints
- Time required vs. time available"""
}
