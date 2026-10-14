from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager, suppress
import asyncio

from app.config import settings
from app.database import init_db
from app.api.v1.router import api_router
from app.api.v1.webhooks import webhook_router
from app.api.v1.endpoints.channels import webhook_router as channel_webhooks
from app.api.v1.endpoints.pilot_requests import router as pilot_requests
from app.services.agent_jobs import agent_jobs_loop
from app.api.v1.auth_routes import auth_router
from app.api.v1.endpoints.payments import router as payments_router
from app.middleware.ads_body_limit import AdsBodyLimit
from app.agents.workflow_engine import automation_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    await init_db()
    scheduler = asyncio.create_task(automation_loop(settings.automation_poll_seconds)) if settings.automation_scheduler_enabled else None
    agent_jobs = asyncio.create_task(agent_jobs_loop(settings.automation_poll_seconds)) if settings.automation_scheduler_enabled else None
    try:
        yield
    finally:
        if agent_jobs:
            agent_jobs.cancel()
            with suppress(asyncio.CancelledError):
                await agent_jobs
        if scheduler:
            scheduler.cancel()
            with suppress(asyncio.CancelledError):
                await scheduler


app = FastAPI(
    title="SME Toolkit API",
    description="Business command center API — AI-powered strategy, content, leads, and growth tools for small and medium enterprises",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(AdsBodyLimit)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, prefix="/api/v1")
app.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])
app.include_router(channel_webhooks, prefix='/channels/webhook', tags=['Verified Channel Webhooks'])
app.include_router(pilot_requests, prefix='/api/v1/pilot-requests', tags=['Pilot Enquiries'])
app.include_router(payments_router, prefix="/api/v1", tags=["Payments"])


@app.get("/")
async def root():
    return {
        "name": "SME Toolkit API",
        "version": "2.0.0",
        "status": "running",
        "agents": [
            "canvas",
            "leads",
            "copywriter",
            "visual",
            "video",
            "strategy"
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
