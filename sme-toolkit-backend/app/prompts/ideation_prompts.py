"""Enhanced prompts for Ideation Agent - Robust ideation with templates and frameworks"""

# Template Framework Instructions
SCAMPER_TEMPLATE = """Use the SCAMPER method for ideation:
- Substitute: What can be replaced?
- Combine: What can be combined together?
- Adapt: What can be adapted or modified?
- Modify: What can be modified or changed?
- Put to another use: What other uses exist?
- Eliminate: What can be removed?
- Reverse: What can be rearranged or reversed?"""

MIND_MAP_TEMPLATE = """Use Mind Mapping for ideation:
- Start with the central topic in the center
- Branch out into main categories
- Add sub-branches for related ideas
- Connect ideas with lines showing relationships
- Use colors and symbols for visual organization
- Expand outward with free associations"""

SWOT_TEMPLATE = """Use SWOT Analysis for ideation:
- Strengths: Internal advantages to leverage
- Weaknesses: Internal areas to improve
- Opportunities: External possibilities to pursue
- Threats: External risks to address
- Generate ideas that maximize strengths and opportunities
- Create strategies to overcome weaknesses and threats"""

BLUE_OCEAN_TEMPLATE = """Use Blue Ocean Strategy for ideation:
- Identify current industry boundaries
- Find uncontested market space
- Make competition irrelevant
- Create and capture new demand
- Break the value-cost trade-off
- Pursue differentiation and low cost simultaneously"""

LEAN_STARTUP_TEMPLATE = """Use Lean Startup principles for ideation:
- Build-Measure-Learn cycle
- Minimum Viable Product (MVP) approach
- Validated learning through experiments
- Pivot or persevere decisions
- Customer development process
- Iterative product development"""

DESIGN_THINKING_TEMPLATE = """Use Design Thinking for ideation:
- Empathize: Understand user needs
- Define: Clearly articulate the problem
- Ideate: Generate diverse solutions
- Prototype: Create tangible representations
- Test: Validate with users
- Iterate based on feedback"""

FIRST_PRINCIPLES_TEMPLATE = """Use First Principles Thinking for ideation:
- Break down the problem into fundamental truths
- Question assumptions and beliefs
- Rebuild solutions from the ground up
- Focus on what is absolutely necessary
- Eliminate unnecessary complexity
- Innovate from core principles"""

REVERSE_ENGINEERING_TEMPLATE = """Use Reverse Engineering for ideation:
- Study successful solutions in other domains
- Deconstruct what makes them work
- Adapt core principles to your context
- Identify transferable patterns
- Apply cross-industry insights
- Innovate through analogy"""

# Ideation Prompts
BRAINSTORM_PROMPT = """Generate innovative ideas using {template} framework.

Topic: {topic}
Industry: {industry}
Target Audience: {target_audience}
Constraints: {constraints}
Innovation Level: {innovation_level}
Quantity: {quantity}

Template Framework:
{template_instructions}

Generate {quantity} diverse, actionable ideas following these requirements:
1. Each idea should be unique and distinct
2. Consider the {innovation_level} innovation level
3. Address the constraints provided
4. Focus on the target audience needs
5. Apply industry-specific knowledge
6. Include implementation considerations

For each idea, provide:
- title: Concise, memorable name
- description: Detailed explanation (2-3 sentences)
- category: Idea category (product, service, process, marketing, business model)
- impact: Expected impact (high/medium/low)
- effort: Implementation effort (high/medium/low)
- innovation_type: Type of innovation (incremental/disruptive/radical)
- feasibility_score: Feasibility score (0-100)
- novelty_score: Novelty score (0-100)
- value_score: Value score (0-100)
- tags: Relevant tags (3-5)
- implementation_steps: 3-5 actionable steps
- risks: 2-3 potential risks
- metrics: 2-3 success metrics

Return JSON:
{{
    "ideas": [
        {{
            "id": "unique_id",
            "title": "Idea Title",
            "description": "Detailed description",
            "category": "category",
            "impact": "high/medium/low",
            "effort": "high/medium/low",
            "innovation_type": "incremental/disruptive/radical",
            "feasibility_score": 85,
            "novelty_score": 70,
            "value_score": 90,
            "tags": ["tag1", "tag2", "tag3"],
            "implementation_steps": ["step1", "step2", "step3"],
            "risks": ["risk1", "risk2"],
            "metrics": ["metric1", "metric2"]
        }}
    ],
    "insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"]
}}"""

