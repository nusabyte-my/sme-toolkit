from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class BusinessCanvasData(BaseModel):
    """9-block Business Model Canvas data structure"""
    keyPartners: List[str] = Field(default_factory=list, description="Key partners and suppliers")
    keyActivities: List[str] = Field(default_factory=list, description="Key business activities")
    keyResources: List[str] = Field(default_factory=list, description="Essential resources")
    valuePropositions: List[str] = Field(default_factory=list, description="Value delivered to customers")
    customerRelationships: List[str] = Field(default_factory=list, description="Customer relationship types")
    channels: List[str] = Field(default_factory=list, description="Distribution and communication channels")
    customerSegments: List[str] = Field(default_factory=list, description="Target customer groups")
    costStructure: List[str] = Field(default_factory=list, description="Major cost categories")
    revenueStreams: List[str] = Field(default_factory=list, description="Revenue sources and pricing")

    class Config:
        json_schema_extra = {
            "example": {
                "keyPartners": ["Coffee bean suppliers", "Logistics partners", "Payment processors"],
                "keyActivities": ["Sourcing quality beans", "Subscription management", "Customer support"],
                "keyResources": ["E-commerce platform", "Supplier relationships", "Brand"],
                "valuePropositions": ["Fresh beans delivered monthly", "Curated selections", "Convenience"],
                "customerRelationships": ["Personalized recommendations", "Loyalty program"],
                "channels": ["Website", "Email marketing", "Social media"],
                "customerSegments": ["Coffee enthusiasts", "Office managers", "Home baristas"],
                "costStructure": ["Product costs", "Shipping", "Marketing", "Platform maintenance"],
                "revenueStreams": ["Monthly subscriptions", "One-time purchases", "Gift cards"]
            }
        }


class CanvasRequest(BaseModel):
    """Request to generate a Business Model Canvas"""
    description: str = Field(..., description="Business idea description")
    user_inputs: Optional[Dict[str, str]] = Field(None, description="Optional partial inputs for specific blocks")
    mode: str = Field("quick", description="Generation mode: 'quick' or 'wizard'")
    enhance: bool = Field(False, description="Whether to enhance the description first")

    class Config:
        json_schema_extra = {
            "example": {
                "description": "A subscription service for organic coffee beans delivered to offices",
                "mode": "quick",
                "enhance": True
            }
        }


class CanvasResponse(BaseModel):
    """Response containing generated Business Model Canvas"""
    success: bool
    canvas: Optional[BusinessCanvasData] = None
    enhanced_description: Optional[str] = None
    error: Optional[str] = None
