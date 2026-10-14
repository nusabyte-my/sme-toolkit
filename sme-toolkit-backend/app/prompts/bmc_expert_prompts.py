"""Prompts for BMC Expert Agent - Conversational Business Model Canvas discovery"""

BMC_EXPERT_SYSTEM_PROMPT = """You are an expert Business Model Canvas consultant with deep experience helping SMEs develop their business models.

Your role is to:
1. Guide users through a natural conversation to understand their business
2. Ask insightful follow-up questions to gather complete information
3. Identify gaps in their business model thinking
4. Provide suggestions and recommendations

Communication style:
- Professional but friendly
- Ask one question at a time
- Acknowledge and validate user inputs
- Provide brief insights when appropriate
- Keep responses concise (2-4 sentences typically)

You are helping to populate a 9-block Business Model Canvas with:
- Key Partners: Strategic partners, suppliers, alliances
- Key Activities: Core operations and processes
- Key Resources: Essential assets (physical, intellectual, human, financial)
- Value Propositions: Unique value delivered to customers
- Customer Relationships: How you interact with customers
- Channels: How you reach and deliver to customers
- Customer Segments: Target market groups
- Cost Structure: Major costs and expenses
- Revenue Streams: How you generate income

Always respond with valid JSON matching the required schema."""


CONVERSATION_PROMPT = """Based on the conversation history and the user's latest message, continue the discovery process.

Conversation so far:
{conversation_history}

Latest user message: {user_message}

Currently extracted information:
{extracted_info}

Areas still needing information: {missing_areas}

Provide a helpful response that:
1. Acknowledges what they shared (briefly)
2. Provides a quick insight or validation if appropriate
3. Asks ONE natural follow-up question to gather more BMC-relevant information
4. Focus on the missing areas mentioned above

Keep your response conversational and concise (2-4 sentences max).
Do not repeat information already gathered.

Return JSON with:
{{
    "response": "your conversational response",
    "suggestions": ["optional suggestion 1", "optional suggestion 2"],
    "extracted_this_turn": {{"key": "value if any new info was extracted"}}
}}"""


CONTEXT_EXTRACTION_PROMPT = """Analyze this conversation and extract structured business information for a Business Model Canvas.

Conversation:
{conversation}

Extract information for each BMC block where mentioned. For each block, provide:
- items: Array of specific items mentioned or clearly implied
- confidence: 0.0 to 1.0 indicating how confident you are about the extraction

Return JSON with this structure:
{{
    "keyPartners": {{"items": [], "confidence": 0.0}},
    "keyActivities": {{"items": [], "confidence": 0.0}},
    "keyResources": {{"items": [], "confidence": 0.0}},
    "valuePropositions": {{"items": [], "confidence": 0.0}},
    "customerRelationships": {{"items": [], "confidence": 0.0}},
    "channels": {{"items": [], "confidence": 0.0}},
    "customerSegments": {{"items": [], "confidence": 0.0}},
    "costStructure": {{"items": [], "confidence": 0.0}},
    "revenueStreams": {{"items": [], "confidence": 0.0}},
    "metadata": {{
        "industry": "detected industry or null",
        "business_stage": "startup/growth/established or null",
        "key_challenges": ["challenge 1", "challenge 2"],
        "company_name": "detected name or null"
    }},
    "ready_for_wizard": true/false,
    "missing_critical": ["list of critical blocks still missing info"]
}}

Rules:
- Only extract what is explicitly stated or strongly implied
- Set confidence based on how clear the information is
- ready_for_wizard should be true if at least 4 blocks have confidence > 0.5
- missing_critical should list blocks with no info that are essential"""


READINESS_CHECK_PROMPT = """Evaluate if we have enough information to proceed to the BMC wizard.

Current extracted context:
{extracted_context}

Conversation history:
{conversation_history}

Determine:
1. Are there at least 4 BMC blocks with reasonable information?
2. Do we understand the core value proposition?
3. Do we know the target customer segment?
4. Is the business concept clear enough to generate suggestions?

Return JSON:
{{
    "ready": true/false,
    "completeness_score": 0-100,
    "strong_areas": ["blocks with good info"],
    "weak_areas": ["blocks needing more info"],
    "recommendation": "proceed to wizard" OR "continue conversation",
    "suggested_question": "question to ask if not ready, or null"
}}"""


WIZARD_SUGGESTIONS_PROMPT = """Generate AI suggestions for a specific BMC wizard step.

Business context from conversation:
{business_context}

Current wizard step: {step_id}
Step focus: {step_focus}
Fields in this step: {fields}

Current user inputs for this step:
{current_inputs}

Generate helpful, specific suggestions for each field based on the business context.
Suggestions should be:
- Specific to this business (not generic)
- Actionable and concrete
- Building on what we know from the conversation

Return JSON:
{{
    "field_suggestions": {{
        "fieldName": ["suggestion 1", "suggestion 2", "suggestion 3"]
    }},
    "insights": "brief insight about this aspect of their business",
    "considerations": ["thing to consider 1", "thing to consider 2"]
}}"""


INITIAL_GREETING_PROMPT = """Generate a warm, professional greeting to start the BMC discovery conversation.

The user wants to create a Business Model Canvas. Generate a greeting that:
1. Welcomes them briefly
2. Explains you'll help them build their BMC through conversation
3. Asks an open-ended question to get started (about their business idea or current situation)

Keep it concise (3-4 sentences max).

Return JSON:
{{
    "greeting": "your greeting message",
    "initial_question": "your opening question"
}}"""


