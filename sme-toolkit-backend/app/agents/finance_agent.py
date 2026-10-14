"""Finance Agent - Analyzes financial aspects and projections"""

from typing import TypedDict, Optional, Dict, List, Any
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.bmc_expert_prompts import FINANCIAL_ANALYSIS_PROMPT


class FinanceState(TypedDict):
    """State for Finance agent"""
    bmc_data: Dict[str, List[str]]
    revenue_analysis: Optional[Dict[str, Any]]
    cost_analysis: Optional[Dict[str, Any]]
    financial_health_score: Optional[float]
    funding_readiness: Optional[str]
    key_metrics: Optional[List[str]]
    financial_recommendations: Optional[List[str]]
    error: Optional[str]


class FinanceAgent(BaseAgent):
    """
    Agent for financial modeling, projections,
    and financial health assessment.
    """

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "finance"

    def get_actions(self) -> list:
        return ["analyze_financials", "model_revenue", "assess_health"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(FinanceState)

        workflow.add_node("analyze_financials", self._analyze_financials)

        workflow.add_edge(START, "analyze_financials")
        workflow.add_edge("analyze_financials", END)

        return workflow.compile()

    async def _analyze_financials(self, state: FinanceState) -> FinanceState:
        """Analyze financial aspects of the business model"""
        try:
            bmc_data = state.get("bmc_data", {})

            prompt = FINANCIAL_ANALYSIS_PROMPT.format(
                bmc_data=str(bmc_data),
                revenue_streams=str(bmc_data.get("revenueStreams", [])),
                cost_structure=str(bmc_data.get("costStructure", []))
            )

            result = await self.client.generate_json(
                prompt=prompt,
                system_prompt="You are a financial analyst specializing in business model economics and startup finance."
            )

            return {
                **state,
                "revenue_analysis": result.get("revenue_analysis", {}),
                "cost_analysis": result.get("cost_analysis", {}),
                "financial_health_score": result.get("financial_health_score", 0),
                "funding_readiness": result.get("funding_readiness", "early"),
                "key_metrics": result.get("key_financial_metrics_to_track", []),
                "financial_recommendations": result.get("financial_recommendations", [])
            }
        except Exception as e:
            return {
                **state,
                "error": f"Financial analysis failed: {str(e)}"
            }

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the finance agent"""
        initial_state: FinanceState = {
            "bmc_data": input_data.get("bmc_data", {}),
            "revenue_analysis": None,
            "cost_analysis": None,
            "financial_health_score": None,
            "funding_readiness": None,
            "key_metrics": None,
            "financial_recommendations": None,
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
            "revenue_analysis": result.get("revenue_analysis", {}),
            "cost_analysis": result.get("cost_analysis", {}),
            "financial_health_score": result.get("financial_health_score", 0),
            "funding_readiness": result.get("funding_readiness", "early"),
            "key_metrics": result.get("key_metrics", []),
            "financial_recommendations": result.get("financial_recommendations", [])
        }
