from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.schemas.copywriter import (
    CopywriterRequest,
    CopywriterResponse,
    OptionsResponse,
    FormatOption,
    PersonaOption,
    TemplateSystemOption
)
from app.agents.orchestrator import get_orchestrator
from app.prompts.copywriter_prompts import (
    FORMAT_INSTRUCTIONS,
    COPYWRITER_PERSONAS,
    TEMPLATE_SYSTEMS
)

router = APIRouter()


@router.get("/options", response_model=OptionsResponse)
async def get_copywriter_options(
    current_user: str = Depends(get_current_user)
):
    """
    Get available options for copywriting.

    Returns all available formats, personas, template systems, and tones.
    """
    formats = [
        FormatOption(name=name, description=desc.split("\n")[0].strip() if desc else "")
        for name, desc in FORMAT_INSTRUCTIONS.items()
    ]

    personas = [
        PersonaOption(name=name, description=desc)
        for name, desc in COPYWRITER_PERSONAS.items()
    ]

    template_systems = [
        TemplateSystemOption(name=name, description=desc.split("\n")[0].strip() if desc else "")
        for name, desc in TEMPLATE_SYSTEMS.items()
    ]

    tones = ["Professional", "Casual", "Excited", "Urgent", "Witty", "Empathetic", "Authoritative"]

    return OptionsResponse(
        formats=formats,
        personas=personas,
        template_systems=template_systems,
        tones=tones
    )


@router.post("/generate", response_model=CopywriterResponse)
async def generate_copy(
    request: CopywriterRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate marketing copy in various formats.

    - **topic**: Product/service/topic to write about
    - **format**: Content format (Social Media Post, Email Newsletter, Product Description, etc.)
    - **tone**: Writing tone (Professional, Casual, Excited, etc.)
    - **target_audience**: Target demographic
    - **variation_count**: Number of variations (1, 2, 3, or 5)
    - **enhance**: Whether to enhance the topic first
    - **persona**: Writing persona (Founder, Expert, Friend, etc.)
    - **ab_testing_mode**: Generate distinct variations for A/B testing
    - **template_system**: Copywriting framework (AIDA, PAS, StoryBrand, Before-After-Bridge)
    - **analyze**: Whether to analyze the generated copy for effectiveness
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="copywriter",
        data={
            "topic": request.topic,
            "format": request.format,
            "tone": request.tone,
            "target_audience": request.target_audience,
            "variation_count": request.variation_count,
            "enhance": request.enhance,
            "template_id": request.template_id,
            "persona": request.persona,
            "ab_testing_mode": request.ab_testing_mode,
            "template_system": request.template_system,
            "analyze": request.analyze
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return CopywriterResponse(
        success=True,
        variations=result.get("variations"),
        raw_content=result.get("raw_content"),
        enhanced_topic=result.get("enhanced_topic"),
        analysis_result=result.get("analysis_result")
    )


@router.post("/enhance")
async def enhance_topic(
    topic: str,
    current_user: str = Depends(get_current_user)
):
    """Enhance a marketing topic for better copy generation"""
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="copywriter",
        data={
            "topic": topic,
            "format": "Social Media Post",
            "tone": "Professional",
            "variation_count": 1,
            "enhance": True
        }
    )

    return {
        "success": True,
        "enhanced_topic": result.get("enhanced_topic", topic)
    }
