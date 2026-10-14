"""
Market Research FastAPI Router for SME OS V2.
Calculates TAM/SAM/SOM in MYR, generates buyer personas, and virality growth hacks.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.market_research_service import MarketResearchService

router = APIRouter()
market_service = MarketResearchService()


class MarketSizeRequest(BaseModel):
    industry: str = Field(..., description="Industry sector")
    target_region: Optional[str] = Field("Malaysia")


class PersonaRequest(BaseModel):
    industry: str = Field(...)
    product_name: str = Field(...)


@router.post("/market-size", summary="Calculate TAM / SAM / SOM in MYR (RM)")
async def calculate_market_size(req: MarketSizeRequest):
    """Calculates TAM, SAM, SOM market size in MYR (RM)"""
    return market_service.analyze_market_size_myr(
        industry=req.industry,
        target_region=req.target_region or "Malaysia"
    )


@router.post("/buyer-personas", summary="Generate Malaysian Buyer Personas")
async def generate_buyer_personas(req: PersonaRequest):
    """Generates buyer demographics, pain points, and preferred channels (WhatsApp/TikTok)"""
    return market_service.generate_audience_persona(
        industry=req.industry,
        product_name=req.product_name
    )


@router.get("/growth-hacks", summary="Get Audience Virality Growth Hacks")
async def get_growth_hacks(industry: Optional[str] = "E-Commerce"):
    """Returns virality growth strategies to acquire Malaysian audience rapidly"""
    return {
        "industry": industry,
        "growth_hacks": market_service.get_audience_growth_hacks(industry or "E-Commerce")
    }
