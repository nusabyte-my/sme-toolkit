from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.canvas_agent import CanvasAgent
from app.agents.lead_agent import LeadAgent
from app.agents.copywriter_agent import CopywriterAgent
from app.agents.visual_agent import VisualAgent
from app.agents.video_agent import VideoAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.prompt_genie_agent import PromptGenieAgent
from app.agents.ideation_agent import IdeationAgent
from app.database import Job, JobStatus, async_session


class AgentOrchestrator:
    """Orchestrates all LangGraph agents for the SME Toolkit"""

    def __init__(self):
        # Initialize all agents
        self._agents = {
            "canvas": CanvasAgent(),
            "leads": LeadAgent(),
            "copywriter": CopywriterAgent(),
            "visual": VisualAgent(),
            "video": VideoAgent(),
            "strategy": StrategyAgent(),
            "prompt_genie": PromptGenieAgent(),
            "ideation": IdeationAgent(),
        }

    @property
    def available_agents(self) -> Dict[str, Any]:
        """Return available agents and their actions"""
        return {
            name: {
                "name": agent.name,
                "actions": agent.get_actions()
            }
            for name, agent in self._agents.items()
        }

    def get_agent(self, agent_name: str):
        """Get an agent by name"""
        return self._agents.get(agent_name)

    async def invoke(
        self,
        agent_name: str,
        action: Optional[str] = None,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Invoke an agent synchronously.

        Args:
            agent_name: Name of the agent to invoke
            action: Optional action for the agent
            data: Input data for the agent

        Returns:
            Agent result dictionary
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found"
            }

        # Merge action into data if provided
        input_data = data or {}
        if action:
            input_data["action"] = action

        try:
            result = await agent.invoke(input_data)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent execution failed: {str(e)}"
            }

    async def invoke_async(
        self,
        agent_name: str,
        action: Optional[str] = None,
        data: Dict[str, Any] = None,
        callback_url: Optional[str] = None
    ) -> str:
        """
        Invoke an agent asynchronously with job tracking.

        Args:
            agent_name: Name of the agent to invoke
            action: Optional action for the agent
            data: Input data for the agent
            callback_url: URL to call when job completes

        Returns:
            Job ID for tracking
        """
        job_id = str(uuid.uuid4())

        async with async_session() as session:
            job = Job(
                id=job_id,
                agent=agent_name,
                action=action or "default",
                input_data=data or {},
                status=JobStatus.PENDING,
                callback_url=callback_url
            )
            session.add(job)
            await session.commit()

        # In a production system, this would queue the job
        # For now, we'll execute it directly in the background
        import asyncio
        asyncio.create_task(self._process_job(job_id))

        return job_id

    async def _process_job(self, job_id: str):
        """Process an async job"""
        async with async_session() as session:
            # Get the job
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                return

            # Update status to processing
            job.status = JobStatus.PROCESSING
            job.updated_at = datetime.utcnow()
            await session.commit()

            try:
                # Execute the agent
                agent_result = await self.invoke(
                    agent_name=job.agent,
                    action=job.action,
                    data=job.input_data
                )

                # Update job with result
                if agent_result.get("success"):
                    job.status = JobStatus.COMPLETED
                    job.result = agent_result
                else:
                    job.status = JobStatus.FAILED
                    job.error = agent_result.get("error", "Unknown error")

            except Exception as e:
                job.status = JobStatus.FAILED
                job.error = str(e)

            job.updated_at = datetime.utcnow()
            await session.commit()

            # Send callback if URL provided
            if job.callback_url:
                await self._send_callback(job)

    async def _send_callback(self, job: Job):
        """Send result to callback URL"""
        import httpx

        payload = {
            "job_id": job.id,
            "agent": job.agent,
            "action": job.action,
            "status": job.status.value,
            "result": job.result,
            "error": job.error
        }

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    job.callback_url,
                    json=payload,
                    timeout=30.0
                )
        except Exception as e:
            # Log the error but don't fail the job
            print(f"Callback failed for job {job.id}: {e}")

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an async job"""
        async with async_session() as session:
            result = await session.execute(
                select(Job).where(Job.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                return None

            return {
                "job_id": job.id,
                "agent": job.agent,
                "action": job.action,
                "status": job.status.value,
                "result": job.result,
                "error": job.error,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat()
            }


# Singleton instance
_orchestrator = None


def get_orchestrator() -> AgentOrchestrator:
    """Get singleton orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
