"""Strategy Orchestrator Service - Central coordinator for agent orchestration"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import asyncio
import logging
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import (
    BusinessProfile,
    # StrategyAnalysis,  # TODO: Model not defined in database.py
    # ScoreRecord,  # TODO: Model not defined in database.py
    # AnalysisStatus,  # TODO: Model not defined in database.py
    AgentInteraction,
)
from app.services.scoring_service import ScoringService
from app.services.analytics_service import AnalyticsService
from app.services.goal_service import GoalService
from app.services.growth_service import GrowthService
from app.services.costing_service import CostingService
from app.services.suggestion_service import SuggestionService
from app.agents.goal_advisor_agent import GoalAdvisorAgent
from app.agents.growth_plan_advisor_agent import GrowthPlanAdvisorAgent
from app.agents.costing_advisor_agent import CostingAdvisorAgent
from app.agents.business_suggestion_agent import BusinessSuggestionAgent
from app.utils.agent_communication import (
    CommunicationProtocol,
    SharedContext,
    DataTransformer,
    MessageType,
)
from app.utils.conflict_resolution import ConflictResolver, ConflictResolutionStrategy
from app.utils.decision_tree import AgentSelector

logger = logging.getLogger(__name__)


class StrategyOrchestrator:
    """
    Central coordinator for all strategy advisor agents.
    Manages agent execution, data flow, and result aggregation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.scoring_service = ScoringService(db)
        self.analytics_service = AnalyticsService(db)

        # Initialize services
        self.goal_service = GoalService(db)
        self.growth_service = GrowthService(db)
        self.costing_service = CostingService(db)
        self.suggestion_service = SuggestionService(db)

        # Initialize agents
        self.goal_advisor = GoalAdvisorAgent(self.goal_service)
        self.growth_advisor = GrowthPlanAdvisorAgent(self.growth_service)
        self.costing_advisor = CostingAdvisorAgent(self.costing_service)
        self.suggestion_advisor = BusinessSuggestionAgent(self.suggestion_service)

        # Initialize utilities
        self.communication = CommunicationProtocol()
        self.conflict_resolver = ConflictResolver()
        self.agent_selector = AgentSelector()

        # Job tracking
        self.jobs: Dict[str, Dict[str, Any]] = {}

        # Result cache
        self.result_cache: Dict[str, Dict[str, Any]] = {}

    async def comprehensive_analysis(
        self, business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute comprehensive analysis using all advisors.

        Args:
            business_context: Dictionary containing business profile ID and context data

        Returns:
            Dictionary containing analysis_id, results, scores, and insights
        """
        business_profile_id = business_context.get("business_profile_id")
        if not business_profile_id:
            raise ValueError("business_profile_id is required")

        logger.info(
            f"Starting comprehensive analysis for profile {business_profile_id}"
        )

        # Load business profile data
        profile = await self._load_profile(business_profile_id)
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")

        # Create shared context
        shared_context = self.communication.create_context(business_profile_id)

        # Populate context with business data
        self._populate_context(shared_context, profile, business_context)

        # Determine which agents to run
        selection = self.agent_selector.select_agents(
            user_request=business_context.get("user_request", "comprehensive analysis"),
            business_context=self._build_selection_context(profile, business_context),
        )

        logger.info(f"Selected agents: {[a.value for a in selection['agents']]}")
        logger.info(f"Execution mode: {selection['execution_mode']}")

        # Execute agents based on mode
        if selection["execution_mode"] == "parallel":
            agent_results = await self.parallel_execution(
                agents=[a.value for a in selection["agents"]], context=shared_context
            )
        else:
            agent_results = await self.sequential_execution(
                agents=[a.value for a in selection["agents"]], context=shared_context
            )

        # Aggregate results
        aggregated = self.aggregate_results(agent_results)

        # Detect and resolve conflicts
        conflicts = self.conflict_resolver.detect_conflicts(aggregated)
        if conflicts:
            logger.info(f"Detected {len(conflicts)} conflicts, resolving...")
            resolution = self.conflict_resolver.resolve_conflicts(
                conflicts, strategy=ConflictResolutionStrategy.WEIGHTED_SCORING
            )
            aggregated["conflict_resolution"] = resolution

        # Calculate scores
        scores = await self.scoring_service.calculate_all_scores(profile, aggregated)

        # Generate insights
        insights = await self._generate_insights(profile, aggregated, scores)

        # Store analysis
        analysis_id = await self._store_analysis(
            business_profile_id, aggregated, scores, insights, selection
        )

        # Store agent interactions
        await self._store_agent_interactions(
            business_profile_id, shared_context, agent_results
        )

        # Cache results
        self.result_cache[analysis_id] = {
            "results": aggregated,
            "scores": scores,
            "insights": insights,
        }

        logger.info(f"Comprehensive analysis completed: {analysis_id}")

        return {
            "analysis_id": analysis_id,
            "results": aggregated,
            "scores": scores,
            "insights": insights,
            "agent_selection": selection,
            "conflicts": len(conflicts),
            "resolved": len(conflicts) > 0,
        }

    async def analyze_comprehensive(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for comprehensive_analysis"""
        return await self.comprehensive_analysis(business_context)

    async def _execute_agents_parallel(self, *args, **kwargs) -> Dict[str, Any]:
        """Alias for parallel_execution"""
        return await self.parallel_execution(*args, **kwargs)

    def _aggregate_results(self, *args, **kwargs) -> Dict[str, Any]:
        """Alias for aggregate_results"""
        return self.aggregate_results(*args, **kwargs)

    async def parallel_execution(
        self, agents: List[str], context: SharedContext
    ) -> Dict[str, Any]:
        """
        Execute multiple agents in parallel.

        Args:
            agents: List of agent names to execute
            context: Shared context object

        Returns:
            Dictionary with results from all agents
        """
        logger.info(f"Executing agents in parallel: {agents}")

        # Create job ID
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "status": "running",
            "agents": agents,
            "started_at": datetime.utcnow(),
            "results": {},
        }

        # Prepare tasks
        tasks = []
        for agent_name in agents:
            task = self._execute_agent(agent_name, context)
            tasks.append(task)

        # Execute in parallel with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=300.0,  # 5 minute timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Parallel execution timed out for job {job_id}")
            # Return partial results
            results = [None] * len(agents)

        # Process results
        agent_results = {}
        for i, result in enumerate(results):
            agent_name = agents[i]

            if isinstance(result, Exception):
                logger.error(f"Agent {agent_name} failed: {result}")
                agent_results[agent_name] = {
                    "success": False,
                    "error": str(result),
                    "agent_name": agent_name,
                }
            else:
                agent_results[agent_name] = result

        # Update job status
        self.jobs[job_id]["status"] = "completed"
        self.jobs[job_id]["completed_at"] = datetime.utcnow()
        self.jobs[job_id]["results"] = agent_results

        logger.info(f"Parallel execution completed: {job_id}")

        return agent_results

    async def sequential_execution(
        self, agents: List[str], context: SharedContext
    ) -> Dict[str, Any]:
        """
        Execute agents sequentially in order.

        Args:
            agents: List of agent names to execute in order
            context: Shared context object

        Returns:
            Dictionary with results from all agents
        """
        logger.info(f"Executing agents sequentially: {agents}")

        # Create job ID
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "status": "running",
            "agents": agents,
            "started_at": datetime.utcnow(),
            "results": {},
            "current_step": 0,
        }

        agent_results = {}

        # Execute agents one by one
        for i, agent_name in enumerate(agents):
            logger.info(f"Executing agent {i + 1}/{len(agents)}: {agent_name}")

            # Update job status
            self.jobs[job_id]["current_step"] = i + 1

            # Execute agent
            try:
                result = await self._execute_agent(agent_name, context)
                agent_results[agent_name] = result

                # Update context with agent results
                context.update_agent_state(
                    agent_name,
                    {"result": result, "completed_at": datetime.utcnow().isoformat()},
                )

                # Pass results to next agent via context
                if result and result.get("success"):
                    context.set(f"{agent_name}_result", result)

            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}", exc_info=True)
                agent_results[agent_name] = {
                    "success": False,
                    "error": str(e),
                    "agent_name": agent_name,
                }

                # Decide whether to continue or stop
                if not self._should_continue_on_failure(agent_name):
                    logger.warning(
                        f"Stopping sequential execution due to critical agent failure"
                    )
                    break

        # Update job status
        self.jobs[job_id]["status"] = "completed"
        self.jobs[job_id]["completed_at"] = datetime.utcnow()
        self.jobs[job_id]["results"] = agent_results

        logger.info(f"Sequential execution completed: {job_id}")

        return agent_results

    def aggregate_results(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from multiple agents.

        Args:
            agent_results: List of agent result dictionaries

        Returns:
            Aggregated results dictionary
        """
        logger.info("Aggregating agent results")

        aggregated = {
            "goals": None,
            "growth": None,
            "costing": None,
            "suggestions": None,
            "aggregated_at": datetime.utcnow().isoformat(),
            "agent_count": len(agent_results),
            "successful_agents": 0,
            "failed_agents": 0,
        }

        # Process each agent result
        for result in agent_results:
            if not isinstance(result, dict):
                continue

            agent_name = result.get("agent_name", "unknown")

            if result.get("success", False):
                aggregated["successful_agents"] += 1

                # Store result based on agent type
                if "goal" in agent_name.lower():
                    aggregated["goals"] = result
                elif "growth" in agent_name.lower():
                    aggregated["growth"] = result
                elif "costing" in agent_name.lower() or "cost" in agent_name.lower():
                    aggregated["costing"] = result
                elif "suggestion" in agent_name.lower():
                    aggregated["suggestions"] = result
            else:
                aggregated["failed_agents"] += 1

        # Generate aggregation summary
        aggregated["summary"] = {
            "total_agents": len(agent_results),
            "successful": aggregated["successful_agents"],
            "failed": aggregated["failed_agents"],
            "success_rate": aggregated["successful_agents"] / len(agent_results)
            if agent_results
            else 0,
        }

        logger.info(
            f"Aggregation complete: {aggregated['successful_agents']}/{len(agent_results)} successful"
        )

        return aggregated

    def resolve_conflicts(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle conflicting recommendations from agents.

        Args:
            results: Aggregated results from multiple agents

        Returns:
            Conflict resolution results
        """
        logger.info("Resolving conflicts in agent results")

        # Detect conflicts
        conflicts = self.conflict_resolver.detect_conflicts(results)

        if not conflicts:
            return {"conflicts_detected": 0, "conflicts_resolved": 0, "resolutions": {}}

        # Resolve conflicts
        resolution = self.conflict_resolver.resolve_conflicts(
            conflicts, strategy=ConflictResolutionStrategy.WEIGHTED_SCORING
        )

        return {
            "conflicts_detected": len(conflicts),
            "conflicts_resolved": resolution["resolved_conflicts"],
            "strategy_used": resolution["strategy_used"],
            "resolutions": resolution["resolutions"],
        }

    async def get_execution_status(self, job_id: str) -> Dict[str, Any]:
        """
        Track execution progress of a job.

        Args:
            job_id: Job ID to check

        Returns:
            Job status information
        """
        job = self.jobs.get(job_id)

        if not job:
            return {"job_id": job_id, "status": "not_found", "error": "Job not found"}

        # Calculate progress
        total_agents = len(job.get("agents", []))
        current_step = job.get("current_step", 0)
        progress = (current_step / total_agents * 100) if total_agents > 0 else 0

        if job["status"] == "completed":
            progress = 100.0

        return {
            "job_id": job_id,
            "status": job["status"],
            "progress": round(progress, 2),
            "current_step": current_step,
            "total_steps": total_agents,
            "started_at": job.get("started_at").isoformat()
            if job.get("started_at")
            else None,
            "updated_at": job.get("updated_at").isoformat()
            if job.get("updated_at")
            else None,
            "completed_at": job.get("completed_at").isoformat()
            if job.get("completed_at")
            else None,
            "results": job.get("results") if job["status"] == "completed" else None,
        }

    async def get_agent_interactions(self, analysis_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve agent communication history.

        Args:
            analysis_id: Analysis ID to get interactions for

        Returns:
            List of agent interactions
        """
        # Query database for interactions
        result = await self.db.execute(
            select(AgentInteraction)
            .where(AgentInteraction.business_profile_id == str(analysis_id))
            .order_by(AgentInteraction.timestamp.desc())
            .limit(100)
        )

        interactions = result.scalars().all()

        return [
            {
                "id": interaction.id,
                "agent_name": interaction.agent_name,
                "interaction_type": interaction.interaction_type,
                "input_data": interaction.input_data,
                "output_data": interaction.output_data,
                "decision": interaction.decision,
                "timestamp": interaction.timestamp.isoformat(),
            }
            for interaction in interactions
        ]

    async def _execute_agent(
        self, agent_name: str, context: SharedContext
    ) -> Dict[str, Any]:
        """
        Execute a single agent with appropriate input data.

        Args:
            agent_name: Name of agent to execute
            context: Shared context object

        Returns:
            Agent execution result
        """
        logger.info(f"Executing agent: {agent_name}")

        # Transform context data for this agent
        if agent_name == "goal_advisor":
            input_data = DataTransformer.transform_for_goal_advisor(context)
            action = "generate_smart_goals"
            agent = self.goal_advisor
        elif agent_name == "growth_advisor":
            input_data = DataTransformer.transform_for_growth_advisor(context)
            action = "create_growth_strategy"
            agent = self.growth_advisor
        elif agent_name == "costing_advisor":
            input_data = DataTransformer.transform_for_costing_advisor(context)
            action = "analyze_cost_structure"
            agent = self.costing_advisor
        elif agent_name == "suggestion_advisor":
            input_data = DataTransformer.transform_for_suggestion_advisor(context)
            action = "suggest_opportunities"
            agent = self.suggestion_advisor
        else:
            return {
                "success": False,
                "error": f"Unknown agent: {agent_name}",
                "agent_name": agent_name,
            }

        # Add action to input data
        input_data["action"] = action

        # Send message to communication protocol
        self.communication.send_message(
            sender="orchestrator",
            recipient=agent_name,
            message_type=MessageType.REQUEST,
            content={"action": action, "input_data": input_data},
            business_profile_id=context.business_profile_id,
        )

        # Execute agent
        start_time = datetime.utcnow()
        result = await agent.invoke(input_data)
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        # Add execution metadata
        result["agent_name"] = agent_name
        result["execution_time"] = execution_time

        # Send response message
        self.communication.send_message(
            sender=agent_name,
            recipient="orchestrator",
            message_type=MessageType.RESPONSE,
            content={"result": result},
            business_profile_id=context.business_profile_id,
        )

        logger.info(f"Agent {agent_name} completed in {execution_time:.2f}s")

        return result

    async def _load_profile(
        self, business_profile_id: str
    ) -> Optional[BusinessProfile]:
        """Load business profile from database"""
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        return result.scalar_one_or_none()

    def _populate_context(
        self,
        context: SharedContext,
        profile: BusinessProfile,
        business_context: Dict[str, Any],
    ) -> None:
        """Populate shared context with business data"""
        # Basic business info
        context.set("company_name", profile.company_name)
        context.set("industry", profile.industry)
        context.set("business_stage", profile.business_stage)

        # BMC data
        if profile.bmc_data:
            context.set("bmc_data", profile.bmc_data)

        # Business context
        if profile.business_context:
            context.set("business_context", profile.business_context)

        # Additional context from request
        for key, value in business_context.items():
            if key != "business_profile_id":
                context.set(key, value)

        # Strategy settings
        if profile.strategy_settings:
            context.set("strategy_settings", profile.strategy_settings)

    def _build_selection_context(
        self, profile: BusinessProfile, business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context for agent selection"""
        return {
            "bmc_data": profile.bmc_data or {},
            "market_data": business_context.get("market_data", {}),
            "financial_data": business_context.get("financial_data", {}),
            "business_stage": profile.business_stage or "growth",
            "analysis_depth": business_context.get("analysis_depth", "deep"),
            "resource_constraints": business_context.get("resource_constraints", 0.0),
            "time_constraints": business_context.get("time_constraints", 0.0),
        }

    def _should_continue_on_failure(self, agent_name: str) -> bool:
        """Determine if execution should continue after agent failure"""
        # Critical agents that should stop execution on failure
        critical_agents = ["goal_advisor"]

        return agent_name not in critical_agents

    async def _generate_insights(
        self, profile: BusinessProfile, results: Dict[str, Any], scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from analysis results and scores"""
        insights = {
            "overall_assessment": self._generate_overall_assessment(scores),
            "key_findings": self._extract_key_findings(results),
            "recommendations": self._generate_recommendations(scores, results),
            "priority_actions": self._determine_priority_actions(scores, results),
            "generated_at": datetime.utcnow().isoformat(),
        }

        return insights

    def _generate_overall_assessment(self, scores: Dict[str, Any]) -> str:
        """Generate overall business assessment based on scores"""
        if not scores:
            return "Insufficient data for assessment"

        # Calculate average score
        score_values = [
            s.get("overall_score", 0)
            for s in scores.values()
            if isinstance(s, dict) and "overall_score" in s
        ]

        if not score_values:
            return "No scores available for assessment"

        avg_score = sum(score_values) / len(score_values)

        # Generate assessment based on score
        if avg_score >= 90:
            return "Excellent: Business is performing exceptionally well across all metrics"
        elif avg_score >= 80:
            return "Very Good: Strong performance with minor areas for improvement"
        elif avg_score >= 70:
            return "Good: Solid performance with some areas needing attention"
        elif avg_score >= 60:
            return (
                "Fair: Adequate performance but requires improvement in several areas"
            )
        else:
            return "Poor: Significant issues requiring immediate attention"

    def _extract_key_findings(self, results: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis results"""
        findings = []

        # Extract from goals
        if results.get("goals") and results["goals"].get("success"):
            goal_analysis = results["goals"].get("goal_analysis", {})
            findings.append(
                f"Generated {goal_analysis.get('total_goals', 0)} SMART goals"
            )

            by_category = goal_analysis.get("by_category", {})
            if by_category:
                top_category = max(by_category.items(), key=lambda x: x[1])[0]
                findings.append(f"Primary goal category: {top_category}")

        # Extract from growth
        if results.get("growth") and results["growth"].get("success"):
            growth_plan = results["growth"].get("growth_plan", {})
            opportunities = growth_plan.get("growth_opportunities", [])
            findings.append(f"Identified {len(opportunities)} growth opportunities")

            if opportunities:
                top_opp = max(opportunities, key=lambda x: x.get("confidence_score", 0))
                findings.append(
                    f"Top growth opportunity: {top_opp.get('title', 'Unknown')}"
                )

        # Extract from costing
        if results.get("costing") and results["costing"].get("success"):
            cost_structure = results["costing"].get("cost_structure", {})
            optimizations = cost_structure.get("optimization_opportunities", [])
            findings.append(
                f"Identified {len(optimizations)} cost optimization opportunities"
            )

            if optimizations:
                total_savings = sum(
                    opt.get("savings_percentage", 0) for opt in optimizations
                )
                findings.append(f"Potential cost savings: {total_savings:.1f}%")

        # Extract from suggestions
        if results.get("suggestions") and results["suggestions"].get("success"):
            suggestions = results["suggestions"].get("business_suggestions", {})
            opportunities = suggestions.get("new_opportunities", [])
            findings.append(f"Generated {len(opportunities)} business suggestions")

        return findings

    def _generate_recommendations(
        self, scores: Dict[str, Any], results: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on scores and results"""
        recommendations = []

        # Analyze scores for recommendations
        if scores:
            for score_type, score_data in scores.items():
                if isinstance(score_data, dict):
                    overall_score = score_data.get("overall_score", 0)

                    if overall_score < 70:
                        recommendations.append(
                            f"Improve {score_type.replace('_', ' ')}: Current score {overall_score:.0f}/100"
                        )

        # Add specific recommendations from results
        if results.get("goals") and results["goals"].get("success"):
            goal_analysis = results["goals"].get("goal_analysis", {})
            recommendations.extend(goal_analysis.get("recommendations", []))

        if results.get("costing") and results["costing"].get("success"):
            cost_structure = results["costing"].get("cost_structure", {})
            recommendations.extend(cost_structure.get("recommendations", []))

        return recommendations[:10]  # Limit to top 10

    def _determine_priority_actions(
        self, scores: Dict[str, Any], results: Dict[str, Any]
    ) -> List[str]:
        """Determine priority actions based on scores and results"""
        priority_actions = []

        # Find lowest scoring areas
        if scores:
            sorted_scores = sorted(
                [
                    (k, v.get("overall_score", 0))
                    for k, v in scores.items()
                    if isinstance(v, dict)
                ],
                key=lambda x: x[1],
            )

            if sorted_scores:
                lowest_area, lowest_score = sorted_scores[0]
                if lowest_score < 70:
                    priority_actions.append(
                        f"Priority: Address {lowest_area.replace('_', ' ')} (Score: {lowest_score:.0f})"
                    )

        # Add specific priority actions from results
        if results.get("growth") and results["growth"].get("success"):
            growth_plan = results["growth"].get("growth_plan", {})
            channels = growth_plan.get("growth_channels", [])

            high_priority_channels = [
                ch for ch in channels if ch.get("priority") == "high"
            ]

            for channel in high_priority_channels[:3]:
                priority_actions.append(
                    f"Priority: {channel.get('channel', 'Unknown')} - {channel.get('expected_impact', '')}"
                )

        return priority_actions[:5]  # Limit to top 5

    async def _store_analysis(
        self,
        business_profile_id: str,
        results: Dict[str, Any],
        scores: Dict[str, Any],
        insights: Dict[str, Any],
        selection: Dict[str, Any],
    ) -> str:
        """Store analysis results in database"""
        analysis = StrategyAnalysis(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            analysis_type="comprehensive",
            results=results,
            scores=scores,
            insights=insights,
            status=AnalysisStatus.COMPLETED,
        )

        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)

        return analysis.id

    async def _store_agent_interactions(
        self,
        business_profile_id: str,
        context: SharedContext,
        agent_results: Dict[str, Any],
    ) -> None:
        """Store agent interactions in database"""
        for agent_name, result in agent_results.items():
            interaction = AgentInteraction(
                id=str(uuid.uuid4()),
                business_profile_id=business_profile_id,
                agent_name=agent_name,
                interaction_type="analysis",
                input_data=context.get_agent_state(agent_name),
                output_data=result,
                decision={"success": result.get("success", False)},
                timestamp=datetime.utcnow(),
            )

            self.db.add(interaction)

        await self.db.commit()

    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific analysis by ID"""
        result = await self.db.execute(
            select(StrategyAnalysis).where(StrategyAnalysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            return None

        return {
            "id": analysis.id,
            "business_profile_id": analysis.business_profile_id,
            "analysis_type": analysis.analysis_type,
            "results": analysis.results,
            "scores": analysis.scores,
            "insights": analysis.insights,
            "status": analysis.status,
            "created_at": analysis.created_at.isoformat(),
            "updated_at": analysis.updated_at.isoformat(),
        }

    async def list_analyses(
        self, business_profile_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List all analyses for a business profile"""
        result = await self.db.execute(
            select(StrategyAnalysis)
            .where(StrategyAnalysis.business_profile_id == business_profile_id)
            .order_by(StrategyAnalysis.created_at.desc())
            .limit(limit)
        )
        analyses = result.scalars().all()

        return [
            {
                "id": analysis.id,
                "analysis_type": analysis.analysis_type,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat(),
            }
            for analysis in analyses
        ]