TREND_ANALYSIS_PROMPT = """Analyze current and emerging trends relevant to the topic.

Topic: {topic}
Industry: {industry}
Context: {context}

Identify and analyze trends that could impact this topic:

For each trend, provide:
- trend: Name of the trend
- description: Clear description of the trend (2-3 sentences)
- relevance_score: Relevance to topic (0-100)
- opportunities: 2-3 opportunities this trend presents
- threats: 2-3 threats or challenges from this trend
- timeframe: Trend maturity (emerging/growing/mature/declining)

Focus on:
1. Technology trends
2. Market trends
3. Consumer behavior trends
4. Regulatory trends
5. Competitive trends

Return JSON:
{{
    "trends": [
        {{
            "trend": "Trend Name",
            "description": "Description",
            "relevance_score": 85,
            "opportunities": ["opp1", "opp2"],
            "threats": ["threat1"],
            "timeframe": "emerging"
        }}
    ],
    "insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"]
}}"""

COMPETITIVE_ANALYSIS_PROMPT = """Analyze the competitive landscape and identify strategic opportunities.

Topic: {topic}
Industry: {industry}
Context: {context}

Analyze competitors and provide strategic insights:

For each competitor (real or representative), provide:
- competitor: Competitor name or type
- strengths: 3-5 key strengths
- weaknesses: 3-5 key weaknesses
- strategies: 3-5 strategies to differentiate from them
- opportunities: 2-3 opportunities to exploit their weaknesses

Provide analysis on:
1. Direct competitors
2. Indirect competitors
3. Potential new entrants
4. Substitute solutions

Return JSON:
{{
    "competitors": [
        {{
            "competitor": "Competitor Name",
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "strategies": ["strategy1", "strategy2"],
            "opportunities": ["opp1", "opp2"]
        }}
    ],
    "insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"]
}}"""

MARKET_OPPORTUNITY_PROMPT = """Identify market opportunities for the given topic.

Topic: {topic}
Industry: {industry}
Target Audience: {target_audience}
Context: {context}

Identify specific market opportunities:

For each opportunity, provide:
- opportunity: Clear description of the opportunity
- market_size: Estimated market size (TAM/SAM/SOM format preferred)
- growth_rate: Expected growth rate
- competition_level: Competition level (low/medium/high)
- barriers_to_entry: 2-4 barriers to entry
- success_factors: 3-5 factors critical for success

Focus on:
1. Underserved segments
2. Emerging needs
3. Gaps in current offerings
4. New market spaces
5. Partnership opportunities

Return JSON:
{{
    "opportunities": [
        {{
            "opportunity": "Opportunity description",
            "market_size": "$X billion (TAM), $Y billion (SAM), $Z million (SOM)",
            "growth_rate": "X% CAGR",
            "competition_level": "low/medium/high",
            "barriers_to_entry": ["barrier1", "barrier2"],
            "success_factors": ["factor1", "factor2", "factor3"]
        }}
    ],
    "insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"]
}}"""

PRODUCT_INNOVATION_PROMPT = """Generate innovative product ideas using {template} framework.

Topic: {topic}
Industry: {industry}
Target Audience: {target_audience}
Context: {context}
Constraints: {constraints}
Innovation Level: {innovation_level}

Template Framework:
{template_instructions}

Generate {quantity} innovative product ideas:

For each product idea, provide:
- id: Unique identifier
- title: Product name
- description: Detailed product description (3-4 sentences)
- category: Product category
- impact: Market impact (high/medium/low)
- effort: Development effort (high/medium/low)
- innovation_type: Innovation type (incremental/disruptive/radical)
- feasibility_score: Feasibility (0-100)
- novelty_score: Novelty (0-100)
- value_score: Value proposition (0-100)
- tags: Relevant tags (3-5)
- implementation_steps: Development roadmap (4-5 steps)
- risks: Development and market risks (2-3)
- metrics: Success metrics (2-3)

Focus on:
1. User pain points
2. Market gaps
3. Technological possibilities
4. Business model innovation

Return JSON:
{{
    "ideas": [{{idea_objects}}],
    "insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"]
}}"""

