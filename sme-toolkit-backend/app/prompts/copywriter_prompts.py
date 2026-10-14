"""Enhanced prompts for Copywriter Agent with more templates and AI integration"""

from typing import Dict, List


FORMAT_INSTRUCTIONS = {
    "Social Media Post": """Requirements for Social Media Post:
- Keep under 280 characters for Twitter compatibility
- Use engaging hooks and emotional triggers
- Include 2-3 relevant hashtags
- End with a clear call-to-action
- Make it shareable and engaging
- Use emoji strategically (1-2 max)
- Structure: Hook → Value → CTA""",

    "Email Newsletter": """Requirements for Email Newsletter:
- Create a compelling subject line (under 50 chars)
- Write a preview text hook (under 100 chars)
- Structure with: Header, Introduction, Body sections, CTA
- Keep paragraphs short (2-3 sentences)
- Include a clear call-to-action button text
- Use personalization tokens: [First Name], [Company]
- Optimize for mobile viewing
- Add P.S. line for urgency""",

    "Blog Post Outline": """Requirements for Blog Post Outline:
- Create an SEO-friendly H1 title (50-60 chars)
- Include a meta description (under 160 chars)
- Provide 4-6 H2 subheadings with key points
- Suggest internal/external linking opportunities
- Include a conclusion with CTA
- Add suggested word count
- Target keywords list
- Reading level estimation""",

    "Ad Headline": """Requirements for Ad Headline:
- Create punchy headlines under 10 words each
- Focus on benefits, not features
- Use power words and emotional triggers
- Include variations: question, statement, command
- Make them A/B testable
- Test emotional vs logical appeals
- Include urgency elements""",

    "Product Description": """Requirements for Product Description:
- Start with a compelling hook
- Focus on benefits over features
- Use sensory language
- Include social proof elements
- Address pain points directly
- Scannable bullet points for features
- Strong closing CTA
- Target 150-200 words""",

    "Cold Email": """Requirements for Cold Email:
- Subject line under 40 chars, curiosity-driven
- Personalized opening line (research-based)
- One-sentence value proposition
- Social proof or credibility element
- Clear, low-friction CTA
- P.S. line for secondary CTA
- Keep under 150 words""",

    "Landing Page Copy": """Requirements for Landing Page Copy:
- Hero headline with subheadline (H2)
- Bullet-pointed benefits (3-5)
- Social proof section ideas
- Objection handling
- Scarcity/urgency element
- Primary and secondary CTAs
- Trust badges placement""",

    "Video Script": """Requirements for Video Script:
- Hook in first 3 seconds
- Scene-by-scene breakdown
- Visual descriptions for each segment
- Audio/narration text
- Timing estimates
- CTA placement and timing
- Platform-specific optimization (TikTok, YouTube, etc.)
- Suggested visuals/overlays""",

    "Press Release": """Requirements for Press Release:
- Attention-grabbing headline
- Dateline (City, State – Date)
- Lead paragraph with 5 Ws (Who, What, When, Where, Why)
- Quote from spokesperson
- Relevant details in inverted pyramid
- Boilerplate company info
- Media contact information""",

    "Case Study": """Requirements for Case Study:
- Compelling title with results
- Client background
- Challenge/problem statement
- Solution implementation
- Measurable results (with data)
- Client testimonial
- Key takeaways
- Strong conclusion""",

    "SEO Content": """Requirements for SEO Content:
- Keyword-optimized H1 (primary keyword)
- Meta description with primary keyword
- H2s with secondary/LSI keywords
- Natural keyword density (1-2%)
- Internal and external links
- Readable structure (short paragraphs, bullet lists)
- FAQ section for long-tail keywords
- Optimized for featured snippets""",

    "SMS Message": """Requirements for SMS Message:
- Under 160 characters
- Clear, immediate value
- Strong CTA with link
- Urgency or exclusivity element
- Personalized greeting
- Opt-out compliance""",
}


COPYWRITER_PERSONAS = {
    "General": "Balanced, professional approach suitable for most contexts",
    "Founder": "Passionate, visionary tone that conveys mission and purpose",
    "Expert": "Authoritative, knowledgeable tone with industry expertise",
    "Friend": "Casual, conversational tone that builds connection",
    "Brand Ambassador": "Enthusiastic, promotional tone that drives engagement",
    "Consultant": "Analytical, solution-oriented tone with strategic insights",
    "Storyteller": "Narrative-driven tone that uses stories to illustrate points",
    "Influencer": "Trendy, relatable tone with social proof emphasis",
}


COPYWRITER_PROMPT = """You are a world-class marketing copywriter with expertise in creating compelling {format} content.

{persona_instruction}

Create {count} distinct variation(s) of {format} content for:

Topic: {topic}
Target Audience: {audience}
Tone: {tone}

{format_instructions}

{variation_instructions}

{ab_testing_instructions}

Make each variation distinct in approach while maintaining the core message and tone."""


