from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime


class LeadBase(BaseModel):
    """Base Lead data"""
    name: str = Field(..., description="Contact name")
    company: Optional[str] = Field(None, description="Company name")
    position: Optional[str] = Field(None, description="Contact position")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    lead_source: Optional[str] = Field(None, description="Lead source (website, referral, social_media, etc.)")
    status: Optional[str] = Field("new", description="Pipeline status")
    notes: Optional[str] = Field(None, description="Additional notes")
    assigned_agent_id: Optional[str] = Field(None, description="ID of assigned sales agent")
    last_contacted_at: Optional[datetime] = Field(None, description="Last contact timestamp")
    next_follow_up_at: Optional[datetime] = Field(None, description="Next follow-up due date")
    score: Optional[int] = Field(None, ge=0, le=100, description="Lead score 0-100")
    score_factors: Optional[Dict[str, Any]] = Field(None, description="Lead scoring factor breakdown")
    score_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Score change history")
    tags: Optional[List[str]] = Field(default_factory=list, description="Lead tags")
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom fields")


class LeadCreate(LeadBase):
    """Schema for creating a lead"""
    pass


class LeadUpdate(BaseModel):
    """Schema for updating a lead"""
    name: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    lead_source: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    last_contacted_at: Optional[datetime] = None
    next_follow_up_at: Optional[datetime] = None
    score: Optional[int] = Field(None, ge=0, le=100)
    score_factors: Optional[Dict[str, Any]] = None
    score_history: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadResponse(LeadBase):
    """Schema for lead response"""
    id: str
    business_profile_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Agent Schemas ---

class LeadAgentInput(BaseModel):
    """Lead data structure for Agents"""
    id: Optional[str] = None
    name: str = Field(..., description="Contact name")
    company: str = Field(..., description="Company name")
    email: EmailStr = Field(..., description="Contact email")
    status: Literal["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"] = Field(
        "New", description="Pipeline status"
    )
    engagement: Literal["Low", "Medium", "High"] = Field(
        "Medium", description="Engagement level"
    )
    notes: str = Field("", description="Additional notes about the lead")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Smith",
                "company": "Acme Corp",
                "email": "john@acme.com",
                "status": "Contacted",
                "engagement": "High",
                "notes": "Interested in enterprise plan, needs demo"
            }
        }


class LeadRequest(BaseModel):
    """Request for lead operations"""
    action: Literal["score", "email", "analyze"] = Field(..., description="Action to perform")
    lead: LeadAgentInput = Field(..., description="Lead data")
    tone: Optional[str] = Field("Professional", description="Email tone (for email action)")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "score",
                "lead": {
                    "name": "John Smith",
                    "company": "Acme Corp",
                    "email": "john@acme.com",
                    "status": "Contacted",
                    "engagement": "High",
                    "notes": "Interested in enterprise plan"
                }
            }
        }


class LeadScoreResponse(BaseModel):
    """Response for lead scoring"""
    success: bool
    score: Optional[int] = Field(None, ge=0, le=100, description="Lead score 0-100")
    suggestions: Optional[str] = Field(None, description="Recommended next action")
    error: Optional[str] = None


class LeadEmailResponse(BaseModel):
    """Response for email generation"""
    success: bool
    email: Optional[str] = Field(None, description="Generated cold email")
    subject: Optional[str] = Field(None, description="Email subject line")
    error: Optional[str] = None


class LeadListResponse(BaseModel):
    items: List[LeadResponse]
    total: int
    page: int
    size: int


# --- Sales Task Schemas ---

class SalesTaskBase(BaseModel):
    """Base SalesTask data"""
    lead_id: str = Field(..., description="Associated lead ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    task_type: Literal["call", "email", "meeting", "demo", "proposal", "follow_up"] = Field(
        ..., description="Type of task"
    )
    priority: Literal["low", "medium", "high", "urgent"] = Field("medium", description="Task priority")
    due_date: datetime = Field(..., description="Task due date")
    assigned_to: Optional[str] = Field(None, description="ID of agent assigned to task")
    outcome: Optional[str] = Field(None, description="Task outcome")
    notes: Optional[str] = Field(None, description="Task notes")


class SalesTaskCreate(SalesTaskBase):
    """Schema for creating a sales task"""
    business_profile_id: str = Field(..., description="Business profile ID")


class SalesTaskUpdate(BaseModel):
    """Schema for updating a sales task"""
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[Literal["call", "email", "meeting", "demo", "proposal", "follow_up"]] = None
    priority: Optional[Literal["low", "medium", "high", "urgent"]] = None
    status: Optional[Literal["pending", "in_progress", "completed", "cancelled"]] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None


class SalesTaskResponse(SalesTaskBase):
    """Schema for sales task response"""
    id: str
    business_profile_id: str
    status: Literal["pending", "in_progress", "completed", "cancelled"]
    assigned_by: Optional[str]
    completed_at: Optional[datetime]
    is_automated: bool
    follow_up_rule_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SalesTaskListResponse(BaseModel):
    items: List[SalesTaskResponse]
    total: int
    page: int
    size: int


# --- Follow Up Rule Schemas ---

class FollowUpRuleBase(BaseModel):
    """Base FollowUpRule data"""
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    trigger_event: Literal["lead_created", "lead_status_changed", "interaction_logged", "score_changed"] = Field(
        ..., description="Event that triggers the rule"
    )
    trigger_status: Optional[str] = Field(None, description="Specific lead status to trigger on")
    trigger_score_threshold: Optional[int] = Field(None, ge=0, le=100, description="Score threshold to trigger")
    delay_hours: int = Field(24, ge=0, description="Delay in hours before creating task")
    delay_business_days_only: bool = Field(False, description="Only count business days")
    task_type: Literal["call", "email", "meeting", "demo", "proposal", "follow_up"] = Field(
        ..., description="Type of task to create"
    )
    task_title_template: str = Field(..., description="Template for task title")
    task_description_template: Optional[str] = Field(None, description="Template for task description")
    task_priority: Literal["low", "medium", "high", "urgent"] = Field("medium", description="Task priority")
    assign_to_agent: Optional[str] = Field(None, description="Agent ID to assign tasks to")
    is_active: bool = Field(True, description="Whether the rule is active")


class FollowUpRuleCreate(FollowUpRuleBase):
    """Schema for creating a follow-up rule"""
    business_profile_id: str = Field(..., description="Business profile ID")


class FollowUpRuleUpdate(BaseModel):
    """Schema for updating a follow-up rule"""
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_event: Optional[Literal["lead_created", "lead_status_changed", "interaction_logged", "score_changed"]] = None
    trigger_status: Optional[str] = None
    trigger_score_threshold: Optional[int] = Field(None, ge=0, le=100)
    delay_hours: Optional[int] = Field(None, ge=0)
    delay_business_days_only: Optional[bool] = None
    task_type: Optional[Literal["call", "email", "meeting", "demo", "proposal", "follow_up"]] = None
    task_title_template: Optional[str] = None
    task_description_template: Optional[str] = None
    task_priority: Optional[Literal["low", "medium", "high", "urgent"]] = None
    assign_to_agent: Optional[str] = None
    is_active: Optional[bool] = None


class FollowUpRuleResponse(FollowUpRuleBase):
    """Schema for follow-up rule response"""
    id: str
    business_profile_id: str
    execution_count: int
    last_executed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FollowUpRuleListResponse(BaseModel):
    items: List[FollowUpRuleResponse]
    total: int
    page: int
    size: int
