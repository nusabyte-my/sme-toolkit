from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.auth import get_current_user
from app.schemas.prompt_genie import (
    PromptTemplate,
    PromptCategory,
    PromptOptimizationRequest,
    PromptOptimizationResponse,
    PromptFromTemplateRequest,
    PromptGenerationResponse,
    PromptLibraryResponse,
    PromptAnalytics,
    PromptFeedback
)
from app.agents.orchestrator import get_orchestrator

router = APIRouter()


PREDEFINED_CATEGORIES: List[PromptCategory] = [
    PromptCategory(id="copywriting", name="Copywriting", description="Marketing and content writing prompts", icon="✍️", color="from-purple-500 to-pink-500"),
    PromptCategory(id="visual", name="Visual Design", description="Image generation and design prompts", icon="🎨", color="from-blue-500 to-cyan-500"),
    PromptCategory(id="video", name="Video Creation", description="Video script and storyboard prompts", icon="🎬", color="from-red-500 to-orange-500"),
    PromptCategory(id="business", name="Business Strategy", description="BMC and strategy prompts", icon="💼", color="from-emerald-500 to-teal-500"),
    PromptCategory(id="coding", name="Coding", description="Code generation and debugging prompts", icon="💻", color="from-violet-500 to-purple-500"),
    PromptCategory(id="research", name="Research", description="Analysis and research prompts", icon="🔬", color="from-amber-500 to-yellow-500"),
]

