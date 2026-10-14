"""Enhanced prompts for Video Agent with more templates and AI integration"""

from typing import Dict, List, Optional


VIDEO_SCRIPT_PROMPT = """Create a detailed visual prompt for AI video generation.

Topic: {topic}
Platform: {platform}

Requirements:
- Describe the visual scene in detail (setting, lighting, camera angle, movement)
- Specify the subject and their actions clearly
- Include mood and atmosphere descriptions
- Keep it concise (2-3 sentences maximum)
- Optimize for text-to-video model (focus on visuals, not audio/dialogue)

Platform Guidelines:
{platform_guidelines}

Generate a single, powerful visual prompt."""


PLATFORM_GUIDELINES = {
    "YouTube": {
        "description": "Long-form video platform, educational or entertainment content",
        "aspect_ratio": "16:9 landscape",
        "style": "longer shots, professional quality, educational or engaging content, good for tutorials and storytelling",
        "duration": "3-10 minutes typical"
    },
    "TikTok": {
        "description": "Short-form vertical video platform, trending and viral content",
        "aspect_ratio": "9:16 vertical",
        "style": "fast-paced, trendy, attention-grabbing first frame, music-driven, quick cuts",
        "duration": "15-60 seconds"
    },
    "Instagram Reels": {
        "description": "Short-form vertical video on Instagram, lifestyle and aesthetic content",
        "aspect_ratio": "9:16 vertical",
        "style": "polished aesthetic, lifestyle-focused, visually striking, smooth transitions",
        "duration": "15-90 seconds"
    },
    "Social Story": {
        "description": "Ephemeral vertical content for social stories",
        "aspect_ratio": "9:16 vertical",
        "style": "casual but engaging, quick payoff, behind-the-scenes feel, authentic",
        "duration": "5-30 seconds"
    },
    "TV Commercial": {
        "description": "Professional advertisement content, brand-focused",
        "aspect_ratio": "16:9 landscape",
        "style": "cinematic quality, brand-focused, professional production, strong call-to-action",
        "duration": "15-60 seconds"
    },
    "LinkedIn Video": {
        "description": "Professional networking platform video content",
        "aspect_ratio": "1:1 or 16:9",
        "style": "professional, business-focused, educational, thought leadership",
        "duration": "1-5 minutes"
    },
    "YouTube Shorts": {
        "description": "YouTube's short-form vertical video format",
        "aspect_ratio": "9:16 vertical",
        "style": "fast-paced, entertaining, educational snippets, high retention focus",
        "duration": "15-60 seconds"
    }
}


STORYBOARD_PROMPT = """Break down this video concept into a storyboard with {scene_count} distinct scenes.

Script/Concept: {script}

For each scene, provide:
1. description: A 5-word summary of the scene action
2. prompt: A detailed visual prompt for video generation (35-40 words)
   - Include: camera angle, lighting, subject, action, mood
   - Be specific enough for AI video generation

Requirements:
- Scenes should flow logically as a narrative
- Each scene should be visually distinct
- Maintain consistent style across scenes
- Each prompt should work standalone for video generation

Return a JSON array of scene objects with "description" and "prompt" keys."""


VIDEO_CATEGORIES = {
    "Product Showcase": """Create a product showcase video.

Product: {product}
Key Features: {features}
Brand Tone: {tone}

Scene Ideas:
- Opening shot with product hero shot
- Feature highlights with smooth transitions
- Lifestyle usage demonstration
- Closing with branding and CTA

Focus on: Product quality, key benefits, professional presentation""",

    "Tutorial/How-To": """Create an educational tutorial video.

Topic: {topic}
Difficulty: {difficulty}
Target Audience: {audience}

Scene Ideas:
- Hook with problem statement
- Step-by-step demonstration
- Clear explanations and visual aids
- Summary and call-to-action

Focus on: Clarity, pacing, educational value, retention""",

    "Brand Story": """Create an engaging brand story video.

Brand: {brand}
Core Message: {message}
Emotional Hook: {hook}

Scene Ideas:
- Emotional opening with brand values
- Story arc with conflict/resolution
- Customer testimonials or success stories
- Inspiring conclusion with brand presence

Focus on: Emotional connection, brand identity, storytelling""",

    "Social Media Trend": """Create a trendy social media video.

Trend: {trend}
Platform: {platform}
Viral Elements: {elements}

Scene Ideas:
- Attention-grabbing opening (0-2 seconds)
- Trend-based action or content
- Surprise or twist element
- Clear engagement prompt

Focus on: Speed, entertainment, shareability, platform optimization""",

    "Testimonial/Review": """Create a compelling testimonial video.

Product/Service: {product}
Customer Type: {customer_type}
Key Benefit: {benefit}

Scene Ideas:
- Customer introduction
- Problem/solution narrative
- Authentic usage demonstration
- Strong recommendation

Focus on: Authenticity, trust, credibility, relatable""",

    "Event Promo": """Create an exciting event promotion video.

Event: {event}
Key Details: {details}
Call to Action: {cta}

Scene Ideas:
- High-energy opening
- Event highlights and features
- Social proof or speakers
- Urgent CTA with date/time

Focus on: Excitement, urgency, clarity, attendance motivation""",

    "Behind the Scenes": """Create an engaging behind-the-scenes video.

Subject: {subject}
Purpose: {purpose}
Tone: {tone}

Scene Ideas:
- Candid opening with team
- Process or workflow showcase
- Personal moments and interactions
- Authentic closing

Focus on: Authenticity, transparency, connection, personality"""
}


