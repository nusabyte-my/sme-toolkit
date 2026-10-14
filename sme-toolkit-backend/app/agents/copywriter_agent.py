from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.copywriter_prompts import (
    COPYWRITER_PROMPT,
    COPY_ANALYSIS_PROMPT,
    FORMAT_INSTRUCTIONS,
    TEMPLATE_SYSTEMS,
    TOPIC_ENHANCEMENT_PROMPT,
    get_ab_testing_instructions,
    get_persona_instruction,
    get_variation_instructions
)


class CopywriterState(TypedDict):
    """State for Copywriter agent"""
    topic: str
    format: str
    tone: str
    target_audience: str
    variation_count: int
    enhance: bool
    template_id: Optional[str]
    persona: Optional[str]
    ab_testing_mode: bool
    template_system: Optional[str]
    analyze: bool
    enhanced_topic: Optional[str]
    raw_content: Optional[str]
    variations: Optional[List[Dict[str, str]]]
    analysis_result: Optional[Dict[str, Any]]
    error: Optional[str]


class CopywriterAgent(BaseAgent):
    """LangGraph agent for Marketing Copy generation"""

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "copywriter"

    def get_actions(self) -> list:
        return ["generate", "enhance"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(CopywriterState)

        # Add nodes
        workflow.add_node("check_enhance", self._check_enhance)
        workflow.add_node("enhance_topic", self._enhance_topic)
        workflow.add_node("generate_copy", self._generate_copy)
        workflow.add_node("parse_variations", self._parse_variations)
        workflow.add_node("check_analyze", self._check_analyze)
        workflow.add_node("analyze_copy", self._analyze_copy)

        # Add edges
        workflow.add_edge(START, "check_enhance")
        workflow.add_conditional_edges(
            "check_enhance",
            self._should_enhance,
            {
                "enhance": "enhance_topic",
                "generate": "generate_copy"
            }
        )
        workflow.add_edge("enhance_topic", "generate_copy")
        workflow.add_edge("generate_copy", "parse_variations")
        workflow.add_edge("parse_variations", "check_analyze")
        workflow.add_conditional_edges(
            "check_analyze",
            self._should_analyze,
            {
                "analyze": "analyze_copy",
                "end": END
            }
        )
        workflow.add_edge("analyze_copy", END)

        return workflow.compile()

    def _should_enhance(self, state: CopywriterState) -> str:
        """Determine if we should enhance the topic"""
        if state.get("enhance", False):
            return "enhance"
        return "generate"

    def _should_analyze(self, state: CopywriterState) -> str:
        """Determine if we should analyze the copy"""
        if state.get("analyze", False):
            return "analyze"
        return "end"

    async def _check_enhance(self, state: CopywriterState) -> CopywriterState:
        """Check if enhancement is needed"""
        return state

    async def _enhance_topic(self, state: CopywriterState) -> CopywriterState:
        """Enhance the topic for better copy"""
        try:
            prompt = TOPIC_ENHANCEMENT_PROMPT.format(topic=state["topic"])
            enhanced = await self.client.enhance_prompt(state["topic"])
            return {**state, "enhanced_topic": enhanced.strip()}
        except Exception as e:
            return {**state, "error": f"Topic enhancement failed: {str(e)}"}

    async def _generate_copy(self, state: CopywriterState) -> CopywriterState:
        """Generate marketing copy"""
        try:
            topic = state.get("enhanced_topic") or state["topic"]
            format_type = state["format"]
            count = state["variation_count"]
            persona = state.get("persona", "General")
            ab_testing = state.get("ab_testing_mode", False)
            template_system = state.get("template_system")

            # Get persona instruction
            persona_instruction = get_persona_instruction(persona)

            # Get template system instruction if specified
            template_instruction = ""
            if template_system and template_system in TEMPLATE_SYSTEMS:
                template_instruction = f"\n\n{TEMPLATE_SYSTEMS[template_system]}"

            # Get A/B testing instruction
            ab_testing_instruction = get_ab_testing_instructions(ab_testing)

            # Combine format instructions
            format_instructions = FORMAT_INSTRUCTIONS.get(format_type, "")
            if template_instruction:
                format_instructions += template_instruction

            prompt = COPYWRITER_PROMPT.format(
                format=format_type,
                count=count,
                topic=topic,
                audience=state.get("target_audience") or "general audience",
                tone=state["tone"],
                persona_instruction=persona_instruction,
                format_instructions=format_instructions,
                variation_instructions=get_variation_instructions(count),
                ab_testing_instructions=ab_testing_instruction
            )

            content = await self.client.generate_text(prompt, temperature=0.85 if ab_testing else 0.7)

            return {**state, "raw_content": content.strip()}

        except Exception as e:
            return {**state, "error": f"Copy generation failed: {str(e)}"}

    async def _parse_variations(self, state: CopywriterState) -> CopywriterState:
        """Parse raw content into variations"""
        try:
            raw = state.get("raw_content", "")
            if not raw:
                return state

            count = state["variation_count"]
            if state.get("ab_testing_mode"):
                count = 2 # Usually A/B is 2

            if count == 1:
                # Single variation
                variations = [{"label": "Option 1", "content": raw}]
            else:
                # Multiple variations separated by ---
                parts = raw.split("---")
                variations = []
                for i, part in enumerate(parts):
                    part = part.strip()
                    if part:
                        # Try to extract label if present
                        if part.startswith("Option") or part.startswith("Variation"):
                            lines = part.split("\n", 1)
                            label = lines[0].strip().rstrip(":")
                            content = lines[1].strip() if len(lines) > 1 else part
                        else:
                            label = f"Option {i + 1}"
                            content = part
                        variations.append({"label": label, "content": content})

            return {**state, "variations": variations}

        except Exception as e:
            return {**state, "error": f"Parsing failed: {str(e)}"}

    async def _check_analyze(self, state: CopywriterState) -> CopywriterState:
        """Check if analysis is needed"""
        return state

    async def _analyze_copy(self, state: CopywriterState) -> CopywriterState:
        """Analyze the generated copy for effectiveness"""
        try:
            variations = state.get("variations", [])
            if not variations:
                return state

            # Analyze the first variation (or could analyze all)
            main_variation = variations[0]["content"]

            prompt = COPY_ANALYSIS_PROMPT.format(
                copy=main_variation,
                format=state["format"],
                audience=state.get("target_audience") or "general audience"
            )

            analysis = await self.client.generate_text(prompt, temperature=0.3)

            return {**state, "analysis_result": {"raw_analysis": analysis}}

        except Exception as e:
            return {**state, "error": f"Analysis failed: {str(e)}"}

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the copywriter agent"""
        initial_state: CopywriterState = {
            "topic": input_data.get("topic", ""),
            "format": input_data.get("format", "Social Media Post"),
            "tone": input_data.get("tone", "Professional"),
            "target_audience": input_data.get("target_audience", ""),
            "variation_count": input_data.get("variation_count", 1),
            "enhance": input_data.get("enhance", False),
            "template_id": input_data.get("template_id"),
            "persona": input_data.get("persona"),
            "ab_testing_mode": input_data.get("ab_testing_mode", False),
            "template_system": input_data.get("template_system"),
            "analyze": input_data.get("analyze", False),
            "enhanced_topic": None,
            "raw_content": None,
            "variations": None,
            "analysis_result": None,
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
            "variations": result.get("variations", []),
            "raw_content": result.get("raw_content"),
            "enhanced_topic": result.get("enhanced_topic"),
            "analysis_result": result.get("analysis_result")
        }