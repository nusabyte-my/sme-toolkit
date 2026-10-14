"""Enhanced prompts for Visual Studio Agent with more templates and AI integration"""

from typing import Dict, List, Optional


VISUAL_GENERATION_PROMPT = """Generate a high-quality marketing visual.

Description: {prompt}
Style: {style}
Aspect Ratio: {aspect_ratio}

Requirements:
- Professional quality suitable for marketing materials
- Clear focal point and balanced composition
- Appropriate color palette for the brand/context
- High resolution and crisp details
- No text or watermarks in the image

{template_requirements}

{composition_guidelines}"""


TEMPLATE_REQUIREMENTS = {
    "1:1": """Square format ideal for Instagram/LinkedIn posts.
Composition guidelines:
- Center the subject with balanced margins
- Rule of thirds for dynamic placement
- Ensure subject doesn't touch edges
- Leave breathing room around focal point""",

    "9:16": """Vertical full-screen format for Stories/Reels/TikTok.
Composition guidelines:
- Maximize vertical space efficiently
- Consider mobile thumb zones (bottom 30%)
- Place important CTAs in accessible areas
- Vertical flow guiding the eye upward""",

    "16:9": """Landscape format for web banners/YouTube thumbnails.
Composition guidelines:
- Wide composition with clear visual hierarchy
- Left-to-right reading flow
- Strong focal point in the left or center third
- Balance text and visual elements""",

    "3:4": """Portrait format ideal for print materials/infographics.
Composition guidelines:
- Classic proportions with elegant composition
- Golden ratio principles
- Clear information hierarchy
- Structured vertical flow""",

    "1:2": """Tall infographic format for carousel posts.
Composition guidelines:
- Structure content vertically with clear sections
- Numbered or labeled sections
- Consistent spacing between elements
- Clear data visualization""",
}


STYLE_GUIDES = {
    "Photorealistic": {
        "description": "Professional photography with natural lighting",
        "characteristics": "photorealistic, high detail, professional photography, natural lighting, sharp focus, 8K quality, shallow depth of field when appropriate"
    },
    "Minimalist Vector": {
        "description": "Clean, flat design with simple shapes",
        "characteristics": "minimalist vector art, clean lines, flat design, simple shapes, limited color palette, scalable graphics, modern aesthetic"
    },
    "3D Render": {
        "description": "High quality CGI with realistic materials",
        "characteristics": "3D rendered, high quality CGI, professional lighting, realistic materials, ray tracing, ambient occlusion, 8K resolution"
    },
    "Corporate Memphis": {
        "description": "Flat illustration style with bold colors",
        "characteristics": "corporate memphis style, flat characters, bold colors, geometric shapes, diverse representation, minimal facial features"
    },
    "Oil Painting": {
        "description": "Traditional art style with visible brushstrokes",
        "characteristics": "oil painting style, visible brushstrokes, rich textures, artistic, impasto technique, warm color palette"
    },
    "Cyberpunk": {
        "description": "Futuristic, neon-lit aesthetic",
        "characteristics": "cyberpunk aesthetic, neon colors, futuristic, high tech, dark atmosphere, glowing elements, urban dystopia"
    },
    "Studio Photography": {
        "description": "Professional studio shots with controlled lighting",
        "characteristics": "professional studio photography, controlled lighting, clean background, sharp focus, product photography, white backdrop"
    },
    "Line Art": {
        "description": "Black and white detailed linework",
        "characteristics": "line art illustration, black and white, detailed linework, artistic, clean lines, minimalist aesthetic"
    },
    "Watercolor": {
        "description": "Soft, flowing artistic texture",
        "characteristics": "watercolor painting style, soft edges, flowing colors, artistic texture, paper texture, pastel tones"
    },
    "Flat Design": {
        "description": "Modern flat style with bold colors",
        "characteristics": "flat design, bold colors, simple shapes, vector graphics, modern aesthetic, clean composition"
    },
    "Isometric": {
        "description": "3D isometric view for technical/business visuals",
        "characteristics": "isometric view, 3D illustration, technical drawing style, clean lines, precise angles, professional"
    },
    "Hand Drawn": {
        "description": "Sketch-like, organic feel",
        "characteristics": "hand drawn style, sketch, organic lines, pencil texture, rough edges, artistic illustration"
    },
}


VISUAL_EDIT_PROMPT = """Edit this image according to the following instruction:

Instruction: {instruction}

Guidelines:
- Maintain the overall composition and quality
- Preserve important elements unless specifically asked to change
- Ensure professional appearance
- Keep the edit natural and seamless
- Match the original lighting and color grading"""


