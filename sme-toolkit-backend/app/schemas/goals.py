"""Goal-related Pydantic schemas"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class GoalPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class SmartCriteria(BaseModel):
    """SMART criteria for goals"""
    specific: Optional[str] = None
    measurable: Optional[str] = None
    achievable: Optional[str] = None
    relevant: Optional[str] = None
    time_bound: Optional[str] = None


class BMCAlignment(BaseModel):
    """Alignment with Business Model Canvas blocks"""
    aligned_blocks: List[str] = Field(default_factory=list)
    alignment_score: Optional[float] = None
    gaps: List[str] = Field(default_factory=list)


class Milestone(BaseModel):
    """Goal milestone"""
    milestone: str
    target_date: Optional[datetime] = None
    metrics: List[str] = Field(default_factory=list)


class GoalCreate(BaseModel):
    """Schema for creating a goal"""
    title: str = Field(..., description="Goal title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Goal description")
    category: Optional[str] = Field(None, description="Goal category (financial, operational, market, innovation)")
    priority: GoalPriority = Field(GoalPriority.MEDIUM, description="Goal priority")
    deadline: Optional[datetime] = Field(None, description="Goal deadline")
    smart_criteria: Optional[SmartCriteria] = Field(None, description="SMART criteria breakdown")
    bmc_alignment: Optional[BMCAlignment] = Field(None, description="Alignment with BMC blocks")
    milestones: Optional[List[Milestone]] = Field(None, description="Goal milestones")
    success_metrics: Optional[List[str]] = Field(None, description="Success metrics")


class GoalUpdate(BaseModel):
    """Schema for updating a goal"""
    title: Optional[str] = Field(None, description="Goal title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Goal description")
    category: Optional[str] = Field(None, description="Goal category")
    priority: Optional[GoalPriority] = Field(None, description="Goal priority")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Goal progress (0-100)")
    deadline: Optional[datetime] = Field(None, description="Goal deadline")
    status: Optional[GoalStatus] = Field(None, description="Goal status")
    smart_criteria: Optional[SmartCriteria] = Field(None, description="SMART criteria breakdown")
    bmc_alignment: Optional[BMCAlignment] = Field(None, description="Alignment with BMC blocks")
    milestones: Optional[List[Milestone]] = Field(None, description="Goal milestones")
    success_metrics: Optional[List[str]] = Field(None, description="Success metrics")


class GoalResponse(BaseModel):
    """Schema for goal response"""
    id: str
    business_profile_id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    progress: float
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    smart_criteria: Optional[Dict[str, Any]] = None
    bmc_alignment: Optional[Dict[str, Any]] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    success_metrics: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalStatistics(BaseModel):
    """Schema for goal statistics"""
    total_goals: int
    active_goals: int
    completed_goals: int
    paused_goals: int
    average_progress: float
    by_category: Dict[str, int]
    by_priority: Dict[str, int]


class GoalListResponse(BaseModel):
    """Schema for goal list response"""
    goals: List[GoalResponse]
    total: int