PREDEFINED_TEMPLATES: List[PromptTemplate] = [
    PromptTemplate(
        id="social_media_post",
        name="Social Media Post",
        description="Generate engaging social media content",
        category_id="copywriting",
        template="""You are a world-class social media marketer.

Create a {{platform}} post for {{product/service}} targeting {{target_audience}}.

Tone: {{tone}}
Goal: {{goal}}
Key points to include: {{key_points}}

Format requirements:
- Include {{num_hashtags}} relevant hashtags
- Keep it under {{max_chars}} characters
- Include a compelling hook in the first sentence
- Add a clear call-to-action

Return JSON:
{{
    "post": "the social media post content",
    "hashtags": ["hashtag1", "hashtag2"],
    "hook": "the opening hook",
    "cta": "the call-to-action"
}}""",
        variables=[
            {"name": "platform", "type": "select", "label": "Platform", "required": True, "options": ["Instagram", "LinkedIn", "Twitter", "Facebook", "TikTok"]},
            {"name": "product/service", "type": "text", "label": "Product/Service", "required": True, "placeholder": "What are you promoting?"},
            {"name": "target_audience", "type": "text", "label": "Target Audience", "required": True, "placeholder": "Who are you targeting?"},
            {"name": "tone", "type": "select", "label": "Tone", "required": True, "options": ["Professional", "Casual", "Excited", "Witty", "Urgent", "Empathetic"], "default_value": "Professional"},
            {"name": "goal", "type": "select", "label": "Goal", "required": True, "options": ["Engagement", "Sales", "Brand Awareness", "Traffic", "Lead Generation"]},
            {"name": "key_points", "type": "text", "label": "Key Points", "required": False, "placeholder": "Any specific points to include?"},
            {"name": "num_hashtags", "type": "number", "label": "Number of Hashtags", "required": True, "default_value": 5},
            {"name": "max_chars", "type": "number", "label": "Max Characters", "required": True, "default_value": 280}
        ],
        tags=["social", "marketing", "engagement"],
        is_public=True,
        usage_count=12500,
        rating=4.7,
        created_at="2024-01-01T00:00:00Z"
    ),
    PromptTemplate(
        id="email_campaign",
        name="Email Campaign",
        description="Create high-converting email campaigns",
        category_id="copywriting",
        template="""You are an expert email copywriter with deep knowledge of email marketing best practices.

Create an email campaign for {{product/service}} with the goal of {{goal}}.

Target Audience: {{target_audience}}
Tone: {{tone}}

Email Requirements:
- Subject line (5 variations for A/B testing)
- Preview text
- Email body (max {{word_count}} words)
- Clear call-to-action
- {{num_bullets}} bullet points highlighting benefits

Psychological triggers to use: {{triggers}}

Return JSON:
{{
    "subject_lines": ["subject1", "subject2", "subject3", "subject4", "subject5"],
    "preview_text": "preview text",
    "email_body": "full email content with HTML",
    "cta": "the call-to-action",
    "benefits": ["benefit1", "benefit2"]
}}""",
        variables=[
            {"name": "product/service", "type": "text", "label": "Product/Service", "required": True},
            {"name": "goal", "type": "select", "label": "Goal", "required": True, "options": ["Sales", "Lead Generation", "Webinar Signup", "Product Launch", "Newsletter"]},
            {"name": "target_audience", "type": "text", "label": "Target Audience", "required": True},
            {"name": "tone", "type": "select", "label": "Tone", "required": True, "options": ["Professional", "Friendly", "Urgent", "Persuasive", "Educational"], "default_value": "Professional"},
            {"name": "word_count", "type": "number", "label": "Max Word Count", "required": True, "default_value": 300},
            {"name": "num_bullets", "type": "number", "label": "Number of Benefits", "required": True, "default_value": 3},
            {"name": "triggers", "type": "multiselect", "label": "Psychological Triggers", "required": False, "options": ["Scarcity", "Urgency", "Social Proof", "Authority", "Reciprocity", "FOMO"]}
        ],
        tags=["email", "marketing", "conversion"],
        is_public=True,
        usage_count=8700,
        rating=4.8,
        created_at="2024-01-01T00:00:00Z"
    ),
    PromptTemplate(
        id="image_generation",
        name="AI Image Generation",
        description="Detailed prompts for AI image generation",
        category_id="visual",
        template="""You are an expert prompt engineer for AI image generation models like Midjourney, DALL-E, and Stable Diffusion.

Create a detailed image generation prompt for:

Subject: {{subject}}
Style: {{style}}
Art Style: {{art_style}}
Composition: {{composition}}
Lighting: {{lighting}}
Color Palette: {{color_palette}}

Additional Elements:
- Mood/Atmosphere: {{mood}}
- Camera Angle: {{camera_angle}}
- Depth of Field: {{depth_of_field}}

Include negative prompts to avoid unwanted elements.

Return JSON:
{{
    "main_prompt": "the primary detailed prompt",
    "negative_prompt": "negative prompts",
    "style_modifiers": ["modifier1", "modifier2"],
    "technical_params": {{
        "aspect_ratio": "16:9",
        "quality": "high"
    }}
}}""",
        variables=[
            {"name": "subject", "type": "text", "label": "Subject", "required": True, "placeholder": "What should be in the image?"},
            {"name": "style", "type": "select", "label": "Style", "required": True, "options": ["Photorealistic", "Illustration", "Digital Art", "Watercolor", "Oil Painting", "Anime", "3D Render"], "default_value": "Photorealistic"},
            {"name": "art_style", "type": "text", "label": "Art Style", "required": False, "placeholder": "e.g., cyberpunk, minimalist, baroque"},
            {"name": "composition", "type": "select", "label": "Composition", "required": True, "options": ["Center Frame", "Rule of Thirds", "Symmetrical", "Asymmetrical", "Golden Ratio"], "default_value": "Rule of Thirds"},
            {"name": "lighting", "type": "select", "label": "Lighting", "required": True, "options": ["Natural", "Studio", "Dramatic", "Soft", "Backlit", "Golden Hour"], "default_value": "Natural"},
            {"name": "color_palette", "type": "text", "label": "Color Palette", "required": False, "placeholder": "e.g., warm tones, monochrome, vibrant"},
            {"name": "mood", "type": "text", "label": "Mood/Atmosphere", "required": False, "placeholder": "e.g., mysterious, joyful, melancholic"},
            {"name": "camera_angle", "type": "select", "label": "Camera Angle", "required": True, "options": ["Eye Level", "High Angle", "Low Angle", "Bird's Eye", "Worm's Eye"], "default_value": "Eye Level"},
            {"name": "depth_of_field", "type": "select", "label": "Depth of Field", "required": True, "options": ["Shallow", "Deep", "Medium"], "default_value": "Medium"}
        ],
        tags=["image", "ai", "visual"],
        is_public=True,
        usage_count=15300,
        rating=4.6,
        created_at="2024-01-01T00:00:00Z"
    ),
    PromptTemplate(
        id="video_script",
        name="Video Script",
        description="Professional video script generation",
        category_id="video",
        template="""You are an expert video scriptwriter.

Create a {{video_type}} video script for {{topic}}.

Video Details:
- Duration: {{duration}}
- Target Audience: {{target_audience}}
- Tone: {{tone}}
- Platform: {{platform}}

Script Requirements:
- Hook in the first 3 seconds
- Clear structure (hook, body, conclusion)
- Engaging dialogue or narration
- Visual descriptions for each scene
- Call-to-action at the end

Format the script with scene headers, action lines, and dialogue.

Return JSON:
{{
    "title": "video title",
    "hook": "opening hook",
    "scenes": [
        {{
            "scene_number": 1,
            "time": "0:00-0:05",
            "visual": "visual description",
            "audio": "narration/dialogue",
            "notes": "directional notes"
        }}
    ],
    "cta": "call to action",
    "estimated_word_count": 1234
}}""",
        variables=[
            {"name": "video_type", "type": "select", "label": "Video Type", "required": True, "options": ["Promotional", "Educational", "Tutorial", "Story", "Interview", "Review"]},
            {"name": "topic", "type": "text", "label": "Topic", "required": True},
            {"name": "duration", "type": "select", "label": "Duration", "required": True, "options": ["15-30 seconds", "30-60 seconds", "1-3 minutes", "3-5 minutes", "5-10 minutes"]},
            {"name": "target_audience", "type": "text", "label": "Target Audience", "required": True},
            {"name": "tone", "type": "select", "label": "Tone", "required": True, "options": ["Professional", "Casual", "Excited", "Authoritative", "Friendly"], "default_value": "Professional"},
            {"name": "platform", "type": "select", "label": "Platform", "required": True, "options": ["YouTube", "TikTok", "Instagram Reels", "LinkedIn", "Website"], "default_value": "YouTube"}
        ],
        tags=["video", "script", "content"],
        is_public=True,
        usage_count=9100,
        rating=4.5,
        created_at="2024-01-01T00:00:00Z"
    ),
    PromptTemplate(
        id="bmc_analysis",
        name="BMC Analysis",
        description="Analyze Business Model Canvas",
        category_id="business",
        template="""You are a Business Model Canvas expert.

Analyze this Business Model Canvas data:

BMC Data:
{{bmc_data}}

Provide insights on:
1. Strengths and weaknesses
2. Growth opportunities
3. Risk factors
4. Improvement recommendations
5. Innovation potential

For each BMC block, provide specific, actionable recommendations.

Return JSON:
{{
    "overall_assessment": "summary of the business model",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "growth_opportunities": [
        {{"opportunity": "description", "potential": "high/medium/low", "timeframe": "short/medium/long"}}
    ],
    "risks": [
        {{"risk": "description", "mitigation": "how to mitigate"}}
    ],
    "block_recommendations": {{
        "valuePropositions": ["rec1", "rec2"],
        "customerSegments": ["rec1"]
    }},
    "innovation_score": 75,
    "next_steps": ["step1", "step2", "step3"]
}}""",
        variables=[
            {"name": "bmc_data", "type": "text", "label": "BMC Data", "required": True, "placeholder": "Paste your BMC data here"}
        ],
        tags=["bmc", "business", "strategy"],
        is_public=True,
        usage_count=4200,
        rating=4.9,
        created_at="2024-01-01T00:00:00Z"
    ),
    PromptTemplate(
        id="code_review",
        name="Code Review",
        description="Comprehensive code review and suggestions",
        category_id="coding",
        template="""You are an expert code reviewer and software architect.

Review the following code:

Language: {{language}}
Code:
{{code}}

Review Criteria:
- Code quality and readability
- Performance considerations
- Security vulnerabilities
- Best practices adherence
- Potential bugs or edge cases
- Documentation needs

Provide:
1. Overall assessment (1-10 score)
2. Specific issues found
3. Suggestions for improvement
4. Refactored version (if applicable)
5. Best practices to follow

Return JSON:
{{
    "overall_score": 8,
    "assessment": "summary of code quality",
    "issues": [
        {{"type": "bug/performance/security/style", "severity": "critical/high/medium/low", "description": "issue description", "location": "line X", "suggestion": "how to fix"}}
    ],
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "refactored_code": "improved version (if needed)",
    "best_practices": ["practice1", "practice2"]
}}""",
        variables=[
            {"name": "language", "type": "select", "label": "Programming Language", "required": True, "options": ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "C#", "PHP"]},
            {"name": "code", "type": "text", "label": "Code", "required": True, "placeholder": "Paste your code here"}
        ],
        tags=["code", "review", "quality"],
        is_public=True,
        usage_count=6700,
        rating=4.4,
        created_at="2024-01-01T00:00:00Z"
    ),
    PromptTemplate(
        id="market_research",
        name="Market Research",
        description="Comprehensive market research and analysis",
        category_id="research",
        template="""You are an expert market researcher.

Conduct market research for:

Product/Service: {{product_service}}
Industry: {{industry}}
Target Market: {{target_market}}
Geography: {{geography}}

Research Focus Areas:
1. Market size and growth (TAM, SAM, SOM)
2. Competitive landscape
3. Customer segments and personas
4. Market trends and opportunities
5. Entry barriers and challenges
6. Pricing analysis
7. Distribution channels

Return JSON:
{{
    "market_size": {{
        "tam": "Total Addressable Market",
        "tam_value": "$X billion",
        "sam": "Serviceable Addressable Market",
        "sam_value": "$X billion",
        "som": "Serviceable Obtainable Market",
        "som_value": "$X million",
        "growth_rate": "X% CAGR"
    }},
    "competitors": [
        {{"name": "competitor", "market_share": "X%", "strengths": [], "weaknesses": []}}
    ],
    "customer_segments": [
        {{"segment": "name", "size": "X%", "characteristics": [], "pain_points": []}}
    ],
    "market_trends": ["trend1", "trend2"],
    "opportunities": ["opportunity1", "opportunity2"],
    "entry_barriers": ["barrier1", "barrier2"],
    "pricing_analysis": {{
        "average_price": "$X",
        "price_range": "$X-$Y",
        "pricing_models": ["model1", "model2"]
    }},
    "recommendations": ["rec1", "rec2", "rec3"]
}}""",
        variables=[
            {"name": "product_service", "type": "text", "label": "Product/Service", "required": True},
            {"name": "industry", "type": "text", "label": "Industry", "required": True},
            {"name": "target_market", "type": "text", "label": "Target Market", "required": True},
            {"name": "geography", "type": "text", "label": "Geography", "required": False, "placeholder": "e.g., Global, US, Europe, Asia"}
        ],
        tags=["research", "market", "analysis"],
        is_public=True,
        usage_count=5800,
        rating=4.7,
        created_at="2024-01-01T00:00:00Z"
    ),
]


