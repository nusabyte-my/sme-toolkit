"""Operations Agent - Analyzes operational aspects and execution capability"""

from typing import TypedDict, Optional, Dict, List, Any
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.bmc_expert_prompts import OPERATIONS_ANALYSIS_PROMPT


class OperationsState(TypedDict):
    """State for Operations agent"""
    bmc_data: Dict[str, List[str]]
    operations_assessment: Optional[Dict[str, Any]]
    resource_analysis: Optional[Dict[str, Any]]
    partnership_assessment: Optional[Dict[str, Any]]
    execution_capability_score: Optional[float]
    operational_priorities: Optional[List[str]]
    error: Optional[str]


class OperationsAgent(BaseAgent):
    """
    Agent for operations analysis and optimization
    recommendations.
    """

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "operations"

    def get_actions(self) -> list:
        return ["analyze_operations", "optimize_processes", "assess_capability"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(OperationsState)

        workflow.add_node("analyze_operations", self._analyze_operations)

        workflow.add_edge(START, "analyze_operations")
        workflow.add_edge("analyze_operations", END)

        return workflow.compile()

    async def _analyze_operations(self, state: OperationsState) -> OperationsState:
        """Analyze operational aspects of the business model"""
        try:
            bmc_data = state.get("bmc_data", {})

            prompt = OPERATIONS_ANALYSIS_PROMPT.format(
                bmc_data=str(bmc_data),
                key_activities=str(bmc_data.get("keyActivities", [])),
                key_resources=str(bmc_data.get("keyResources", [])),
                key_partners=str(bmc_data.get("keyPartners", []))
            )

            result = await self.client.generate_json(
                prompt=prompt,
                system_prompt="You are an operations expert analyzing business processes and execution capabilities."
            )

            return {
                **state,
                "operations_assessment": result.get("operations_assessment", {}),
                "resource_analysis": result.get("resource_analysis", {}),
                "partnership_assessment": result.get("partnership_assessment", {}),
                "execution_capability_score": result.get("execution_capability_score", 0),
                "operational_priorities": result.get("operational_priorities", [])
            }
        except Exception as e:
            return {
                **state,
                "error": f"Operations analysis failed: {str(e)}"
            }

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the operations agent"""
        initial_state: OperationsState = {
            "bmc_data": input_data.get("bmc_data", {}),
            "operations_assessment": None,
            "resource_analysis": None,
            "partnership_assessment": None,
            "execution_capability_score": None,
            "operational_priorities": None,
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
            "operations_assessment": result.get("operations_assessment", {}),
            "resource_analysis": result.get("resource_analysis", {}),
            "partnership_assessment": result.get("partnership_assessment", {}),
            "execution_capability_score": result.get("execution_capability_score", 0),
            "operational_priorities": result.get("operational_priorities", [])
        }
