"""Prompt Genie Agent - Optimizes and generates high-quality prompts"""

from typing import TypedDict, Optional, Dict, List, Any
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.schemas.prompt_genie import PromptTemplate, PromptVariable


class PromptGenieState(TypedDict):
    """State for Prompt Genie agent"""
    original_prompt: str
    goal: str
    target_model: Optional[str]
    context: Optional[str]
    output_format: Optional[str]
    constraints: Optional[List[str]]
    optimized_prompt: Optional[str]
    improvements: Optional[List[str]]
    reasoning: Optional[str]
    variations: Optional[List[Dict[str, Any]]]
    error: Optional[str]


class PromptGenieAgent(BaseAgent):
    """
    Agent for prompt optimization, enhancement, and generation.
    """

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "prompt_genie"

    def get_actions(self) -> list:
        return ["optimize_prompt", "generate_from_template", "analyze_prompt"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(PromptGenieState)

        workflow.add_node("optimize_prompt", self._optimize_prompt)

        workflow.add_edge(START, "optimize_prompt")
        workflow.add_edge("optimize_prompt", END)

        return workflow.compile()

    async def _optimize_prompt(self, state: PromptGenieState) -> PromptGenieState:
        """Optimize the given prompt based on goals and context"""
        try:
            system_prompt = """You are an expert prompt engineer specializing in creating high-quality prompts for AI models.

Your task is to optimize prompts for:
- Clarity and specificity
- Context and constraints
- Output format expectations
- Best practices for the target AI model

Key principles:
1. Be specific and detailed
2. Provide clear context
3. Specify desired output format
4. Include constraints when needed
5. Use examples when helpful
6. Chain-of-thought reasoning for complex tasks
7. Role-based prompting for better alignment

Always return valid JSON."""

            goal_guidance = {
                "clarity": "Focus on making the prompt clear, unambiguous, and easy to understand",
                "creativity": "Enhance the prompt to encourage more creative and diverse outputs",
                "specificity": "Add specific details, constraints, and precise requirements",
                "conciseness": "Make the prompt more concise while maintaining effectiveness",
                "comprehensive": "Create a thorough, well-structured prompt with all necessary elements"
            }

            guidance = goal_guidance.get(state.get("goal", "comprehensive"), goal_guidance["comprehensive"])

            context_section = ""
            if state.get("context"):
                context_section = f"\nContext/Use Case: {state['context']}"

            model_section = ""
            if state.get("target_model"):
                model_section = f"\nTarget Model: {state['target_model']}"

            format_section = ""
            if state.get("output_format"):
                format_section = f"\nDesired Output Format: {state['output_format']}"

            constraints_section = ""
            if state.get("constraints"):
                constraints_section = f"\nConstraints: {', '.join(state['constraints'])}"

            user_prompt = f"""Optimize the following prompt based on the goal.

Original Prompt:
{state['original_prompt']}

Optimization Goal: {state['goal']}
{guidance}{context_section}{model_section}{format_section}{constraints_section}

Return JSON with:
{{
    "optimized_prompt": "the fully optimized prompt",
    "improvements": ["improvement 1", "improvement 2", "improvement 3"],
    "reasoning": "brief explanation of changes made",
    "variations": [
        {{"label": "Variation Name", "prompt": "alternative version", "focus": "what this variation emphasizes"}}
    ]
}}"""

            result = await self.client.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt
            )

            return {
                **state,
                "optimized_prompt": result.get("optimized_prompt"),
                "improvements": result.get("improvements", []),
                "reasoning": result.get("reasoning"),
                "variations": result.get("variations", [])
            }
        except Exception as e:
            return {
                **state,
                "error": f"Prompt optimization failed: {str(e)}"
            }

    async def generate_from_template(self, template: PromptTemplate, variable_values: Dict[str, Any]) -> str:
        """Generate a prompt from a template by filling in variables"""
        try:
            prompt = template.template

            for var in template.variables:
                value = variable_values.get(var.name)
                if value is None:
                    if var.default_value:
                        value = var.default_value
                    elif var.required:
                        raise ValueError(f"Required variable '{var.name}' not provided")
                    else:
                        value = ""

                if var.type == "multiselect" and isinstance(value, list):
                    value = ", ".join(value)

                prompt = prompt.replace(f"{{{{{var.name}}}}}", str(value))

            return prompt
        except Exception as e:
            raise ValueError(f"Template generation failed: {str(e)}")

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the prompt genie agent"""
        action = input_data.get("action", "optimize_prompt")

        if action == "optimize_prompt":
            initial_state: PromptGenieState = {
                "original_prompt": input_data.get("original_prompt", ""),
                "goal": input_data.get("goal", "comprehensive"),
                "target_model": input_data.get("target_model"),
                "context": input_data.get("context"),
                "output_format": input_data.get("output_format"),
                "constraints": input_data.get("constraints"),
                "optimized_prompt": None,
                "improvements": None,
                "reasoning": None,
                "variations": None,
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
                "optimized_prompt": result.get("optimized_prompt"),
                "improvements": result.get("improvements", []),
                "reasoning": result.get("reasoning"),
                "variations": result.get("variations", [])
            }

        elif action == "generate_from_template":
            template = input_data.get("template")
            variable_values = input_data.get("variable_values", {})

            try:
                prompt = await self.generate_from_template(template, variable_values)
                return {
                    "success": True,
                    "prompt": prompt
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
