from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime


class PromptCategory(BaseModel):
    """Category for organizing prompts"""
    id: str
    name: str
    description: str
    icon: str
    color: str


class PromptVariable(BaseModel):
    """Variable definition for dynamic prompts"""
    name: str = Field(..., description="Variable name (e.g., {{topic}})")
    type: Literal["text", "number", "select", "multiselect", "date"] = Field("text", description="Variable data type")
    label: str = Field(..., description="Human-readable label")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    required: bool = Field(True, description="Whether this variable is required")
    default_value: Optional[Any] = Field(None, description="Default value")
    options: Optional[List[str]] = Field(None, description="Options for select/multiselect types")


class PromptTemplate(BaseModel):
    """Reusable prompt template"""
    id: str
    name: str
    description: str
    category_id: str
    template: str = Field(..., description="Prompt template with {{variable}} placeholders")
    variables: List[PromptVariable] = Field(default_factory=list, description="Variables in the template")
    tags: List[str] = Field(default_factory=list)
    is_public: bool = Field(False, description="Whether template is shared")
    usage_count: int = Field(0, description="Number of times used")
    rating: Optional[float] = Field(None, description="Average rating (1-5)")
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = Field(None, description="User ID of creator")


class PromptOptimizationRequest(BaseModel):
    """Request to optimize a prompt"""
    original_prompt: str = Field(..., description="Original prompt to optimize")
    goal: Literal["clarity", "creativity", "specificity", "conciseness", "comprehensive"] = Field(
        "comprehensive", description="Optimization goal"
    )
    target_model: Optional[str] = Field(None, description="Target AI model (e.g., GPT-4, Claude)")
    context: Optional[str] = Field(None, description="Additional context about the use case")
    output_format: Optional[Literal["text", "json", "code", "markdown"]] = Field(None, description="Desired output format")
    constraints: Optional[List[str]] = Field(None, description="Any constraints to include")


class PromptOptimizationResponse(BaseModel):
    """Response containing optimized prompt"""
    success: bool
    optimized_prompt: Optional[str] = None
    improvements: List[str] = Field(default_factory=list, description="List of improvements made")
    reasoning: Optional[str] = None
    variations: Optional[List[Dict[str, Any]]] = Field(None, description="Alternative variations")
    error: Optional[str] = None


class PromptFromTemplateRequest(BaseModel):
    """Request to generate prompt from template"""
    template_id: str
    variable_values: Dict[str, Any] = Field(..., description="Values for template variables")
    optimize: bool = Field(False, description="Whether to optimize the generated prompt")
    optimization_goal: Optional[str] = Field(None, description="Optimization goal if optimize=true")


class PromptGenerationResponse(BaseModel):
    """Response containing generated prompt"""
    success: bool
    prompt: Optional[str] = None
    template_used: Optional[PromptTemplate] = None
    error: Optional[str] = None


class PromptLibraryResponse(BaseModel):
    """Response listing prompt templates"""
    success: bool
    templates: List[PromptTemplate]
    categories: List[PromptCategory]
    total: int


class PromptAnalytics(BaseModel):
    """Analytics for prompt performance"""
    prompt_id: str
    total_uses: int
    avg_rating: float
    success_rate: float
    avg_response_time: float
    last_used: datetime
    usage_trend: List[Dict[str, Any]]


class PromptFeedback(BaseModel):
    """Feedback on a prompt"""
    prompt_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    comment: Optional[str] = None
    helpful: bool = Field(True, description="Whether the prompt was helpful")
