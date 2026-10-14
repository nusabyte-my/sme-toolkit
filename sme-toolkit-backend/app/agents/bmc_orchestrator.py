"""BMC Orchestrator - Multi-agent coordination for comprehensive BMC analysis"""

from typing import TypedDict, Optional, Dict, List, Any
from langgraph.graph import StateGraph, START, END
import asyncio

from app.agents.bmc_expert_agent import BMCExpertAgent
from app.agents.growth_agent import GrowthAgent
from app.agents.market_agent import MarketAnalysisAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.operations_agent import OperationsAgent
from app.agents.ideation_agent import IdeationAgent


class BMCOrchestratorState(TypedDict):
    """State for BMC multi-agent orchestration"""
    session_id: str
    user_id: str
    bmc_data: Dict[str, List[str]]
    business_context: Optional[Dict[str, Any]]

    # Agent results
    market_analysis: Optional[Dict[str, Any]]
    financial_analysis: Optional[Dict[str, Any]]
    operations_analysis: Optional[Dict[str, Any]]
    growth_analysis: Optional[Dict[str, Any]]
    ideation_results: Optional[Dict[str, Any]]

    # Synthesis
    growth_score: Optional[Dict[str, Any]]
    strategy_recommendations: Optional[List[str]]
    action_items: Optional[List[Dict[str, Any]]]

    current_phase: str  # 'analysis', 'synthesis', 'complete'
    error: Optional[str]


