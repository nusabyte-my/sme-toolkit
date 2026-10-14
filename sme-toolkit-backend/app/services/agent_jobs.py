"""In-process durable agent schedules and channel inbox processing; no replay of uncertain sends."""
import asyncio
import logging
from app.api.v1.endpoints.agent_chat import check_agent_schedules
from app.services.channels import process_channel_queue

logger=logging.getLogger(__name__)


async def agent_jobs_loop(poll_seconds=60):
    while True:
        for job in (check_agent_schedules,process_channel_queue):
            try:
                await job()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception('Agent background job failed: %s',job.__name__)
        await asyncio.sleep(poll_seconds)
