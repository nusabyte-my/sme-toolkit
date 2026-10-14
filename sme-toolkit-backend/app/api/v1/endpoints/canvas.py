from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.schemas.canvas import CanvasRequest, CanvasResponse
from app.agents.orchestrator import get_orchestrator

router = APIRouter()


@router.post("/generate", response_model=CanvasResponse)
async def generate_canvas(
    request: CanvasRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate a Business Model Canvas from a business description.

    - **description**: Business idea description
    - **user_inputs**: Optional partial inputs for specific blocks
    - **mode**: 'quick' or 'wizard' generation mode
    - **enhance**: Whether to enhance the description first
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="canvas",
        data={
            "description": request.description,
            "user_inputs": request.user_inputs,
            "mode": request.mode,
            "enhance": request.enhance
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return CanvasResponse(
        success=True,
        canvas=result.get("canvas"),
        enhanced_description=result.get("enhanced_description")
    )


@router.post("/enhance")
async def enhance_description(
    description: str,
    current_user: str = Depends(get_current_user)
):
    """Enhance a business description for better canvas generation"""
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="canvas",
        data={
            "description": description,
            "enhance": True,
            "mode": "quick"
        }
    )

    return {
        "success": True,
        "enhanced_description": result.get("enhanced_description", description)
    }
