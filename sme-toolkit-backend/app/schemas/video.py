from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class StoryboardScene(BaseModel):
    """Single scene in a storyboard"""
    id: Optional[str] = None
    description: str = Field(..., description="5-word scene summary")
    prompt: str = Field(..., description="Visual prompt for video generation")
    video_url: Optional[str] = None
    status: Literal["idle", "generating", "done", "error"] = "idle"
    duration: float = Field(5.0, description="Scene duration in seconds")
    trim_start: float = Field(0.0, description="Trim start time")
    trim_end: float = Field(5.0, description="Trim end time")


class VideoRequest(BaseModel):
    """Request for video operations"""
    action: Literal["script", "storyboard", "generate"] = Field(..., description="Action type")
    topic: Optional[str] = Field(None, description="Video topic (for script action)")
    platform: Optional[str] = Field(None, description="Target platform (YouTube, TikTok, etc.)")
    script: Optional[str] = Field(None, description="Full script (for storyboard action)")
    prompt: Optional[str] = Field(None, description="Visual prompt (for generate action)")
    resolution: Literal["720p", "1080p"] = Field("720p", description="Video resolution")
    aspect_ratio: Literal["16:9", "9:16"] = Field("16:9", description="Video aspect ratio")
    style_filter: Optional[str] = Field(None, description="Visual style filter")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "script",
                "topic": "Premium leather handbag showcase",
                "platform": "Instagram Reels"
            }
        }


class VideoScriptResponse(BaseModel):
    """Response for video script generation"""
    success: bool
    script: Optional[str] = Field(None, description="Generated video script/prompt")
    error: Optional[str] = None


class StoryboardResponse(BaseModel):
    """Response for storyboard generation"""
    success: bool
    scenes: Optional[List[StoryboardScene]] = None
    error: Optional[str] = None


class VideoGenerateResponse(BaseModel):
    """Response for video generation"""
    success: bool
    job_id: Optional[str] = Field(None, description="Job ID for async polling")
    video_url: Optional[str] = Field(None, description="Video URL if sync completed")
    status: str = Field("pending", description="Generation status")
    error: Optional[str] = None


class VideoResponse(BaseModel):
    """Generic video response that can contain any result type"""
    success: bool
    action: str
    script: Optional[str] = None
    scenes: Optional[List[StoryboardScene]] = None
    job_id: Optional[str] = None
    video_url: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
