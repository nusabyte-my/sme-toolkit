"""Orchestration API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database import get_db
from app.services.strategy_orchestrator import StrategyOrchestrator
from app.schemas.orchestration import (
    ParallelExecutionRequest,
    SequentialExecutionRequest,
    ParallelExecutionResponse,
    SequentialExecutionResponse,
    JobStatusResponse,
    InteractionLogResponse
)

router = APIRouter(tags=["Orchestration"])


@router.post("/analyze", response_model=dict)
async def orchestrate_analysis(
    business_profile_id: str = Query(..., description="Business profile ID"),
    analysis_type: str = Query("comprehensive", description="Type of analysis"),
    user_request: Optional[str] = Query(None, description="Natural language user request"),
    analysis_depth: str = Query("deep", description="Analysis depth (quick/deep)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Orchestrate comprehensive analysis using multiple advisors.
    
    This endpoint coordinates execution of multiple advisor agents
    and aggregates their results.
    
    - **business_profile_id**: ID of business profile to analyze
    - **analysis_type**: Type of analysis (comprehensive, goals, growth, costing, suggestions)
    - **user_request**: Natural language description of user's request
    - **analysis_depth**: Depth of analysis (quick/deep)
    """
    try:
        orchestrator = StrategyOrchestrator(db)
        
        # Build business context
        business_context = {
            "business_profile_id": business_profile_id,
            "user_request": user_request or f"{analysis_type} analysis",
            "analysis_type": analysis_type,
            "analysis_depth": analysis_depth
        }
        
        # Execute comprehensive analysis
        result = await orchestrator.comprehensive_analysis(
            business_context=business_context
        )
        
        return {
            "analysis_id": result["analysis_id"],
            "results": result["results"],
            "scores": result["scores"],
            "insights": result["insights"],
            "agent_selection": result["agent_selection"],
            "conflicts_detected": result["conflicts"],
            "conflicts_resolved": result["resolved"],
            "status": "completed"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error orchestrating analysis: {str(e)}"
        )