# Agent-specific prompts for multi-agent system

GROWTH_ANALYSIS_PROMPT = """Analyze the business model for growth potential.

Business Model Canvas:
{bmc_data}

Market Analysis (if available):
{market_analysis}

Analyze:
1. Growth opportunities based on the current model
2. Scaling potential for each revenue stream
3. Expansion possibilities (geographic, product, market)
4. Growth barriers and how to overcome them
5. Quick wins vs long-term growth strategies

Return JSON:
{{
    "growth_opportunities": [
        {{"opportunity": "desc", "potential": "high/medium/low", "timeframe": "short/medium/long", "requirements": ["req1"]}}
    ],
    "scaling_recommendations": ["rec1", "rec2"],
    "growth_score_factors": {{
        "market_size_potential": 0-100,
        "scalability": 0-100,
        "competitive_position": 0-100,
        "resource_readiness": 0-100
    }},
    "priority_actions": ["action1", "action2", "action3"]
}}"""


MARKET_ANALYSIS_PROMPT = """Analyze the market context for this business model.

Business Model Canvas:
{bmc_data}

Business Context:
{business_context}

Analyze:
1. Market size and growth potential
2. Competitive landscape
3. Market positioning opportunities
4. Entry barriers and timing considerations
5. Market readiness assessment

Return JSON:
{{
    "market_size": {{
        "tam": "Total Addressable Market estimate",
        "sam": "Serviceable Addressable Market",
        "som": "Serviceable Obtainable Market"
    }},
    "competitive_analysis": {{
        "direct_competitors": ["competitor1", "competitor2"],
        "indirect_competitors": ["competitor1"],
        "competitive_advantages": ["advantage1", "advantage2"],
        "threats": ["threat1"]
    }},
    "positioning": {{
        "recommended_position": "description",
        "differentiation_factors": ["factor1", "factor2"]
    }},
    "market_readiness_score": 0-100,
    "timing_assessment": "favorable/neutral/challenging",
    "key_market_trends": ["trend1", "trend2"]
}}"""


FINANCIAL_ANALYSIS_PROMPT = """Analyze the financial aspects of this business model.

Business Model Canvas:
{bmc_data}

Revenue Streams: {revenue_streams}
Cost Structure: {cost_structure}

Analyze:
1. Revenue model viability
2. Cost structure efficiency
3. Unit economics potential
4. Break-even considerations
5. Funding/investment readiness

Return JSON:
{{
    "revenue_analysis": {{
        "primary_streams": ["stream1", "stream2"],
        "revenue_model_strength": 0-100,
        "pricing_recommendations": ["rec1"],
        "diversification_opportunities": ["opp1"]
    }},
    "cost_analysis": {{
        "fixed_costs": ["cost1"],
        "variable_costs": ["cost1"],
        "optimization_opportunities": ["opp1"]
    }},
    "financial_health_score": 0-100,
    "funding_readiness": "ready/developing/early",
    "key_financial_metrics_to_track": ["metric1", "metric2"],
    "financial_recommendations": ["rec1", "rec2"]
}}"""


OPERATIONS_ANALYSIS_PROMPT = """Analyze the operational aspects of this business model.

Business Model Canvas:
{bmc_data}

Key Activities: {key_activities}
Key Resources: {key_resources}
Key Partners: {key_partners}

Analyze:
1. Operational efficiency potential
2. Resource allocation optimization
3. Process maturity assessment
4. Partnership effectiveness
5. Execution capability

Return JSON:
{{
    "operations_assessment": {{
        "core_processes": ["process1", "process2"],
        "efficiency_score": 0-100,
        "bottlenecks": ["bottleneck1"],
        "optimization_opportunities": ["opp1"]
    }},
    "resource_analysis": {{
        "critical_resources": ["resource1"],
        "resource_gaps": ["gap1"],
        "allocation_recommendations": ["rec1"]
    }},
    "partnership_assessment": {{
        "key_dependencies": ["dep1"],
        "partnership_opportunities": ["opp1"],
        "risk_factors": ["risk1"]
    }},
    "execution_capability_score": 0-100,
    "operational_priorities": ["priority1", "priority2", "priority3"]
}}"""


IDEATION_PROMPT = """Generate innovative ideas and suggestions for this business model.

Business Model Canvas:
{bmc_data}

Market Analysis:
{market_analysis}

Generate:
1. Innovation opportunities within current model
2. Potential pivot directions
3. New feature/product ideas
4. Differentiation strategies
5. Creative growth hacks

Return JSON:
{{
    "innovation_opportunities": [
        {{"idea": "description", "category": "product/service/process/market", "impact": "high/medium/low", "effort": "high/medium/low"}}
    ],
    "pivot_suggestions": [
        {{"direction": "description", "rationale": "why this makes sense", "risks": ["risk1"]}}
    ],
    "feature_ideas": ["idea1", "idea2", "idea3"],
    "differentiation_strategies": [
        {{"strategy": "description", "competitive_advantage": "what advantage it creates"}}
    ],
    "creative_experiments": [
        {{"experiment": "description", "hypothesis": "what you'll learn", "resources_needed": "minimal/moderate/significant"}}
    ]
}}"""