@router.get("/library", response_model=PromptLibraryResponse)
async def get_prompt_library(
    category: str = None,
    search: str = None,
    current_user: str = Depends(get_current_user)
):
    """
    Get the prompt template library.

    - **category**: Filter by category (copywriting, visual, video, business, coding, research)
    - **search**: Search by name or tags
    """
    templates = PREDEFINED_TEMPLATES.copy()

    if category:
        templates = [t for t in templates if t.category_id == category]

    if search:
        search_lower = search.lower()
        templates = [
            t for t in templates
            if search_lower in t.name.lower()
            or search_lower in t.description.lower()
            or any(search_lower in tag.lower() for tag in t.tags)
        ]

    return PromptLibraryResponse(
        success=True,
        templates=templates,
        categories=PREDEFINED_CATEGORIES,
        total=len(templates)
    )


@router.get("/templates/{template_id}", response_model=PromptTemplate)
async def get_template(
    template_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get a specific prompt template by ID.
    """
    for template in PREDEFINED_TEMPLATES:
        if template.id == template_id:
            return template

    raise HTTPException(status_code=404, detail="Template not found")


@router.post("/optimize", response_model=PromptOptimizationResponse)
async def optimize_prompt(
    request: PromptOptimizationRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Optimize a prompt for better AI results.

    - **original_prompt**: The prompt to optimize
    - **goal**: Optimization goal (clarity, creativity, specificity, conciseness, comprehensive)
    - **target_model**: Target AI model (optional)
    - **context**: Additional context (optional)
    - **output_format**: Desired output format (optional)
    - **constraints**: List of constraints (optional)
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="prompt_genie",
        data={
            "action": "optimize_prompt",
            "original_prompt": request.original_prompt,
            "goal": request.goal,
            "target_model": request.target_model,
            "context": request.context,
            "output_format": request.output_format,
            "constraints": request.constraints
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return PromptOptimizationResponse(
        success=True,
        optimized_prompt=result.get("optimized_prompt"),
        improvements=result.get("improvements", []),
        reasoning=result.get("reasoning"),
        variations=result.get("variations", [])
    )


@router.post("/generate-from-template", response_model=PromptGenerationResponse)
async def generate_from_template(
    request: PromptFromTemplateRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate a prompt from a template by filling in variables.

    - **template_id**: ID of the template to use
    - **variable_values**: Dictionary of variable names to values
    - **optimize**: Whether to optimize the generated prompt
    - **optimization_goal**: Optimization goal if optimize=true
    """
    template = None
    for t in PREDEFINED_TEMPLATES:
        if t.id == request.template_id:
            template = t
            break

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="prompt_genie",
        data={
            "action": "generate_from_template",
            "template": template,
            "variable_values": request.variable_values
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    prompt = result.get("prompt")

    if request.optimize:
        optimization_result = await orchestrator.invoke(
            agent_name="prompt_genie",
            data={
                "action": "optimize_prompt",
                "original_prompt": prompt,
                "goal": request.optimization_goal or "comprehensive"
            }
        )

        if optimization_result.get("success"):
            prompt = optimization_result.get("optimized_prompt")

    return PromptGenerationResponse(
        success=True,
        prompt=prompt,
        template_used=template
    )


@router.get("/categories", response_model=List[PromptCategory])
async def get_categories(
    current_user: str = Depends(get_current_user)
):
    """
    Get all prompt categories.
    """
    return PREDEFINED_CATEGORIES


@router.post("/feedback")
async def submit_feedback(
    template_id: str,
    rating: int,
    comment: str = None,
    helpful: bool = True,
    current_user: str = Depends(get_current_user)
):
    """
    Submit feedback on a prompt template.

    - **template_id**: ID of the template
    - **rating**: Rating 1-5
    - **comment**: Optional comment
    - **helpful**: Whether the prompt was helpful
    """
    for template in PREDEFINED_TEMPLATES:
        if template.id == template_id:
            template.usage_count += 1

            if template.rating is None:
                template.rating = rating
            else:
                template.rating = (template.rating * (template.usage_count - 1) + rating) / template.usage_count

            return {"success": True, "message": "Feedback recorded"}

    raise HTTPException(status_code=404, detail="Template not found")
