from typing import TypedDict, Optional, Dict, Any, Literal, List
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.tools.image_tools import ImageTools
from app.prompts.visual_prompts import (
    VISUAL_GENERATION_PROMPT,
    VISUAL_EDIT_PROMPT,
    TEMPLATE_REQUIREMENTS,
    STYLE_GUIDES,
    CATEGORY_TEMPLATES,
    PROMPT_ENHANCEMENT_TEMPLATE,
    COMPOSITION_RULES,
    build_enhanced_prompt,
    get_style_characteristics,
    get_aspect_ratio_guidelines,
    get_category_template
)


class VisualState(TypedDict):
    """State for Visual Generator agent"""
    action: Literal["generate", "edit"]
    prompt: str
    style: Optional[str]
    aspect_ratio: str
    category: Optional[str]
    composition_rule: Optional[str]
    reference_image: Optional[str]
    source_image: Optional[str]
    enhance: bool
    enhanced_prompt: Optional[str]
    generated_image: Optional[str]
    variations: Optional[Dict[str, str]]
    error: Optional[str]


class VisualAgent(BaseAgent):
    """LangGraph agent for Visual Generation and Editing with enhanced templates"""

    def __init__(self):
        self.client = get_gemini_client()
        self.image_tools = ImageTools()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "visual"

    def get_actions(self) -> list:
        return ["generate", "edit"]

    def get_available_styles(self) -> Dict[str, str]:
        """Get available visual styles"""
        return {name: info["description"] for name, info in STYLE_GUIDES.items()}

    def get_available_categories(self) -> List[str]:
        """Get available visual categories"""
        return list(CATEGORY_TEMPLATES.keys())

    def get_available_aspect_ratios(self) -> List[str]:
        """Get available aspect ratios"""
        return list(TEMPLATE_REQUIREMENTS.keys())

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(VisualState)

        # Add nodes
        workflow.add_node("route_action", self._route_action)
        workflow.add_node("enhance_prompt", self._enhance_prompt)
        workflow.add_node("generate_image", self._generate_image)
        workflow.add_node("generate_variations", self._generate_variations)
        workflow.add_node("edit_image", self._edit_image)

        # Add edges
        workflow.add_edge(START, "route_action")
        workflow.add_conditional_edges(
            "route_action",
            self._determine_path,
            {
                "enhance_generate": "enhance_prompt",
                "generate": "generate_image",
                "edit": "edit_image"
            }
        )
        workflow.add_edge("enhance_prompt", "generate_image")
        workflow.add_conditional_edges(
            "generate_image",
            self._should_generate_variations,
            {
                "generate_variations": "generate_variations",
                "end": END
            }
        )
        workflow.add_edge("generate_variations", END)
        workflow.add_edge("edit_image", END)

        return workflow.compile()

    def _determine_path(self, state: VisualState) -> str:
        """Determine the processing path"""
        if state["action"] == "edit":
            return "edit"
        if state.get("enhance", False):
            return "enhance_generate"
        return "generate"

    def _should_generate_variations(self, state: VisualState) -> str:
        """Determine if we should generate variations"""
        if state.get("variations") and len(state.get("variations", {})) > 0:
            return "generate_variations"
        return "end"

    async def _route_action(self, state: VisualState) -> VisualState:
        """Route to appropriate action"""
        return state

    async def _enhance_prompt(self, state: VisualState) -> VisualState:
        """Enhance the visual prompt"""
        try:
            prompt = state["prompt"]
            style = state.get("style") or "Photorealistic"
            aspect_ratio = state.get("aspect_ratio", "1:1")
            category = state.get("category")

            # Use AI enhancement if no category template is used
            if not category:
                enhancement_prompt = PROMPT_ENHANCEMENT_TEMPLATE.format(
                    prompt=prompt,
                    use_case="visual generation",
                    style=style
                )
                enhanced = await self.client.generate_text(enhancement_prompt, temperature=0.3)
                return {**state, "enhanced_prompt": enhanced.strip()}
            else:
                # Build enhanced prompt from templates
                kwargs = {
                    "aspect_ratio": aspect_ratio,
                    "tone": style,
                    "product": prompt,
                    "topic": prompt,
                    "subject": prompt,
                    "background": "clean, neutral background",
                    "event_type": prompt,
                    "theme": style,
                    "use_case": "marketing"
                }
                enhanced = build_enhanced_prompt(prompt, style, aspect_ratio, category, **kwargs)
                return {**state, "enhanced_prompt": enhanced}

        except Exception as e:
            return {**state, "error": f"Prompt enhancement failed: {str(e)}"}

    async def _generate_image(self, state: VisualState) -> VisualState:
        """Generate an image from prompt"""
        try:
            prompt = state.get("enhanced_prompt") or state["prompt"]
            style = state.get("style") or "Photorealistic"
            aspect_ratio = state.get("aspect_ratio", "1:1")
            category = state.get("category")
            composition_rule = state.get("composition_rule")

            # Get style characteristics
            style_char = get_style_characteristics(style)

            # Get aspect ratio guidelines
            ratio_guidelines = get_aspect_ratio_guidelines(aspect_ratio)

            # Build composition guidelines
            composition_guidelines = ""
            if composition_rule and composition_rule in COMPOSITION_RULES:
                composition_guidelines = f"Composition Rule: {COMPOSITION_RULES[composition_rule]}"

            # Build full prompt
            full_prompt = VISUAL_GENERATION_PROMPT.format(
                prompt=prompt,
                style=style_char,
                aspect_ratio=aspect_ratio,
                template_requirements=ratio_guidelines,
                composition_guidelines=composition_guidelines
            )

            image = await self.image_tools.generate_image(
                prompt=full_prompt,
                style=style,
                aspect_ratio=aspect_ratio,
                reference_image=state.get("reference_image")
            )

            return {**state, "generated_image": image}

        except Exception as e:
            return {**state, "error": f"Image generation failed: {str(e)}"}

    async def _generate_variations(self, state: VisualState) -> VisualState:
        """Generate variations of the generated image"""
        try:
            variations = state.get("variations", {})
            if not variations:
                return state

            generated_variations = {}
            prompt = state.get("enhanced_prompt") or state["prompt"]
            style = state.get("style") or "Photorealistic"
            aspect_ratio = state.get("aspect_ratio", "1:1")

            for var_name, var_instruction in variations.items():
                var_prompt = f"{prompt} Variation: {var_instruction}"
                
                image = await self.image_tools.generate_image(
                    prompt=var_prompt,
                    style=style,
                    aspect_ratio=aspect_ratio,
                    reference_image=state.get("reference_image")
                )
                
                generated_variations[var_name] = image

            return {**state, "variations": generated_variations}

        except Exception as e:
            return {**state, "error": f"Variation generation failed: {str(e)}"}

    async def _edit_image(self, state: VisualState) -> VisualState:
        """Edit an existing image"""
        try:
            source = state.get("source_image")
            if not source:
                return {**state, "error": "No source image provided for editing"}

            instruction = VISUAL_EDIT_PROMPT.format(instruction=state["prompt"])

            edited = await self.image_tools.edit_image(
                source_image=source,
                instruction=instruction
            )

            return {**state, "generated_image": edited}

        except Exception as e:
            return {**state, "error": f"Image editing failed: {str(e)}"}

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the visual agent"""
        initial_state: VisualState = {
            "action": input_data.get("action", "generate"),
            "prompt": input_data.get("prompt", ""),
            "style": input_data.get("style"),
            "aspect_ratio": input_data.get("aspect_ratio", "1:1"),
            "category": input_data.get("category"),
            "composition_rule": input_data.get("composition_rule"),
            "reference_image": input_data.get("reference_image"),
            "source_image": input_data.get("source_image"),
            "enhance": input_data.get("enhance", False),
            "enhanced_prompt": None,
            "generated_image": None,
            "variations": input_data.get("variations"),
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
            "image": result.get("generated_image"),
            "enhanced_prompt": result.get("enhanced_prompt"),
            "variations": result.get("variations")
        }

    async def get_options(self) -> Dict[str, Any]:
        """Get available options for visual generation"""
        return {
            "styles": self.get_available_styles(),
            "categories": self.get_available_categories(),
            "aspect_ratios": self.get_available_aspect_ratios(),
            "composition_rules": list(COMPOSITION_RULES.keys())
        }