from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any


class CopywriterRequest(BaseModel):
    """Request for marketing copy generation"""
    topic: str = Field(..., description="Product/service/topic to write about")
    format: str = Field(
        ..., description="Content format (e.g., Social Media Post, Email, etc.)"
    )
    tone: Literal["Professional", "Casual", "Excited", "Urgent", "Witty", "Empathetic", "Authoritative"] = Field(
        "Professional", description="Writing tone"
    )
    target_audience: Optional[str] = Field(None, description="Target demographic")
    variation_count: Literal[1, 2, 3, 5] = Field(1, description="Number of variations (2 for A/B testing)")
    enhance: bool = Field(False, description="Whether to enhance the topic first")
    
    # Enhanced Fields
    template_id: Optional[str] = Field(None, description="Specific template ID to use")
    persona: Optional[str] = Field("General", description="Writing persona (e.g., Founder, Expert, Friend)")
    ab_testing_mode: bool = Field(False, description="Generate distinct variations for A/B testing")
    output_format: Literal["text", "markdown", "json"] = Field("markdown", description="Output format")
    template_system: Optional[Literal["AIDA", "PAS", "StoryBrand", "Before-After-Bridge"]] = Field(
        None, description="Copywriting framework to apply"
    )
    analyze: bool = Field(False, description="Whether to analyze the generated copy for effectiveness")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Launch of our new eco-friendly sneakers",
                "format": "Social Media Post",
                "tone": "Excited",
                "target_audience": "Environmentally conscious millennials",
                "variation_count": 3,
                "enhance": True,
                "persona": "Brand Ambassador",
                "ab_testing_mode": False,
                "template_system": "AIDA",
                "analyze": True
            }
        }


class CopyVariation(BaseModel):
    """Single copy variation"""
    label: str = Field(..., description="Variation label (e.g., 'Option 1')")
    content: str = Field(..., description="Generated copy content")


class CopyAnalysisResult(BaseModel):
    """Analysis of generated copy effectiveness"""
    raw_analysis: Optional[str] = Field(None, description="Raw AI analysis output")
    clarity_score: Optional[int] = Field(None, description="Clarity score (1-10)")
    engagement_score: Optional[int] = Field(None, description="Engagement potential score (1-10)")
    persuasion_elements: Optional[List[str]] = Field(None, description="Persuasion techniques used")
    improvements: Optional[List[str]] = Field(None, description="Suggested improvements")
    suggested_variations: Optional[List[str]] = Field(None, description="Variations to test")


class CopywriterResponse(BaseModel):
    """Response containing generated marketing copy"""
    success: bool
    variations: Optional[List[CopyVariation]] = None
    raw_content: Optional[str] = Field(None, description="Raw content if not parsed into variations")
    enhanced_topic: Optional[str] = None
    analysis_result: Optional[CopyAnalysisResult] = Field(None, description="Copy effectiveness analysis")
    error: Optional[str] = None


class FormatOption(BaseModel):
    """Available content format"""
    name: str = Field(..., description="Format name")
    description: str = Field(..., description="Format description")


class PersonaOption(BaseModel):
    """Available writing persona"""
    name: str = Field(..., description="Persona name")
    description: str = Field(..., description="Persona description")


class TemplateSystemOption(BaseModel):
    """Available copywriting template system"""
    name: str = Field(..., description="Template system name")
    description: str = Field(..., description="Template system description")


class OptionsResponse(BaseModel):
    """Response containing available options"""
    formats: List[FormatOption]
    personas: List[PersonaOption]
    template_systems: List[TemplateSystemOption]
    tones: List[str]
