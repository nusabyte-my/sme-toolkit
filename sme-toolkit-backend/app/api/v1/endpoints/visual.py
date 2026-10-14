from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.schemas.visual import (
    VisualRequest,
    VisualResponse,
    VisualOptionsResponse
)
from app.agents.orchestrator import get_orchestrator
from app.agents.visual_agent import VisualAgent

router = APIRouter()


@router.get("/options", response_model=VisualOptionsResponse)
async def get_visual_options(
    current_user: str = Depends(get_current_user)
):
    """
    Get available options for visual generation.

    Returns all available styles, categories, aspect ratios, and composition rules.
    """
    orchestrator = get_orchestrator()
    
    # Get the visual agent from orchestrator
    visual_agent: VisualAgent = orchestrator._agents.get("visual")
    
    if not visual_agent:
        raise HTTPException(status_code=500, detail="Visual agent not available")
    
    options = await visual_agent.get_options()
    
    return VisualOptionsResponse(
        styles=options["styles"],
        categories=options["categories"],
        aspect_ratios=options["aspect_ratios"],
        composition_rules=options["composition_rules"]
    )


@router.post("/generate", response_model=VisualResponse)
async def generate_visual(
    request: VisualRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate a visual from text prompt.

    - **prompt**: Visual description
    - **style**: Visual style (Photorealistic, Minimalist Vector, etc.)
    - **aspect_ratio**: Image aspect ratio (1:1, 9:16, 16:9, 3:4, 1:2)
    - **category**: Visual category template (Product Showcase, Social Media Post, etc.)
    - **composition_rule**: Composition rule to apply (rule_of_thirds, centered, etc.)
    - **reference_image**: Optional base64 reference image
    - **enhance**: Whether to enhance the prompt first
    - **variations**: Dictionary of variations to generate (name: instruction)
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="visual",
        data={
            "action": "generate",
            "prompt": request.prompt,
            "style": request.style,
            "aspect_ratio": request.aspect_ratio,
            "category": request.category,
            "composition_rule": request.composition_rule,
            "reference_image": request.reference_image,
            "enhance": request.enhance,
            "variations": request.variations
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return VisualResponse(
        success=True,
        image=result.get("image"),
        enhanced_prompt=result.get("enhanced_prompt"),
        variations=result.get("variations")
    )


@router.post("/edit", response_model=VisualResponse)
async def edit_visual(
    request: VisualRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Edit an existing image based on instructions.

    - **prompt**: Edit instruction
    - **source_image**: Base64 source image to edit
    """
    if not request.source_image:
        raise HTTPException(
            status_code=400,
            detail="source_image is required for editing"
        )

    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="visual",
        data={
            "action": "edit",
            "prompt": request.prompt,
            "source_image": request.source_image
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return VisualResponse(
        success=True,
        image=result.get("image")
    )