STYLE_FILTERS = {
    "Cinematic": {
        "description": "Film-like quality with dramatic lighting",
        "characteristics": "cinematic look, film grain, dramatic lighting, wide aspect ratio feel, shallow depth of field, smooth camera movement"
    },
    "Photorealistic": {
        "description": "Natural, lifelike appearance",
        "characteristics": "photorealistic, natural lighting, high detail, lifelike, realistic textures, natural color grading"
    },
    "3D Animation": {
        "description": "Computer-generated 3D animation style",
        "characteristics": "3D animated style, smooth rendering, CGI quality, vibrant colors, fluid motion, polished 3D aesthetic"
    },
    "Cyberpunk": {
        "description": "Futuristic neon-lit aesthetic",
        "characteristics": "cyberpunk aesthetic, neon lights, futuristic, dark atmosphere, glowing elements, urban dystopia, high-tech vibe"
    },
    "Vintage Film": {
        "description": "Retro film look with warm tones",
        "characteristics": "vintage film look, warm tones, slight grain, nostalgic feel, film scratches, classic color palette"
    },
    "Drone Shot": {
        "description": "Aerial perspective from drone footage",
        "characteristics": "aerial drone perspective, smooth movement, wide establishing shot, cinematic flight path, high vantage point"
    },
    "Studio Lighting": {
        "description": "Professional commercial lighting setup",
        "characteristics": "professional studio lighting, clean background, commercial quality, perfect exposure, product-focused lighting"
    },
    "Motion Graphics": {
        "description": "Animated graphics and text overlays",
        "characteristics": "motion graphics style, animated text and shapes, clean typography, smooth transitions, modern design elements"
    },
    "Handheld Documentary": {
        "description": "Authentic documentary-style footage",
        "characteristics": "handheld camera movement, documentary style, authentic feel, natural lighting, raw and genuine aesthetic"
    },
    "Slow Motion": {
        "description": "Dramatic slow-motion footage",
        "characteristics": "slow motion, high frame rate feel, dramatic emphasis, smooth slow playback, cinematic time-stretch"
    },
    "Time Lapse": {
        "description": "Accelerated time passage footage",
        "characteristics": "time lapse, accelerated motion, smooth speed ramping, day-to-night transitions, dynamic time compression"
    },
    "Stop Motion": {
        "description": "Frame-by-frame animation style",
        "characteristics": "stop motion animation, jerky but deliberate movement, handcrafted feel, frame-by-frame aesthetic, playful style"
    }
}


CAMERA_MOVEMENTS = {
    "Static": "Camera remains stationary",
    "Pan": "Horizontal camera movement left to right or right to left",
    "Tilt": "Vertical camera movement up or down",
    "Zoom In": "Gradual closer shot",
    "Zoom Out": "Gradual wider shot",
    "Dolly In": "Camera moves forward toward subject",
    "Dolly Out": "Camera moves backward from subject",
    "Tracking": "Camera follows subject movement",
    "Crane Up": "Camera rises vertically",
    "Crane Down": "Camera lowers vertically",
    "Handheld": "Natural, slightly shaky movement for authenticity"
}


LIGHTING_SETUPS = {
    "Natural": "Natural daylight, soft shadows, realistic outdoor or window-lit indoor scenes",
    "Studio": "Professional studio lighting, controlled and balanced, perfect for products",
    "Dramatic": "High contrast, strong shadows, moody and atmospheric lighting",
    "Neon": "Colored neon lights, vibrant and glowing, urban nightlife aesthetic",
    "Golden Hour": "Warm golden light during sunrise or sunset, soft and flattering",
    "Low Key": "Dark scenes with focused lighting, dramatic shadows and highlights",
    "High Key": "Bright, evenly lit scenes, minimal shadows, clean and cheerful",
    "Backlit": "Light source behind subject, creating silhouettes or rim lighting effects",
    "Practical": "Light sources visible in scene (lamps, screens), realistic and atmospheric",
    "Rembrandt": "Classic portrait lighting with triangular light patch on cheek"
}


SCRIPT_ENHANCEMENT_PROMPT = """Enhance this video script for better AI video generation.

Original Script: {script}
Platform: {platform}
Target Duration: {duration}

Provide an enhanced script that includes:
1. More specific visual descriptions
2. Clear camera movements and angles
3. Lighting specifications
4. Mood and atmosphere details
5. Appropriate pacing for the platform

Return enhanced script only, no explanations."""


def get_platform_guidelines(platform: str) -> str:
    """Get guidelines for a specific platform"""
    platform_info = PLATFORM_GUIDELINES.get(platform, {})
    if isinstance(platform_info, dict):
        return f"Aspect Ratio: {platform_info.get('aspect_ratio', '16:9')}\nStyle: {platform_info.get('style', 'engaging visual content')}\nDuration: {platform_info.get('duration', '30-60 seconds')}"
    return platform_info


def get_style_characteristics(style: str) -> str:
    """Get the characteristics for a given style"""
    style_info = STYLE_FILTERS.get(style, {})
    if isinstance(style_info, dict):
        return style_info.get("characteristics", style)
    return style_info


def get_category_template(category: str, **kwargs) -> str:
    """Get a template for a specific video category"""
    template = VIDEO_CATEGORIES.get(category, "")
    if template:
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return template
    return template


def build_video_prompt(
    topic: str,
    platform: str,
    category: Optional[str] = None,
    style: Optional[str] = None,
    **kwargs
) -> str:
    """Build an enhanced video prompt with all elements"""
    parts = [topic]
    
    # Add platform guidelines
    platform_guide = get_platform_guidelines(platform)
    if platform_guide:
        parts.append(f"Platform: {platform}")
    
    # Add style characteristics
    if style:
        style_char = get_style_characteristics(style)
        if style_char:
            parts.append(f"Style: {style_char}")
    
    # Add category template if specified
    if category:
        category_template = get_category_template(category, **kwargs)
        if category_template:
            parts.append(category_template)
    
    return " ".join(parts)