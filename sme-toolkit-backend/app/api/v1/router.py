from fastapi import APIRouter, Depends
from app.auth import require_business_access

from app.api.v1.endpoints import (
    owner,
    ads,
    workspace,
    ad_optimization,
    bookkeeping,
    hr,
    billing,
    agent_chat,
    channels,
    canvas,
    leads,
    copywriter,
    visual,
    video,
    strategy,
    jobs,
    bmc_chat,
    strategy_advisor,
    goals,
    growth_plans,
    costing,
    suggestions,
    analytics,
    scoring,
    orchestration,
    sales,
    profiles,
    subscription,
    providers,
    models,
    tokens,
    prompt_genie,
    ideation,
    ideation_templates,
    workflows,
    seo,
    market_research,
    billing_cycles,
    quickwins,
)

api_router = APIRouter(dependencies=[Depends(require_business_access)])

# Owner portal replaces simulated agent deployments, commerce and social endpoints.
api_router.include_router(owner.router, prefix='/owner', tags=['Owner Portal'])
api_router.include_router(ads.router, prefix='/ads', tags=['Ads Studio'])
api_router.include_router(workspace.router, prefix='/workspace', tags=['Business Workspace'])
api_router.include_router(ad_optimization.router, prefix='/ad-optimization', tags=['Ad Optimization'])
api_router.include_router(bookkeeping.router, prefix='/bookkeeping', tags=['Bookkeeping'])
api_router.include_router(hr.router, prefix='/hr', tags=['HR'])
api_router.include_router(billing.router, prefix='/billing', tags=['Quotations and Invoices'])
api_router.include_router(agent_chat.router, prefix='/agent-chat', tags=['Agent Chat'])
api_router.include_router(channels.router, prefix='/channels', tags=['Agent Channels'])
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflow Automation"])
api_router.include_router(seo.router, prefix="/seo", tags=["SEO Studio"])
api_router.include_router(market_research.router, prefix="/market-research", tags=["Market Research"])
api_router.include_router(billing_cycles.router, prefix="/billing-v2", tags=["Multi-Cycle Billing"])
api_router.include_router(quickwins.router, prefix="/quickwins", tags=["QuickWins & BYOK"])

# Core tools
api_router.include_router(canvas.router, prefix="/canvas", tags=["Business Canvas"])
api_router.include_router(leads.router, prefix="/leads", tags=["Lead Manager"])
api_router.include_router(sales.router, prefix="/sales", tags=["Sales Tracking"])
api_router.include_router(copywriter.router, prefix="/copywriter", tags=["Copywriter"])
api_router.include_router(visual.router, prefix="/visual", tags=["Visual Generator"])
api_router.include_router(video.router, prefix="/video", tags=["Video Generator"])
api_router.include_router(ideation.router, prefix="/ideation", tags=["Ideation"])
api_router.include_router(ideation_templates.router, prefix="/ideation", tags=["Ideation Templates"])
api_router.include_router(
    strategy.router, prefix="/strategy", tags=["Strategy Advisor"]
)
api_router.include_router(jobs.router, prefix="/jobs", tags=["Job Queue"])
api_router.include_router(prompt_genie.router, prefix="/prompt-genie", tags=["Prompt Genie"])

# Enhanced BMC system
api_router.include_router(bmc_chat.router, prefix="/bmc", tags=["BMC Chat & Analysis"])

# Strategy Advisor System (Phase 1)
api_router.include_router(
    strategy_advisor.router, prefix="/strategy-advisor", tags=["Strategy Advisor"]
)
api_router.include_router(goals.router, prefix="/goals", tags=["Goals"])
api_router.include_router(
    growth_plans.router, prefix="/growth-plans", tags=["Growth Plans"]
)
api_router.include_router(costing.router, prefix="/costing", tags=["Costing"])
api_router.include_router(
    suggestions.router, prefix="/suggestions", tags=["Suggestions"]
)
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(scoring.router, prefix="/scoring", tags=["Scoring"])
api_router.include_router(
    orchestration.router, prefix="/orchestration", tags=["Orchestration"]
)

# Enhanced Data Profiling
api_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])

# Multi-Provider AI System
api_router.include_router(
    subscription.router, prefix="/subscription", tags=["Subscription"]
)
api_router.include_router(providers.router, prefix="/providers", tags=["AI Providers"])
api_router.include_router(models.router, tags=["Models"])

# Token Billing System
api_router.include_router(tokens.router, prefix="/tokens", tags=["Tokens"])
