"""Market Analysis Agent - Analyzes market context and competitive landscape"""

from typing import TypedDict, Optional, Dict, List, Any
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.bmc_expert_prompts import MARKET_ANALYSIS_PROMPT


class MarketState(TypedDict):
    """State for Market Analysis agent"""
    bmc_data: Dict[str, List[str]]
    business_context: Optional[Dict[str, Any]]
    market_size: Optional[Dict[str, str]]
    competitive_analysis: Optional[Dict[str, Any]]
    positioning: Optional[Dict[str, Any]]
    market_readiness_score: Optional[float]
    timing_assessment: Optional[str]
    key_market_trends: Optional[List[str]]
    error: Optional[str]


class MarketAnalysisAgent(BaseAgent):
    """
    Agent for market analysis, competitor research,
    and market readiness assessment.
    """

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "market"

    def get_actions(self) -> list:
        return ["analyze_market", "competitor_analysis", "assess_readiness"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(MarketState)

        workflow.add_node("analyze_market", self._analyze_market)

        workflow.add_edge(START, "analyze_market")
        workflow.add_edge("analyze_market", END)

        return workflow.compile()

    async def _analyze_market(self, state: MarketState) -> MarketState:
        """Perform comprehensive market analysis"""
        try:
            prompt = MARKET_ANALYSIS_PROMPT.format(
                bmc_data=str(state.get("bmc_data", {})),
                business_context=str(state.get("business_context", {}))
            )

            result = await self.client.generate_json(
                prompt=prompt,
                system_prompt="You are a market research expert analyzing business opportunities and competitive landscapes."
            )

            return {
                **state,
                "market_size": result.get("market_size", {}),
                "competitive_analysis": result.get("competitive_analysis", {}),
                "positioning": result.get("positioning", {}),
                "market_readiness_score": result.get("market_readiness_score", 0),
                "timing_assessment": result.get("timing_assessment", "neutral"),
                "key_market_trends": result.get("key_market_trends", [])
            }
        except Exception as e:
            return {
                **state,
                "error": f"Market analysis failed: {str(e)}"
            }

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the market analysis agent"""
        initial_state: MarketState = {
            "bmc_data": input_data.get("bmc_data", {}),
            "business_context": input_data.get("business_context"),
            "market_size": None,
            "competitive_analysis": None,
            "positioning": None,
            "market_readiness_score": None,
            "timing_assessment": None,
            "key_market_trends": None,
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
            "market_size": result.get("market_size", {}),
            "competitive_analysis": result.get("competitive_analysis", {}),
            "positioning": result.get("positioning", {}),
            "market_readiness_score": result.get("market_readiness_score", 0),
            "timing_assessment": result.get("timing_assessment", "neutral"),
            "key_market_trends": result.get("key_market_trends", [])
        }
