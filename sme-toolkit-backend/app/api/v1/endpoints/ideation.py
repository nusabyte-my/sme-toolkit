"""Ideation API endpoints - Robust ideation workflow with templates"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging

from app.agents.orchestrator import get_orchestrator
from app.schemas.ideation import (
    IdeationRequest,
    IdeationResponse,
    IdeationOptionsResponse,
    ActionOption,
    TemplateOption,
    InnovationLevelOption
)
from app.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=IdeationResponse)
async def generate_ideation(
    request: IdeationRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate ideas using various ideation techniques and templates.
    
    Supports multiple action types:
    - brainstorm: Generate diverse ideas using creative techniques
    - analyze_trends: Analyze current and emerging trends
    - competitive_analysis: Analyze competitors and identify strategic opportunities
    - market_opportunity: Identify market opportunities and assess potential
    - product_innovation: Generate innovative product ideas
    - business_model_innovation: Generate innovative business model ideas
    
    Templates available:
    - scamper: Substitute, Combine, Adapt, Modify, Put to another use, Eliminate, Reverse
    - mind_map: Visual brainstorming with central topic and branching ideas
    - swot: Strengths, Weaknesses, Opportunities, Threats analysis
    - blue_ocean: Find uncontested market space and make competition irrelevant
    - lean_startup: Build-Measure-Learn cycle with MVP focus
    - design_thinking: Empathize, Define, Ideate, Prototype, Test, Iterate
    - first_principles: Break down to fundamental truths and rebuild from scratch
    - reverse_engineering: Study successful solutions and adapt core principles
    """
    try:
        orchestrator = get_orchestrator()
        ideation_agent = orchestrator._agents.get("ideation")
        
        if not ideation_agent:
            raise HTTPException(status_code=500, detail="Ideation agent not available")
        
        input_data = {
            "action": request.action,
            "topic": request.topic,
            "context": request.context,
            "template": request.template,
            "industry": request.industry,
            "target_audience": request.target_audience,
            "constraints": request.constraints,
            "innovation_level": request.innovation_level,
            "quantity": request.quantity,
            "enhance": request.enhance
        }
        
        result = await ideation_agent.invoke(input_data)
        
        if result.get("error"):
            return IdeationResponse(
                success=False,
                action=request.action,
                error=result.get("error")
            )
        
        logger.info(f"Template: {request.template}, Result keys: {result.keys()}")
        logger.info(f"Ideas in result: {result.get('ideas')}")
        
        return IdeationResponse(
            success=True,
            action=result.get("action"),
            ideas=result.get("ideas"),
            trend_analysis=result.get("trend_analysis"),
            competitor_analysis=result.get("competitor_analysis"),
            market_opportunities=result.get("market_opportunities"),
            insights=result.get("insights") or [],
            recommendations=result.get("recommendations") or [],
            template_used=result.get("template") or request.template
        )
        
    except Exception as e:
        return IdeationResponse(
            success=False,
            action=request.action,
            error=str(e)
        )


@router.get("/options", response_model=IdeationOptionsResponse)
async def get_ideation_options(
    current_user: str = Depends(get_current_user)
):
    """
    Get available options for ideation.
    Returns all available actions, templates, and innovation levels.
    """
    try:
        orchestrator = get_orchestrator()
        ideation_agent = orchestrator._agents.get("ideation")
        
        if not ideation_agent:
            raise HTTPException(status_code=500, detail="Ideation agent not available")
        
        options = await ideation_agent.get_options()
        
        return IdeationOptionsResponse(
            actions=[ActionOption(**action) for action in options["actions"]],
            templates=[TemplateOption(**template) for template in options["templates"]],
            innovation_levels=[InnovationLevelOption(**level) for level in options["innovation_levels"]]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ideation options: {str(e)}")