@router.post("/parallel", response_model=ParallelExecutionResponse)
async def execute_parallel(
    request: ParallelExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute multiple agents in parallel.
    
    Runs specified agents concurrently and aggregates results.
    
    - **business_profile_id**: ID of business profile
    - **agents**: List of agents to execute (goal_advisor, growth_advisor, costing_advisor, suggestion_advisor)
    - **input_data**: Input data for agents
    """
    try:
        orchestrator = StrategyOrchestrator(db)
        
        # Load business profile
        from app.database import BusinessProfile
        from sqlalchemy import select
        
        result = await db.execute(
            select(BusinessProfile).where(BusinessProfile.id == request.business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business profile {request.business_profile_id} not found"
            )
        
        # Create shared context
        from app.utils.agent_communication import SharedContext
        context = SharedContext(request.business_profile_id)
        
        # Populate context
        context.set("bmc_data", profile.bmc_data or {})
        context.set("company_name", profile.company_name)
        context.set("industry", profile.industry)
        context.set("business_stage", profile.business_stage)
        
        # Add input data to context
        for key, value in request.input_data.items():
            context.set(key, value)
        
        # Execute agents in parallel
        agent_results = await orchestrator.parallel_execution(
            agents=request.agents,
            context=context
        )
        
        # Calculate execution time
        started_at = datetime.utcnow()
        completed_at = datetime.utcnow()
        total_execution_time = (completed_at - started_at).total_seconds()
        
        # Format results
        results = []
        for agent_name, result in agent_results.items():
            execution_time = result.get("execution_time", 0.0)
            
            results.append({
                "agent_name": agent_name,
                "success": result.get("success", False),
                "result": result if result.get("success", False) else None,
                "error": result.get("error"),
                "execution_time": execution_time
            })
        
        return ParallelExecutionResponse(
            job_id=f"job_{request.business_profile_id}_{int(datetime.utcnow().timestamp())}",
            business_profile_id=request.business_profile_id,
            results=results,
            total_execution_time=total_execution_time,
            started_at=started_at,
            completed_at=completed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing parallel agents: {str(e)}"
        )


@router.post("/sequential", response_model=SequentialExecutionResponse)
async def execute_sequential(
    request: SequentialExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute agents sequentially in a workflow.
    
    Runs agents in specified order, passing output of one
    as input to the next.
    
    - **business_profile_id**: ID of business profile
    - **workflow**: List of workflow steps with agent and data
    - **input_data**: Initial input data
    """
    try:
        orchestrator = StrategyOrchestrator(db)
        
        # Load business profile
        from app.database import BusinessProfile
        from sqlalchemy import select
        
        result = await db.execute(
            select(BusinessProfile).where(BusinessProfile.id == request.business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business profile {request.business_profile_id} not found"
            )
        
        # Create shared context
        from app.utils.agent_communication import SharedContext
        context = SharedContext(request.business_profile_id)
        
        # Populate context
        context.set("bmc_data", profile.bmc_data or {})
        context.set("company_name", profile.company_name)
        context.set("industry", profile.industry)
        context.set("business_stage", profile.business_stage)
        
        # Add input data to context
        for key, value in request.input_data.items():
            context.set(key, value)
        
        # Extract agents from workflow
        agents = [step.get("agent") for step in request.workflow if step.get("agent")]
        
        # Execute agents sequentially
        agent_results = await orchestrator.sequential_execution(
            agents=agents,
            context=context
        )
        
        # Calculate execution time
        started_at = datetime.utcnow()
        completed_at = datetime.utcnow()
        total_execution_time = (completed_at - started_at).total_seconds()
        
        # Format workflow results
        workflow_results = []
        for i, step in enumerate(request.workflow):
            agent_name = step.get("agent", "unknown")
            result = agent_results.get(agent_name, {})
            
            workflow_results.append({
                "step": i + 1,
                "agent": agent_name,
                "success": result.get("success", False),
                "result": result if result.get("success", False) else None,
                "error": result.get("error")
            })
        
        return SequentialExecutionResponse(
            job_id=f"job_{request.business_profile_id}_{int(datetime.utcnow().timestamp())}",
            business_profile_id=request.business_profile_id,
            workflow_results=workflow_results,
            total_execution_time=total_execution_time,
            started_at=started_at,
            completed_at=completed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing sequential workflow: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of an orchestration job.
    
    Returns current status, progress, and results if completed.
    
    - **job_id**: Job ID to check status for
    """
    try:
        orchestrator = StrategyOrchestrator(db)
        
        # Get job status
        status_info = await orchestrator.get_execution_status(job_id)
        
        return JobStatusResponse(
            job_id=status_info["job_id"],
            business_profile_id=job_id.split("_")[0] if "_" in job_id else job_id,
            status=status_info["status"],
            progress=status_info.get("progress", 0.0),
            current_step=status_info.get("current_step"),
            results=status_info.get("results"),
            error=status_info.get("error"),
            started_at=datetime.fromisoformat(status_info["started_at"]) if status_info.get("started_at") else None,
            updated_at=datetime.fromisoformat(status_info["updated_at"]) if status_info.get("updated_at") else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job status: {str(e)}"
        )


@router.get("/interactions", response_model=InteractionLogResponse)
async def get_interaction_log(
    business_profile_id: str = Query(..., description="Business profile ID"),
    analysis_id: Optional[str] = Query(None, description="Analysis ID to filter interactions"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of interactions to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get agent interaction log for a business profile.
    
    Returns history of agent communications and decisions.
    
    - **business_profile_id**: Business profile ID
    - **analysis_id**: Optional analysis ID to filter interactions
    - **limit**: Maximum number of interactions to return (1-100)
    """
    try:
        orchestrator = StrategyOrchestrator(db)
        
        # Get agent interactions
        if analysis_id:
            interactions = await orchestrator.get_agent_interactions(analysis_id)
        else:
            # Get all interactions for business profile
            from app.database import AgentInteraction
            from sqlalchemy import select
            
            result = await db.execute(
                select(AgentInteraction)
                .where(AgentInteraction.business_profile_id == business_profile_id)
                .order_by(AgentInteraction.timestamp.desc())
                .limit(limit)
            )
            
            interaction_records = result.scalars().all()
            
            interactions = [
                {
                    "agent_name": interaction.agent_name,
                    "interaction_type": interaction.interaction_type,
                    "input_data": interaction.input_data,
                    "output_data": interaction.output_data,
                    "decision": interaction.decision,
                    "timestamp": interaction.timestamp.isoformat()
                }
                for interaction in interaction_records
            ]
        
        return InteractionLogResponse(
            business_profile_id=business_profile_id,
            interactions=interactions,
            total=len(interactions)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving interaction log: {str(e)}"
        )


@router.get("/agents")
async def list_available_agents():
    """
    Get list of available advisor agents.
    
    Returns information about all available agents and their capabilities.
    """
    return {
        "agents": [
            {
                "name": "goal_advisor",
                "display_name": "Goal Advisor",
                "description": "Generates SMART goals, aligns with BMC, tracks progress",
                "actions": [
                    "generate_smart_goals",
                    "align_with_bmc",
                    "track_progress",
                    "recommend_goals",
                    "calculate_feasibility"
                ],
                "input_requirements": [
                    "business_context",
                    "bmc_data",
                    "metrics",
                    "resources"
                ]
            },
            {
                "name": "growth_advisor",
                "display_name": "Growth Plan Advisor",
                "description": "Creates growth strategies, identifies opportunities, generates roadmaps",
                "actions": [
                    "create_growth_strategy",
                    "identify_opportunities",
                    "generate_roadmap",
                    "assess_risks",
                    "calculate_growth_potential"
                ],
                "input_requirements": [
                    "business_context",
                    "bmc_data",
                    "market_data",
                    "financial_projections",
                    "growth_metrics",
                    "competitive_landscape"
                ]
            },
            {
                "name": "costing_advisor",
                "display_name": "Costing Advisor",
                "description": "Analyzes costs, develops pricing strategies, identifies optimizations",
                "actions": [
                    "analyze_cost_structure",
                    "develop_pricing_strategy",
                    "identify_optimization_opportunities",
                    "break_even_analysis",
                    "calculate_profitability_metrics"
                ],
                "input_requirements": [
                    "financial_data",
                    "cost_breakdown",
                    "bmc_data",
                    "operational_metrics"
                ]
            },
            {
                "name": "suggestion_advisor",
                "display_name": "Business Suggestion Agent",
                "description": "Suggests opportunities, partnerships, market expansions, innovations",
                "actions": [
                    "suggest_opportunities",
                    "identify_partnerships",
                    "recommend_expansion",
                    "propose_innovations",
                    "calculate_feasibility"
                ],
                "input_requirements": [
                    "business_context",
                    "market_data",
                    "bmc_data",
                    "capabilities",
                    "industry_analysis"
                ]
            }
        ],
        "execution_modes": [
            {
                "mode": "parallel",
                "description": "Execute multiple agents concurrently",
                "use_case": "When agents have no dependencies"
            },
            {
                "mode": "sequential",
                "description": "Execute agents one after another",
                "use_case": "When agents have dependencies or require data from previous agents"
            }
        ]
    }


@router.get("/decision-tree/stats")
async def get_decision_tree_stats(db: AsyncSession = Depends(get_db)):
    """
    Get statistics about decision tree usage.
    
    Returns information about agent selection patterns and execution modes.
    """
    try:
        orchestrator = StrategyOrchestrator(db)
        
        # Get decision tree statistics
        stats = orchestrator.agent_selector.decision_tree.get_decision_statistics()
        
        return {
            "total_decisions": stats["total_decisions"],
            "agent_usage": stats["agent_usage"],
            "execution_mode_usage": stats["execution_mode_usage"],
            "most_used_agent": stats["most_used_agent"],
            "most_used_mode": stats["most_used_mode"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving decision tree stats: {str(e)}"
        )
