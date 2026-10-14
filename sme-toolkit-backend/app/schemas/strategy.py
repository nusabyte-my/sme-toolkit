from pydantic import BaseModel, Field
from typing import Optional, Literal


class StrategyRequest(BaseModel):
    """Request for strategic advice generation"""
    business_context: str = Field(..., description="Business situation/goal description")
    advice_type: Literal["TIPS", "GROWTH_PLAN", "INSIGHTS", "CREATIVE"] = Field(
        ..., description="Type of strategic advice"
    )
    enhance: bool = Field(False, description="Whether to enhance the context first")

    class Config:
        json_schema_extra = {
            "example": {
                "business_context": "I run a small bakery and want to expand online sales",
                "advice_type": "GROWTH_PLAN",
                "enhance": True
            }
        }


class StrategyResponse(BaseModel):
    """Response containing strategic advice"""
    success: bool
    advice_type: Optional[str] = None
    content: Optional[str] = Field(None, description="Generated strategic advice")
    enhanced_context: Optional[str] = None
    error: Optional[str] = None
