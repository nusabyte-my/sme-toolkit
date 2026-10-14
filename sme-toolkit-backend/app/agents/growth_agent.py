"""Growth Agent - Analyzes growth potential and scaling opportunities"""

from typing import TypedDict, Optional, Dict, List, Any
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.bmc_expert_prompts import GROWTH_ANALYSIS_PROMPT


class GrowthState(TypedDict):
    """State for Growth agent"""
    bmc_data: Dict[str, List[str]]
    market_analysis: Optional[Dict[str, Any]]
    financial_data: Optional[Dict[str, Any]]
    growth_opportunities: Optional[List[Dict[str, Any]]]
    scaling_recommendations: Optional[List[str]]
    growth_score_factors: Optional[Dict[str, float]]
    priority_actions: Optional[List[str]]
    error: Optional[str]


class GrowthAgent(BaseAgent):
    """
    Agent for analyzing growth potential, identifying opportunities,
    and calculating growth-related scores.
    """

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "growth"

    def get_actions(self) -> list:
        return ["analyze", "calculate_score", "identify_opportunities"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(GrowthState)

        workflow.add_node("analyze_growth", self._analyze_growth)

        workflow.add_edge(START, "analyze_growth")
        workflow.add_edge("analyze_growth", END)

        return workflow.compile()

    async def _analyze_growth(self, state: GrowthState) -> GrowthState:
        """Analyze growth potential and opportunities"""
        try:
            prompt = GROWTH_ANALYSIS_PROMPT.format(
                bmc_data=str(state.get("bmc_data", {})),
                market_analysis=str(state.get("market_analysis", {}))
            )

            result = await self.client.generate_json(
                prompt=prompt,
                system_prompt="You are a growth strategy expert analyzing business models for scaling potential."
            )

            return {
                **state,
                "growth_opportunities": result.get("growth_opportunities", []),
                "scaling_recommendations": result.get("scaling_recommendations", []),
                "growth_score_factors": result.get("growth_score_factors", {}),
                "priority_actions": result.get("priority_actions", [])
            }
        except Exception as e:
            return {
                **state,
                "error": f"Growth analysis failed: {str(e)}"
            }

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the growth agent"""
        initial_state: GrowthState = {
            "bmc_data": input_data.get("bmc_data", {}),
            "market_analysis": input_data.get("market_analysis"),
            "financial_data": input_data.get("financial_data"),
            "growth_opportunities": None,
            "scaling_recommendations": None,
            "growth_score_factors": None,
            "priority_actions": None,
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
            "growth_opportunities": result.get("growth_opportunities", []),
            "scaling_recommendations": result.get("scaling_recommendations", []),
            "growth_score_factors": result.get("growth_score_factors", {}),
            "priority_actions": result.get("priority_actions", [])
        }
