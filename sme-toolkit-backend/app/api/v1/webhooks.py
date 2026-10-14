from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
import httpx

from app.auth import get_current_user
from app.schemas.common import WebhookRequest, WebhookResponse
from app.agents.orchestrator import get_orchestrator

webhook_router = APIRouter()


async def send_callback(callback_url: str, payload: dict):
    """Send result to n8n callback webhook"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(callback_url, json=payload, timeout=30.0)
    except Exception as e:
        print(f"Callback failed: {e}")


@webhook_router.post("/{agent_name}", response_model=WebhookResponse)
async def invoke_agent_webhook(
    agent_name: str,
    request: WebhookRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """
    Universal webhook endpoint for n8n to invoke any agent.

    **Supported agents:**
    - `canvas` - Business Model Canvas generation
    - `leads` - Lead scoring and email generation
    - `copywriter` - Marketing copy generation
    - `visual` - Image generation and editing
    - `video` - Video script and generation
    - `strategy` - Business strategy advice

    **Request Body:**
    - `action`: Agent-specific action (optional)
    - `data`: Input data for the agent
    - `callback_url`: n8n webhook URL for async response (optional)
    - `sync`: If true, wait for result; if false, return job_id (default: true)

    **Examples:**

    Canvas generation:
    ```json
    {
        "data": {
            "description": "A subscription coffee service",
            "enhance": true
        }
    }
    ```

    Lead scoring:
    ```json
    {
        "action": "score",
        "data": {
            "lead": {
                "name": "John Smith",
                "company": "Acme Corp",
                "email": "john@acme.com",
                "status": "Contacted",
                "engagement": "High"
            }
        }
    }
    ```
    """
    orchestrator = get_orchestrator()

    if agent_name not in orchestrator.available_agents:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. Available: {list(orchestrator.available_agents.keys())}"
        )

    try:
        if request.sync:
            # Synchronous execution - return result directly
            result = await orchestrator.invoke(
                agent_name=agent_name,
                action=request.action,
                data=request.data
            )

            return WebhookResponse(
                success=result.get("success", False),
                result=result
            )
        else:
            # Async execution - return job_id, send result to callback
            callback_url = str(request.callback_url) if request.callback_url else None

            job_id = await orchestrator.invoke_async(
                agent_name=agent_name,
                action=request.action,
                data=request.data,
                callback_url=callback_url
            )

            return WebhookResponse(
                success=True,
                job_id=job_id,
                result={"message": "Job queued", "poll_url": f"/api/v1/jobs/{job_id}"}
            )

    except Exception as e:
        error_msg = str(e)

        if request.callback_url and not request.sync:
            background_tasks.add_task(
                send_callback,
                str(request.callback_url),
                {"success": False, "error": error_msg}
            )

        return WebhookResponse(
            success=False,
            error=error_msg
        )


@webhook_router.get("/agents")
async def list_available_agents(
    current_user: str = Depends(get_current_user)
):
    """List all available agents and their supported actions"""
    orchestrator = get_orchestrator()
    return orchestrator.available_agents


# Convenience endpoints for specific agent actions

@webhook_router.post("/canvas/generate")
async def webhook_canvas_generate(
    request: WebhookRequest,
    current_user: str = Depends(get_current_user)
):
    """Direct webhook for canvas generation"""
    return await invoke_agent_webhook(
        "canvas", request, BackgroundTasks(), current_user
    )


@webhook_router.post("/leads/score")
async def webhook_lead_score(
    request: WebhookRequest,
    current_user: str = Depends(get_current_user)
):
    """Direct webhook for lead scoring"""
    request.action = "score"
    return await invoke_agent_webhook(
        "leads", request, BackgroundTasks(), current_user
    )


@webhook_router.post("/leads/email")
async def webhook_lead_email(
    request: WebhookRequest,
    current_user: str = Depends(get_current_user)
):
    """Direct webhook for cold email generation"""
    request.action = "email"
    return await invoke_agent_webhook(
        "leads", request, BackgroundTasks(), current_user
    )


@webhook_router.post("/copywriter/generate")
async def webhook_copy_generate(
    request: WebhookRequest,
    current_user: str = Depends(get_current_user)
):
    """Direct webhook for marketing copy generation"""
    return await invoke_agent_webhook(
        "copywriter", request, BackgroundTasks(), current_user
    )


@webhook_router.post("/visual/generate")
async def webhook_visual_generate(
    request: WebhookRequest,
    current_user: str = Depends(get_current_user)
):
    """Direct webhook for image generation"""
    request.action = "generate"
    return await invoke_agent_webhook(
        "visual", request, BackgroundTasks(), current_user
    )


@webhook_router.post("/video/script")
async def webhook_video_script(
    request: WebhookRequest,
    current_user: str = Depends(get_current_user)
):
    """Direct webhook for video script generation"""
    request.action = "script"
    return await invoke_agent_webhook(
        "video", request, BackgroundTasks(), current_user
    )


@webhook_router.post("/strategy/tips")
async def webhook_strategy_tips(
    request: WebhookRequest,
    current_user: str = Depends(get_current_user)
):
    """Direct webhook for business tips"""
    if "advice_type" not in request.data:
        request.data["advice_type"] = "TIPS"
    return await invoke_agent_webhook(
        "strategy", request, BackgroundTasks(), current_user
    )