BUSINESS_MODEL_INNOVATION_PROMPT = """Generate innovative business model ideas using {template} framework.

Topic: {topic}
Industry: {industry}
Context: {context}
Innovation Level: {innovation_level}

Template Framework:
{template_instructions}

Generate {quantity} innovative business model ideas:

For each business model idea, provide:
- id: Unique identifier
- title: Business model name
- description: Detailed description (3-4 sentences)
- category: Business model type (subscription, marketplace, platform, freemium, etc.)
- impact: Market impact (high/medium/low)
- effort: Implementation effort (high/medium/low)
- innovation_type: Innovation type (incremental/disruptive/radical)
- feasibility_score: Feasibility (0-100)
- novelty_score: Novelty (0-100)
- value_score: Value proposition (0-100)
- tags: Relevant tags (3-5)
- implementation_steps: Implementation steps (4-5)
- risks: Business risks (2-3)
- metrics: Success metrics (2-3)

Consider:
1. Revenue model innovation
2. Cost structure innovation
3. Value proposition innovation
4. Customer relationship innovation
5. Channel innovation
6. Partnership innovation

Return JSON:
{{
    "ideas": [{{idea_objects}}],
    "insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"]
}}"""

IDEA_ENHANCEMENT_PROMPT = """Enhance these ideas with deeper analysis and AI insights.

Original Ideas:
{ideas}

Context:
{topic}
{industry}
{target_audience}

For each idea, provide enhanced analysis:
1. Refine the description for clarity and impact
2. Validate feasibility score with reasoning
3. Assess market potential more accurately
4. Identify synergies between ideas
5. Suggest combination opportunities
6. Highlight risks and mitigation strategies

Return enhanced JSON with the same structure, including:
- Enhanced descriptions
- Updated scores with reasoning
- Synergy notes between related ideas
- Combination suggestions where applicable
- Risk mitigation strategies"""

# Helper functions
def get_template_instructions(template: str) -> str:
    """Get template instructions based on template name"""
    templates = {
        "scamper": SCAMPER_TEMPLATE,
        "mind_map": MIND_MAP_TEMPLATE,
        "swot": SWOT_TEMPLATE,
        "blue_ocean": BLUE_OCEAN_TEMPLATE,
        "lean_startup": LEAN_STARTUP_TEMPLATE,
        "design_thinking": DESIGN_THINKING_TEMPLATE,
        "first_principles": FIRST_PRINCIPLES_TEMPLATE,
        "reverse_engineering": REVERSE_ENGINEERING_TEMPLATE
    }
    return templates.get(template, BRAINSTORM_PROMPT)


def get_action_prompt(action: str) -> str:
    """Get the appropriate prompt for a given action"""
    prompts = {
        "brainstorm": BRAINSTORM_PROMPT,
        "analyze_trends": TREND_ANALYSIS_PROMPT,
        "competitive_analysis": COMPETITIVE_ANALYSIS_PROMPT,
        "market_opportunity": MARKET_OPPORTUNITY_PROMPT,
        "product_innovation": PRODUCT_INNOVATION_PROMPT,
        "business_model_innovation": BUSINESS_MODEL_INNOVATION_PROMPT
    }
    return prompts.get(action, BRAINSTORM_PROMPT)


def build_ideation_prompt(
    action: str,
    topic: str,
    template: str = None,
    industry: str = None,
    target_audience: str = None,
    constraints: list = None,
    innovation_level: str = "incremental",
    quantity: int = 10,
    context: dict = None
) -> str:
    """Build a complete ideation prompt with all parameters"""
    base_prompt = get_action_prompt(action)
    template_instructions = get_template_instructions(template) if template else ""
    
    constraints_str = ", ".join(constraints) if constraints else "None"
    context_str = str(context) if context else "{}"
    
    return base_prompt.format(
        topic=topic,
        template=template or "brainstorming",
        template_instructions=template_instructions,
        industry=industry or "general",
        target_audience=target_audience or "general",
        constraints=constraints_str,
        innovation_level=innovation_level,
        quantity=quantity,
        context=context_str
    )
