from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict


class VisualRequest(BaseModel):
    """Request for visual generation or editing"""
    action: Literal["generate", "edit"] = Field("generate", description="Action type")
    prompt: str = Field(..., description="Visual description or edit instruction")
    style: Optional[str] = Field(None, description="Visual style (e.g., 'Photorealistic', 'Minimalist Vector')")
    aspect_ratio: str = Field("1:1", description="Image aspect ratio (1:1, 9:16, 16:9, 3:4, 1:2)")
    category: Optional[Literal["Product Showcase", "Social Media Post", "Banner/Header", "Infographic Element", "Event Poster", "Abstract Background"]] = Field(
        None, description="Visual category template to use"
    )
    composition_rule: Optional[Literal["rule_of_thirds", "centered", "golden_ratio", "leading_lines", "negative_space", "symmetry"]] = Field(
        None, description="Composition rule to apply"
    )
    reference_image: Optional[str] = Field(None, description="Base64 reference image for generation")
    source_image: Optional[str] = Field(None, description="Base64 source image for editing")
    enhance: bool = Field(False, description="Whether to enhance the prompt first")
    variations: Optional[Dict[str, str]] = Field(None, description="Variations to generate (key: variation_name, value: variation_instruction)")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "generate",
                "prompt": "Modern office space with plants and natural lighting",
                "style": "Photorealistic",
                "aspect_ratio": "16:9",
                "category": "Social Media Post",
                "composition_rule": "rule_of_thirds",
                "enhance": True,
                "variations": {
                    "brighter": "with more natural light",
                    "minimal": "cleaner, minimalist version"
                }
            }
        }


class VisualResponse(BaseModel):
    """Response containing generated/edited image"""
    success: bool
    image: Optional[str] = Field(None, description="Base64 encoded image data")
    enhanced_prompt: Optional[str] = None
    variations: Optional[Dict[str, str]] = Field(None, description="Generated variations")
    error: Optional[str] = None


class StyleOption(BaseModel):
    """Available visual style option"""
    name: str = Field(..., description="Style name")
    description: str = Field(..., description="Style description")


class CategoryOption(BaseModel):
    """Available visual category option"""
    name: str = Field(..., description="Category name")


class AspectRatioOption(BaseModel):
    """Available aspect ratio option"""
    name: str = Field(..., description="Aspect ratio name")


class CompositionRuleOption(BaseModel):
    """Available composition rule option"""
    name: str = Field(..., description="Composition rule name")


class VisualOptionsResponse(BaseModel):
    """Response containing available visual options"""
    styles: Dict[str, str] = Field(..., description="Available styles with descriptions")
    categories: list = Field(..., description="Available categories")
    aspect_ratios: list = Field(..., description="Available aspect ratios")
    composition_rules: list = Field(..., description="Available composition rules")