class BMCOrchestrator:
    """
    Multi-agent orchestrator for comprehensive BMC analysis.
    Coordinates: BMCExpert, Growth, Market, Finance, Operations, Ideation agents
    """

    def __init__(self):
        # Initialize all agents
        self._agents = {
            "bmc_expert": BMCExpertAgent(),
            "growth": GrowthAgent(),
            "market": MarketAnalysisAgent(),
            "finance": FinanceAgent(),
            "operations": OperationsAgent(),
            "ideation": IdeationAgent(),
        }
        self.graph = self._build_orchestration_graph()

    def _build_orchestration_graph(self) -> StateGraph:
        """Build LangGraph workflow for agent coordination"""
        workflow = StateGraph(BMCOrchestratorState)

        # Nodes for orchestration phases
        workflow.add_node("parallel_analysis", self._parallel_analysis)
        workflow.add_node("synthesize_results", self._synthesize_results)
        workflow.add_node("calculate_growth_score", self._calculate_growth_score)
        workflow.add_node("generate_recommendations", self._generate_recommendations)

        # Orchestration flow
        workflow.add_edge(START, "parallel_analysis")
        workflow.add_edge("parallel_analysis", "synthesize_results")
        workflow.add_edge("synthesize_results", "calculate_growth_score")
        workflow.add_edge("calculate_growth_score", "generate_recommendations")
        workflow.add_edge("generate_recommendations", END)

        return workflow.compile()

    async def _parallel_analysis(self, state: BMCOrchestratorState) -> BMCOrchestratorState:
        """Run multiple analysis agents in parallel"""
        try:
            bmc_data = state.get("bmc_data", {})
            business_context = state.get("business_context", {})

            # Run agents in parallel
            market_task = self._agents["market"].invoke({
                "bmc_data": bmc_data,
                "business_context": business_context
            })

            finance_task = self._agents["finance"].invoke({
                "bmc_data": bmc_data
            })

            operations_task = self._agents["operations"].invoke({
                "bmc_data": bmc_data
            })

            # Gather results
            market_result, finance_result, operations_result = await asyncio.gather(
                market_task, finance_task, operations_task,
                return_exceptions=True
            )

            # Handle any exceptions
            if isinstance(market_result, Exception):
                market_result = {"success": False, "error": str(market_result)}
            if isinstance(finance_result, Exception):
                finance_result = {"success": False, "error": str(finance_result)}
            if isinstance(operations_result, Exception):
                operations_result = {"success": False, "error": str(operations_result)}

            # Now run growth and ideation with market analysis context
            growth_task = self._agents["growth"].invoke({
                "bmc_data": bmc_data,
                "market_analysis": market_result if market_result.get("success") else None
            })

            ideation_task = self._agents["ideation"].invoke({
                "bmc_data": bmc_data,
                "market_analysis": market_result if market_result.get("success") else None
            })

            growth_result, ideation_result = await asyncio.gather(
                growth_task, ideation_task,
                return_exceptions=True
            )

            if isinstance(growth_result, Exception):
                growth_result = {"success": False, "error": str(growth_result)}
            if isinstance(ideation_result, Exception):
                ideation_result = {"success": False, "error": str(ideation_result)}

            return {
                **state,
                "market_analysis": market_result,
                "financial_analysis": finance_result,
                "operations_analysis": operations_result,
                "growth_analysis": growth_result,
                "ideation_results": ideation_result,
                "current_phase": "synthesis"
            }
        except Exception as e:
            return {
                **state,
                "error": f"Parallel analysis failed: {str(e)}"
            }

    async def _synthesize_results(self, state: BMCOrchestratorState) -> BMCOrchestratorState:
        """Synthesize results from all agents"""
        try:
            # Collect key insights from each analysis
            action_items = []

            # From market analysis
            market = state.get("market_analysis", {})
            if market.get("success"):
                positioning = market.get("positioning", {})
                if positioning.get("recommended_position"):
                    action_items.append({
                        "category": "Market",
                        "action": f"Position as: {positioning.get('recommended_position')}",
                        "priority": "high"
                    })

            # From financial analysis
            finance = state.get("financial_analysis", {})
            if finance.get("success"):
                for rec in finance.get("financial_recommendations", [])[:2]:
                    action_items.append({
                        "category": "Finance",
                        "action": rec,
                        "priority": "medium"
                    })

            # From operations analysis
            operations = state.get("operations_analysis", {})
            if operations.get("success"):
                for priority in operations.get("operational_priorities", [])[:2]:
                    action_items.append({
                        "category": "Operations",
                        "action": priority,
                        "priority": "medium"
                    })

            # From growth analysis
            growth = state.get("growth_analysis", {})
            if growth.get("success"):
                for action in growth.get("priority_actions", [])[:2]:
                    action_items.append({
                        "category": "Growth",
                        "action": action,
                        "priority": "high"
                    })

            return {
                **state,
                "action_items": action_items
            }
        except Exception as e:
            return {
                **state,
                "error": f"Synthesis failed: {str(e)}"
            }

    async def _calculate_growth_score(self, state: BMCOrchestratorState) -> BMCOrchestratorState:
        """Calculate multi-factor growth score"""
        try:
            # Weight definitions
            WEIGHTS = {
                "bmc_quality": 0.25,
                "strategy_alignment": 0.25,
                "market_readiness": 0.30,
                "execution_capability": 0.20
            }

            # Calculate BMC quality score
            bmc_data = state.get("bmc_data", {})
            filled_blocks = sum(1 for items in bmc_data.values() if items and len(items) > 0)
            total_items = sum(len(items) for items in bmc_data.values() if items)
            bmc_completeness = (filled_blocks / 9) * 100
            bmc_depth = min(100, (total_items / 27) * 100)
            bmc_quality_score = (bmc_completeness * 0.6 + bmc_depth * 0.4)

            # Get market readiness score
            market = state.get("market_analysis", {})
            market_readiness_score = market.get("market_readiness_score", 50) if market.get("success") else 50

            # Get execution capability score
            operations = state.get("operations_analysis", {})
            execution_score = operations.get("execution_capability_score", 50) if operations.get("success") else 50

            # Get financial health as proxy for strategy alignment
            finance = state.get("financial_analysis", {})
            financial_score = finance.get("financial_health_score", 50) if finance.get("success") else 50

            # Calculate weighted overall score
            components = {
                "bmc_quality": {
                    "score": bmc_quality_score,
                    "weight": WEIGHTS["bmc_quality"],
                    "weighted_score": bmc_quality_score * WEIGHTS["bmc_quality"],
                    "factors": [
                        {"name": "Completeness", "score": bmc_completeness, "detail": f"{filled_blocks}/9 blocks filled"},
                        {"name": "Depth", "score": bmc_depth, "detail": f"{total_items} total items"}
                    ],
                    "recommendations": self._get_bmc_recommendations(bmc_data)
                },
                "strategy_alignment": {
                    "score": financial_score,
                    "weight": WEIGHTS["strategy_alignment"],
                    "weighted_score": financial_score * WEIGHTS["strategy_alignment"],
                    "factors": [],
                    "recommendations": []
                },
                "market_readiness": {
                    "score": market_readiness_score,
                    "weight": WEIGHTS["market_readiness"],
                    "weighted_score": market_readiness_score * WEIGHTS["market_readiness"],
                    "factors": [],
                    "recommendations": []
                },
                "execution_capability": {
                    "score": execution_score,
                    "weight": WEIGHTS["execution_capability"],
                    "weighted_score": execution_score * WEIGHTS["execution_capability"],
                    "factors": [],
                    "recommendations": []
                }
            }

            overall_score = sum(comp["weighted_score"] for comp in components.values())

            # Determine grade
            grade = self._score_to_grade(overall_score)

            # Generate summary
            summary = self._generate_score_summary(overall_score, components)

            # Identify improvement priorities
            improvement_priorities = sorted(
                [(name, comp["score"]) for name, comp in components.items()],
                key=lambda x: x[1]
            )[:2]

            growth_score = {
                "overall_score": round(overall_score, 1),
                "grade": grade,
                "components": components,
                "summary": summary,
                "improvement_priorities": [p[0] for p in improvement_priorities]
            }

            return {
                **state,
                "growth_score": growth_score
            }
        except Exception as e:
            return {
                **state,
                "error": f"Growth score calculation failed: {str(e)}"
            }

    def _get_bmc_recommendations(self, bmc_data: Dict[str, List[str]]) -> List[str]:
        """Generate recommendations for BMC improvement"""
        recommendations = []

        block_names = {
            "keyPartners": "Key Partners",
            "keyActivities": "Key Activities",
            "keyResources": "Key Resources",
            "valuePropositions": "Value Propositions",
            "customerRelationships": "Customer Relationships",
            "channels": "Channels",
            "customerSegments": "Customer Segments",
            "costStructure": "Cost Structure",
            "revenueStreams": "Revenue Streams"
        }

        for key, name in block_names.items():
            items = bmc_data.get(key, [])
            if not items:
                recommendations.append(f"Add content to {name} block")
            elif len(items) < 3:
                recommendations.append(f"Expand {name} with more specific items")

        return recommendations[:5]

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90: return "A+"
        if score >= 85: return "A"
        if score >= 80: return "A-"
        if score >= 75: return "B+"
        if score >= 70: return "B"
        if score >= 65: return "B-"
        if score >= 60: return "C+"
        if score >= 55: return "C"
        if score >= 50: return "C-"
        return "D"

    def _generate_score_summary(self, score: float, components: Dict) -> str:
        """Generate human-readable summary of the growth score"""
        if score >= 80:
            return "Your business model shows strong potential across all dimensions. Focus on execution and scaling."
        elif score >= 60:
            return "Good foundation with room for improvement. Address the weaker areas to strengthen your position."
        elif score >= 40:
            return "Several areas need attention. Consider refining your business model before scaling."
        else:
            return "Significant improvements needed. Focus on building a stronger foundation first."

    async def _generate_recommendations(self, state: BMCOrchestratorState) -> BMCOrchestratorState:
        """Generate final strategy recommendations"""
        try:
            recommendations = []

            # From growth analysis
            growth = state.get("growth_analysis", {})
            if growth.get("success"):
                for opp in growth.get("growth_opportunities", [])[:2]:
                    if isinstance(opp, dict):
                        recommendations.append(opp.get("opportunity", str(opp)))
                    else:
                        recommendations.append(str(opp))

            # From ideation
            ideation = state.get("ideation_results", {})
            if ideation.get("success"):
                for idea in ideation.get("innovation_opportunities", [])[:2]:
                    if isinstance(idea, dict):
                        recommendations.append(idea.get("idea", str(idea)))
                    else:
                        recommendations.append(str(idea))

            # Growth score based recommendations
            growth_score = state.get("growth_score", {})
            for priority in growth_score.get("improvement_priorities", []):
                priority_name = priority.replace("_", " ").title()
                recommendations.append(f"Improve {priority_name} to boost overall growth potential")

            return {
                **state,
                "strategy_recommendations": recommendations,
                "current_phase": "complete"
            }
        except Exception as e:
            return {
                **state,
                "error": f"Recommendation generation failed: {str(e)}"
            }

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the BMC orchestrator"""
        initial_state: BMCOrchestratorState = {
            "session_id": input_data.get("session_id", ""),
            "user_id": input_data.get("user_id", ""),
            "bmc_data": input_data.get("bmc_data", {}),
            "business_context": input_data.get("business_context"),
            "market_analysis": None,
            "financial_analysis": None,
            "operations_analysis": None,
            "growth_analysis": None,
            "ideation_results": None,
            "growth_score": None,
            "strategy_recommendations": None,
            "action_items": None,
            "current_phase": "analysis",
            "error": None
        }

        result = await self.graph.ainvoke(initial_state)

        if result.get("error"):
            return {
                "success": False,
                "error": result["error"]
            }

        return {
            "success": True,
            "growth_score": result.get("growth_score"),
            "market_analysis": result.get("market_analysis"),
            "financial_analysis": result.get("financial_analysis"),
            "operations_analysis": result.get("operations_analysis"),
            "growth_analysis": result.get("growth_analysis"),
            "ideation_results": result.get("ideation_results"),
            "strategy_recommendations": result.get("strategy_recommendations", []),
            "action_items": result.get("action_items", [])
        }


# Singleton instance
_bmc_orchestrator = None


def get_bmc_orchestrator() -> BMCOrchestrator:
    """Get singleton BMC orchestrator instance"""
    global _bmc_orchestrator
    if _bmc_orchestrator is None:
        _bmc_orchestrator = BMCOrchestrator()
    return _bmc_orchestrator
