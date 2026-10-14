from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.schemas.video import (
    VideoRequest,
    VideoResponse,
    VideoScriptResponse,
    StoryboardResponse,
    VideoGenerateResponse
)
from app.agents.orchestrator import get_orchestrator

router = APIRouter()


@router.post("/script", response_model=VideoScriptResponse)
async def generate_script(
    request: VideoRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate a video script/prompt optimized for video generation.

    - **topic**: Video topic
    - **platform**: Target platform (YouTube, TikTok, etc.)
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="video",
        action="script",
        data={
            "action": "script",
            "topic": request.topic,
            "platform": request.platform
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return VideoScriptResponse(
        success=True,
        script=result.get("script")
    )


@router.post("/storyboard", response_model=StoryboardResponse)
async def generate_storyboard(
    request: VideoRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate a storyboard from a video script.

    - **script**: Full video script to break into scenes
    """
    if not request.script:
        raise HTTPException(
            status_code=400,
            detail="script is required for storyboard generation"
        )

    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="video",
        action="storyboard",
        data={
            "action": "storyboard",
            "script": request.script
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return StoryboardResponse(
        success=True,
        scenes=result.get("scenes", [])
    )


@router.post("/generate", response_model=VideoGenerateResponse)
async def generate_video(
    request: VideoRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Start video generation (async operation).

    Returns a job_id for polling status.

    - **prompt**: Visual prompt for video
    - **resolution**: Video resolution (720p, 1080p)
    - **aspect_ratio**: Video aspect ratio (16:9, 9:16)
    - **style_filter**: Optional style filter
    """
    if not request.prompt:
        raise HTTPException(
            status_code=400,
            detail="prompt is required for video generation"
        )

    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="video",
        action="generate",
        data={
            "action": "generate",
            "prompt": request.prompt,
            "resolution": request.resolution,
            "aspect_ratio": request.aspect_ratio,
            "style_filter": request.style_filter
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return VideoGenerateResponse(
        success=True,
        job_id=result.get("job_id"),
        status=result.get("status", "queued")
    )
