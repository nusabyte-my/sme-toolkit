from typing import TypedDict, Optional, Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.strategy_prompts import STRATEGY_PROMPTS, ENHANCE_CONTEXT_PROMPT


class StrategyState(TypedDict):
    """State for Strategy Advisor agent"""
    business_context: str
    profile_data: Optional[Dict[str, Any]]  # Added structured profile data
    advice_type: Literal["TIPS", "GROWTH_PLAN", "INSIGHTS", "CREATIVE"]
    enhance: bool
    enhanced_context: Optional[str]
    content: Optional[str]
    error: Optional[str]


class StrategyAgent(BaseAgent):
    """LangGraph agent for Strategic Business Advice"""

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "strategy"

    def get_actions(self) -> list:
        return ["TIPS", "GROWTH_PLAN", "INSIGHTS", "CREATIVE"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(StrategyState)

        # Add nodes
        workflow.add_node("check_enhance", self._check_enhance)
        workflow.add_node("enhance_context", self._enhance_context)
        workflow.add_node("generate_advice", self._generate_advice)

        # Add edges
        workflow.add_edge(START, "check_enhance")
        workflow.add_conditional_edges(
            "check_enhance",
            self._should_enhance,
            {
                "enhance": "enhance_context",
                "generate": "generate_advice"
            }
        )
        workflow.add_edge("enhance_context", "generate_advice")
        workflow.add_edge("generate_advice", END)

        return workflow.compile()

    def _should_enhance(self, state: StrategyState) -> str:
        """Determine if we should enhance the context"""
        # If we have structured profile data, we might not need enhancement as much,
        # but let's respect the flag for now.
        if state.get("enhance", False):
            return "enhance"
        return "generate"

    async def _check_enhance(self, state: StrategyState) -> StrategyState:
        """Check if enhancement is needed"""
        return state

    async def _enhance_context(self, state: StrategyState) -> StrategyState:
        """Enhance the business context"""
        try:
            # Prefer profile data if available, falling back to string context
            context_source = self._format_profile(state.get("profile_data")) or state["business_context"]
            
            prompt = ENHANCE_CONTEXT_PROMPT.format(context=context_source)
            enhanced = await self.client.generate_text(prompt, temperature=0.7)
            return {**state, "enhanced_context": enhanced.strip()}
        except Exception as e:
            return {**state, "error": f"Context enhancement failed: {str(e)}"}

    async def _generate_advice(self, state: StrategyState) -> StrategyState:
        """Generate strategic advice"""
        try:
            # 1. Use enhanced context if available
            # 2. Else use structured profile data if available
            # 3. Else use raw business_context string
            
            if state.get("enhanced_context"):
                context = state["enhanced_context"]
            else:
                context = self._format_profile(state.get("profile_data")) or state["business_context"]

            advice_type = state["advice_type"]

            prompt_template = STRATEGY_PROMPTS.get(advice_type)
            if not prompt_template:
                return {**state, "error": f"Unknown advice type: {advice_type}"}

            prompt = prompt_template.format(context=context)

            # Use Pro model for deeper strategic reasoning
            content = await self.client.generate_text(
                prompt,
                use_pro=True,
                temperature=0.7
            )

            return {**state, "content": content.strip()}

        except Exception as e:
            return {**state, "error": f"Advice generation failed: {str(e)}"}

    def _format_profile(self, profile: Optional[Dict[str, Any]]) -> Optional[str]:
        """Convert structured profile dict to a readable string context"""
        if not profile:
            return None
            
        lines = []
        if profile.get("company_name"):
            lines.append(f"Company: {profile['company_name']}")
        if profile.get("industry"):
            lines.append(f"Industry: {profile['industry']}")
        if profile.get("business_description"):
            lines.append(f"Description: {profile['business_description']}")
        
        # Add goals if present
        if profile.get("short_term_goals"):
            lines.append("Short-term Goals: " + ", ".join(profile["short_term_goals"]))
        
        # Add revenue/metrics if present
        if profile.get("annual_revenue"):
            lines.append(f"Annual Revenue: {profile['annual_revenue']} {profile.get('revenue_currency', 'USD')}")
            
        return "\n".join(lines) if lines else None

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the strategy agent"""
        initial_state: StrategyState = {
            "business_context": input_data.get("business_context", ""),
            "advice_type": input_data.get("advice_type", "TIPS"),
            "enhance": input_data.get("enhance", False),
            "enhanced_context": None,
            "content": None,
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
            "advice_type": result["advice_type"],
            "content": result.get("content"),
            "enhanced_context": result.get("enhanced_context")
        }