def get_variation_instructions(count: int) -> str:
    if count == 1:
        return "Create one polished version."
    return f"""Create {count} distinct variations, clearly labeled:

Option 1: [first variation]
---
Option 2: [second variation]
---
(continue for all {count} options)

Each variation should take a different angle or approach while serving the same goal."""


def get_ab_testing_instructions(ab_mode: bool) -> str:
    if not ab_mode:
        return ""
    return """IMPORTANT: A/B TESTING MODE
You are creating content for A/B testing. Make the variations distinctly different in approach:

Variation A should focus on: Emotional appeal, storytelling, or aspirational messaging
Variation B should focus on: Logical appeal, data-driven, or practical messaging

For each variation, include:
HYPOTHESIS: [What you're testing and why]
APPROACH: [Brief description of the angle taken]

This will help measure which approach resonates better with the audience."""


def get_persona_instruction(persona: str) -> str:
    if not persona or persona == "General":
        return ""
    persona_desc = COPYWRITER_PERSONAS.get(persona, COPYWRITER_PERSONAS["General"])
    return f"""Adopt the persona of a {persona}: {persona_desc}

Write strictly in this voice throughout all content."""


TEMPLATE_SYSTEMS = {
    "AIDA": """Use the AIDA framework:
- Attention: Grab with a powerful hook
- Interest: Build with compelling benefits
- Desire: Create emotional connection
- Action: Drive with clear CTA""",

    "PAS": """Use the PAS framework:
- Problem: Identify and articulate the pain
- Agitate: Make the problem feel urgent
- Solution: Present your product/service as the answer""",

    "StoryBrand": """Use the StoryBrand framework:
- Make the customer the hero
- Define their problem and guide
- Position your brand as the guide
- Provide a clear plan
- Call them to action""",

    "Before-After-Bridge": """Use the Before-After-Bridge framework:
- Before: Describe the current situation (painful)
- After: Describe the ideal future (desirable)
- Bridge: Show how your product gets them there""",
}


# AI Enhancement prompts
TOPIC_ENHANCEMENT_PROMPT = """Enhance this marketing topic for better copy generation.

Original Topic: {topic}

Provide:
1. A clearer, more specific version
2. Key benefits to highlight
3. Pain points to address
4. Target audience refinement
5. Unique selling proposition angle

Return JSON:
{{
    "enhanced_topic": "improved topic statement",
    "key_benefits": ["benefit1", "benefit2"],
    "pain_points": ["pain1", "pain2"],
    "audience_refinement": "more specific audience",
    "usp_angle": "unique angle to emphasize"
}}"""


COPY_ANALYSIS_PROMPT = """Analyze this marketing copy for effectiveness.

Copy:
{copy}

Format: {format}
Target Audience: {audience}

Analyze and provide:
1. Clarity score (1-10) with feedback
2. Engagement potential (1-10) with feedback
3. Persuasion elements used
4. Areas for improvement
5. Suggested variations for testing

Return JSON:
{{
    "clarity_score": 8,
    "clarity_feedback": "detailed feedback",
    "engagement_score": 7,
    "engagement_feedback": "detailed feedback",
    "persuasion_elements": ["element1", "element2"],
    "improvements": ["improvement1", "improvement2"],
    "suggested_variations": ["variation1", "variation2"]
}}"""


# Template-specific prompts
EMAIL_TEMPLATE_PROMPT = """Generate an email using this template structure:

Subject Line: [curiosity-driven, under 40 chars]
Preview: [hook, under 100 chars]

Hi [First Name],

[Personalized opening line based on research]

[One-sentence value proposition]

[Social proof/credibility element]

[Clear CTA with single action]

P.S. [Secondary CTA or urgency element]

Best regards,
[Name]"""


SOCIAL_MEDIA_TEMPLATE_PROMPT = """Generate social media content using this structure:

[Hook line - grabs attention immediately]

[Value/benefit in 1-2 sentences]

[Social proof or authority element]

[Clear CTA with emoji]

[2-3 relevant hashtags]"""


LANDING_PAGE_TEMPLATE_PROMPT = """Generate landing page copy using this structure:

HEADLINE: [Main benefit-focused headline]
SUBHEADLINE: [Supporting benefit or social proof]

BENEFITS:
• [Benefit 1 with result-oriented language]
• [Benefit 2 with emotional appeal]
• [Benefit 3 addressing pain point]

SOCIAL PROOF: [Testimonial, number of users, or trust badge]

OBJECTION HANDLING: [Address common concern]

URGENCY: [Limited time/quantity element]

PRIMARY CTA: [Strong action verb + benefit]
SECONDARY CTA: [Alternative lower-friction action]"""
