"""Orchestration-related Pydantic schemas"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AnalysisType(str, Enum):
    COMPREHENSIVE = "comprehensive"
    GOALS = "goals"
    GROWTH = "growth"
    COSTING = "costing"
    SUGGESTIONS = "suggestions"


class AnalysisStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AnalysisConfig(BaseModel):
    """Configuration for analysis"""
    include_goals: bool = Field(True, description="Include goal advisor")
    include_growth: bool = Field(True, description="Include growth advisor")
    include_costing: bool = Field(True, description="Include costing advisor")
    include_suggestions: bool = Field(True, description="Include suggestion advisor")


class AnalysisRequest(BaseModel):
    """Schema for analysis request"""
    business_profile_id: str = Field(..., description="ID of business profile to analyze")
    analysis_type: AnalysisType = Field(AnalysisType.COMPREHENSIVE, description="Type of analysis")
    config: Optional[AnalysisConfig] = Field(None, description="Analysis configuration")


class AnalysisResponse(BaseModel):
    """Schema for analysis response"""
    id: str
    business_profile_id: str
    analysis_type: str
    results: Dict[str, Any]
    scores: Optional[Dict[str, Any]] = None
    insights: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    """Schema for analysis list response"""
    analyses: List[AnalysisResponse]
    total: int


class ParallelExecutionRequest(BaseModel):
    """Schema for parallel execution request"""
    business_profile_id: str = Field(..., description="ID of business profile")
    agents: List[str] = Field(..., description="List of agents to execute in parallel")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for agents")


class SequentialExecutionRequest(BaseModel):
    """Schema for sequential execution request"""
    business_profile_id: str = Field(..., description="ID of business profile")
    workflow: List[Dict[str, Any]] = Field(..., description="Workflow steps with agent and data")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Initial input data")


class ExecutionResult(BaseModel):
    """Result from agent execution"""
    agent_name: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class ParallelExecutionResponse(BaseModel):
    """Schema for parallel execution response"""
    job_id: str
    business_profile_id: str
    results: List[ExecutionResult]
    total_execution_time: float
    started_at: datetime
    completed_at: datetime


class SequentialExecutionResponse(BaseModel):
    """Schema for sequential execution response"""
    job_id: str
    business_profile_id: str
    workflow_results: List[Dict[str, Any]]
    total_execution_time: float
    started_at: datetime
    completed_at: datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatusResponse(BaseModel):
    """Schema for job status response"""
    job_id: str
    business_profile_id: str
    status: str
    progress: float = Field(0, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    updated_at: datetime


class AgentInteraction(BaseModel):
    """Agent interaction record"""
    agent_name: str
    interaction_type: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    decision: Optional[Dict[str, Any]] = None
    timestamp: datetime


class InteractionLogResponse(BaseModel):
    """Schema for interaction log response"""
    business_profile_id: str
    interactions: List[AgentInteraction]
    total: int
