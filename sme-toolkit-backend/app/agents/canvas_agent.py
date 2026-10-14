from typing import TypedDict, Optional, Dict, List, Any
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.canvas_prompts import (
    CANVAS_SYSTEM_PROMPT,
    CANVAS_GENERATION_PROMPT,
    ENHANCE_PROMPT
)


class CanvasState(TypedDict):
    """State for Business Model Canvas agent"""
    business_description: str
    user_inputs: Optional[Dict[str, str]]
    mode: str  # 'quick' or 'wizard'
    enhance: bool
    enhanced_description: Optional[str]
    canvas_data: Optional[Dict[str, List[str]]]
    error: Optional[str]


class CanvasAgent(BaseAgent):
    """LangGraph agent for Business Model Canvas generation"""

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "canvas"

    def get_actions(self) -> list:
        return ["generate", "enhance"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(CanvasState)

        # Add nodes
        workflow.add_node("check_enhance", self._check_enhance)
        workflow.add_node("enhance_description", self._enhance_description)
        workflow.add_node("generate_canvas", self._generate_canvas)

        # Add edges
        workflow.add_edge(START, "check_enhance")
        workflow.add_conditional_edges(
            "check_enhance",
            self._should_enhance,
            {
                "enhance": "enhance_description",
                "generate": "generate_canvas"
            }
        )
        workflow.add_edge("enhance_description", "generate_canvas")
        workflow.add_edge("generate_canvas", END)

        return workflow.compile()

    def _should_enhance(self, state: CanvasState) -> str:
        """Determine if we should enhance the description"""
        if state.get("enhance", False):
            return "enhance"
        return "generate"

    async def _check_enhance(self, state: CanvasState) -> CanvasState:
        """Check if enhancement is needed"""
        return state

    async def _enhance_description(self, state: CanvasState) -> CanvasState:
        """Enhance the business description"""
        try:
            prompt = ENHANCE_PROMPT.format(original=state["business_description"])
            enhanced = await self.client.generate_text(prompt, temperature=0.7)
            return {**state, "enhanced_description": enhanced.strip()}
        except Exception as e:
            return {**state, "error": f"Enhancement failed: {str(e)}"}

    async def _generate_canvas(self, state: CanvasState) -> CanvasState:
        """Generate the business model canvas"""
        try:
            # Use enhanced description if available
            description = state.get("enhanced_description") or state["business_description"]

            # Build user context from wizard inputs
            user_context = ""
            if state.get("user_inputs"):
                context_parts = []
                for key, value in state["user_inputs"].items():
                    if value:
                        context_parts.append(f"- {key}: {value}")
                if context_parts:
                    user_context = "User-provided information:\n" + "\n".join(context_parts)

            prompt = CANVAS_GENERATION_PROMPT.format(
                description=description,
                user_context=user_context
            )

            canvas = await self.client.generate_json(
                prompt=prompt,
                system_prompt=CANVAS_SYSTEM_PROMPT
            )

            return {**state, "canvas_data": canvas}

        except Exception as e:
            return {**state, "error": f"Canvas generation failed: {str(e)}"}

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the canvas agent"""
        initial_state: CanvasState = {
            "business_description": input_data.get("description", ""),
            "user_inputs": input_data.get("user_inputs"),
            "mode": input_data.get("mode", "quick"),
            "enhance": input_data.get("enhance", False),
            "enhanced_description": None,
            "canvas_data": None,
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
            "canvas": result.get("canvas_data"),
            "enhanced_description": result.get("enhanced_description")
        }
