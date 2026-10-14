from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.schemas.strategy import StrategyRequest, StrategyResponse
from app.agents.orchestrator import get_orchestrator

router = APIRouter()


@router.post("/generate", response_model=StrategyResponse)
async def generate_strategy(
    request: StrategyRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate strategic business advice.

    - **business_context**: Business situation/goal description
    - **advice_type**: Type of advice (TIPS, GROWTH_PLAN, INSIGHTS, CREATIVE)
    - **enhance**: Whether to enhance the context first
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="strategy",
        data={
            "business_context": request.business_context,
            "advice_type": request.advice_type,
            "enhance": request.enhance
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return StrategyResponse(
        success=True,
        advice_type=result.get("advice_type"),
        content=result.get("content"),
        enhanced_context=result.get("enhanced_context")
    )


@router.post("/tips")
async def get_tips(
    business_context: str,
    enhance: bool = False,
    current_user: str = Depends(get_current_user)
):
    """Quick endpoint for business tips"""
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="strategy",
        data={
            "business_context": business_context,
            "advice_type": "TIPS",
            "enhance": enhance
        }
    )

    return result


@router.post("/growth-plan")
async def get_growth_plan(
    business_context: str,
    enhance: bool = False,
    current_user: str = Depends(get_current_user)
):
    """Quick endpoint for 6-month growth plan"""
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="strategy",
        data={
            "business_context": business_context,
            "advice_type": "GROWTH_PLAN",
            "enhance": enhance
        }
    )

    return result


@router.post("/insights")
async def get_insights(
    business_context: str,
    enhance: bool = False,
    current_user: str = Depends(get_current_user)
):
    """Quick endpoint for business insights and risk analysis"""
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="strategy",
        data={
            "business_context": business_context,
            "advice_type": "INSIGHTS",
            "enhance": enhance
        }
    )

    return result


@router.post("/creative")
async def get_creative_concepts(
    business_context: str,
    enhance: bool = False,
    current_user: str = Depends(get_current_user)
):
    """Quick endpoint for creative marketing concepts"""
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="strategy",
        data={
            "business_context": business_context,
            "advice_type": "CREATIVE",
            "enhance": enhance
        }
    )

    return result
