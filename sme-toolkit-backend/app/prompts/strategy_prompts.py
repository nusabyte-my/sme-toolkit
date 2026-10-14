STRATEGY_PROMPTS = {
    "TIPS": """Provide 5 actionable, specific business tips for:

{context}

Format each tip with:
**Tip Title**: Brief, descriptive title
Description: 2-3 sentences explaining the tip and why it matters

Focus on:
- Immediately implementable actions
- Specific to this business context
- Practical and cost-effective suggestions
- Quick wins with measurable impact""",

    "GROWTH_PLAN": """Create a detailed 6-month growth plan for:

{context}

Structure the plan as:

**Month 1-2: Foundation Phase**
- Key objectives (2-3 specific goals)
- Action items (3-4 concrete tasks)
- Success metrics (how to measure progress)

**Month 3-4: Growth Phase**
- Key objectives
- Action items
- Success metrics

**Month 5-6: Scale Phase**
- Key objectives
- Action items
- Success metrics

**Resources Needed**:
- Budget considerations
- Team/skills requirements
- Tools/technology needs

Be specific to this business, include realistic milestones.""",

    "INSIGHTS": """Analyze this business context and provide critical strategic insights:

{context}

Cover these areas:

**1. Market Positioning Analysis**
- Current market position
- Competitive landscape
- Differentiation opportunities

**2. Strengths & Opportunities**
- Key competitive advantages
- Untapped opportunities
- Growth levers

**3. Risks & Threats**
- Market risks
- Operational risks
- Competitive threats

**4. Strategic Priorities**
- Top 3 priorities for the next quarter
- Resource allocation recommendations
- Key decisions to make

Be honest about challenges while highlighting genuine opportunities.""",

    "CREATIVE": """Create concepts for three visual marketing assets to promote:

{context}

For each asset type, provide:

**1. Infographic Concept**
- Key Message: (one compelling headline)
- Visual Style: (design approach and color palette)
- Content Structure: (what data/info to include)
- Target Impact: (what action should viewers take)

**2. Social Media Graphic Concept**
- Key Message: (attention-grabbing hook)
- Visual Style: (aesthetic and format)
- Platform Optimization: (which platforms, sizing)
- Target Impact: (engagement goal)

**3. Website Banner Ad Concept**
- Key Message: (value proposition headline)
- Visual Style: (design that converts)
- Call-to-Action: (specific CTA text)
- Target Impact: (click-through goal)

Make each concept specific, actionable, and ready for a designer to execute."""
}

ENHANCE_CONTEXT_PROMPT = """Enhance this business context to be more specific and detailed for strategic analysis:

Original: {context}

Add relevant details about:
- Industry/market context
- Business stage and size indicators
- Key challenges or goals mentioned
- Target audience/customer base

Keep the enhanced version to 3-4 sentences while adding valuable specificity."""