PROMPT_ENHANCEMENT_TEMPLATE = """Enhance this visual generation prompt for better image generation results.

Original Prompt: {prompt}
Intended Use: {use_case}
Style Preference: {style}

Provide an enhanced prompt that includes:
1. More descriptive visual elements
2. Specific lighting conditions
3. Composition details
4. Color palette suggestions
5. Technical quality specifications

Return enhanced prompt only, no explanations."""


# Visual category templates
CATEGORY_TEMPLATES = {
    "Product Showcase": """Create a professional product photography shot.

Subject: {product}
Background: {background}
Lighting: Soft studio lighting with subtle highlights
Style: Clean, commercial product photography
Focus: Sharp focus on the product with pleasing bokeh
Details: High resolution, 8K quality, premium feel
Composition: Centered product with balanced negative space""",

    "Social Media Post": """Create an eye-catching social media visual.

Topic: {topic}
Format: Instagram-ready {aspect_ratio} composition
Style: Trendy, engaging visual aesthetic
Elements: Bold colors, clear focal point, shareable quality
Text placement: Leave space for potential overlay text
Vibe: {tone} atmosphere that encourages engagement
Composition: Rule of thirds, dynamic but balanced""",

    "Banner/Header": """Create a professional website banner or header.

Topic: {topic}
Format: Wide {aspect_ratio} landscape banner
Style: Professional, modern business aesthetic
Elements: Clear visual hierarchy, brand-appropriate colors
Layout: Left-to-right flow, balanced composition
Background: Subtle texture or gradient that supports foreground
Impact: Eye-catching but not overwhelming, professional quality""",

    "Infographic Element": """Create a visual element for an infographic.

Subject: {subject}
Style: Clean, informational illustration approach
Elements: Clear, easy-to-understand visual representation
Colors: Accessible color palette, good contrast
Composition: Simple, scalable, works at small sizes
Format: Works as part of larger infographic layout
Clarity: Visually communicate complex information simply""",

    "Event Poster": """Create an eye-catching event poster visual.

Event Type: {event_type}
Theme: {theme}
Style: {style} aesthetic that attracts target audience
Elements: Strong focal point, event-appropriate imagery
Composition: Clear hierarchy, event details area consideration
Atmosphere: Exciting, professional, memorable
Impact: Attention-grabbing but maintains credibility""",

    "Abstract Background": """Create a beautiful abstract background.

Theme: {theme}
Style: {style} abstract art
Colors: Harmonious color palette with good contrast
Elements: Abstract shapes, gradients, textures
Composition: Balanced, non-distracting for content overlay
Use: Suitable as background for {use_case}
Quality: High resolution, professional finish""",
}


# Visual composition rules
COMPOSITION_RULES = {
    "rule_of_thirds": "Place key elements at the intersections of a 3x3 grid",
    "centered": "Center the main subject with symmetrical balance",
    "golden_ratio": "Use the golden ratio for natural, pleasing proportions",
    "leading_lines": "Use lines to guide the viewer's eye to the focal point",
    "negative_space": "Use negative space to create balance and focus",
    "symmetry": "Create symmetrical or mirror-image compositions",
}


def get_style_characteristics(style_name: str) -> str:
    """Get the characteristics for a given style"""
    style_info = STYLE_GUIDES.get(style_name, {})
    return style_info.get("characteristics", style_name)


def get_category_template(category: str, **kwargs) -> str:
    """Get a template for a specific visual category"""
    template = CATEGORY_TEMPLATES.get(category, "")
    if template:
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return template
    return template


def get_aspect_ratio_guidelines(aspect_ratio: str) -> str:
    """Get composition guidelines for a specific aspect ratio"""
    return TEMPLATE_REQUIREMENTS.get(aspect_ratio, "")


def build_enhanced_prompt(
    base_prompt: str,
    style: str,
    aspect_ratio: str,
    category: Optional[str] = None,
    **kwargs
) -> str:
    """Build an enhanced visual prompt with all elements"""
    style_char = get_style_characteristics(style)
    ratio_guidelines = get_aspect_ratio_guidelines(aspect_ratio)
    
    # Start with base prompt
    enhanced_parts = [base_prompt]
    
    # Add style characteristics
    if style_char:
        enhanced_parts.append(f"Style: {style_char}")
    
    # Add aspect ratio guidelines
    if ratio_guidelines:
        enhanced_parts.append(ratio_guidelines)
    
    # Add category template if specified
    if category:
        category_template = get_category_template(category, **kwargs)
        if category_template:
            enhanced_parts.append(category_template)
    
    return " ".join(enhanced_parts)