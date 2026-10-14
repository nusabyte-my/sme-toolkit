from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.schemas.common import JobResponse
from app.agents.orchestrator import get_orchestrator

router = APIRouter()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get the status of an async job.

    Used for polling video generation and other long-running operations.
    """
    orchestrator = get_orchestrator()
    job = await orchestrator.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(**job)


@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retry a failed job.
    """
    orchestrator = get_orchestrator()
    job = await orchestrator.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "failed":
        raise HTTPException(
            status_code=400,
            detail="Only failed jobs can be retried"
        )

    # Re-invoke the agent with the same parameters
    new_job_id = await orchestrator.invoke_async(
        agent_name=job["agent"],
        action=job["action"],
        data=job.get("input_data", {})
    )

    return {
        "success": True,
        "new_job_id": new_job_id,
        "message": "Job requeued"
    }
