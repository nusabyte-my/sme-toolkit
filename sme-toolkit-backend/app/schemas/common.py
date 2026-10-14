from pydantic import BaseModel, HttpUrl
from typing import Optional, Any, Dict


class WebhookRequest(BaseModel):
    """Universal webhook request schema for n8n integration"""
    action: Optional[str] = None
    data: Dict[str, Any]
    callback_url: Optional[HttpUrl] = None
    sync: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "action": "generate",
                "data": {"description": "A subscription coffee service"},
                "callback_url": "https://n8n.example.com/webhook/callback",
                "sync": True
            }
        }


class WebhookResponse(BaseModel):
    """Universal webhook response schema"""
    success: bool
    job_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class JobResponse(BaseModel):
    """Job status response"""
    job_id: str
    agent: str
    action: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str
