"""Enhanced Ideation Agent - Generates innovative ideas with templates and frameworks"""

from typing import TypedDict, Optional, Dict, List, Any, Literal
from langgraph.graph import StateGraph, START, END
import uuid
import logging

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.ideation_prompts import (
    get_action_prompt,
    get_template_instructions,
    build_ideation_prompt,
    IDEA_ENHANCEMENT_PROMPT
)


class IdeationState(TypedDict):
    """State for Ideation agent"""
    action: Literal["brainstorm", "analyze_trends", "competitive_analysis", "market_opportunity", "product_innovation", "business_model_innovation"]
    topic: str
    context: Optional[Dict[str, Any]]
    template: Optional[str]
    industry: Optional[str]
    target_audience: Optional[str]
    constraints: Optional[List[str]]
    innovation_level: str
    quantity: int
    enhance: bool
    ideas: Optional[List[Dict[str, Any]]]
    trend_analysis: Optional[List[Dict[str, Any]]]
    competitor_analysis: Optional[List[Dict[str, Any]]]
    market_opportunities: Optional[List[Dict[str, Any]]]
    insights: Optional[List[str]]
    recommendations: Optional[List[str]]
    error: Optional[str]


class IdeationAgent(BaseAgent):
    """
    Enhanced Agent for innovation, ideation, and creative
    business model improvements with template support.
    """

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()
        self.logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "ideation"

    def get_actions(self) -> list:
        return ["brainstorm", "analyze_trends", "competitive_analysis", "market_opportunity", "product_innovation", "business_model_innovation"]

    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get available ideation templates"""
        return [
            {
                "name": "scamper",
                "description": "Substitute, Combine, Adapt, Modify, Put to another use, Eliminate, Reverse",
                "best_for": ["product innovation", "feature enhancement", "process improvement"]
            },
            {
                "name": "mind_map",
                "description": "Visual brainstorming with central topic and branching ideas",
                "best_for": ["exploratory ideation", "complex problems", "creative sessions"]
            },
            {
                "name": "swot",
                "description": "Strengths, Weaknesses, Opportunities, Threats analysis",
                "best_for": ["strategic planning", "competitive analysis", "risk assessment"]
            },
            {
                "name": "blue_ocean",
                "description": "Find uncontested market space and make competition irrelevant",
                "best_for": ["market strategy", "differentiation", "new market creation"]
            },
            {
                "name": "lean_startup",
                "description": "Build-Measure-Learn cycle with MVP focus",
                "best_for": ["startup ideation", "product validation", "agile development"]
            },
            {
                "name": "design_thinking",
                "description": "Empathize, Define, Ideate, Prototype, Test, Iterate",
                "best_for": ["user-centered design", "problem solving", "innovation"]
            },
            {
                "name": "first_principles",
                "description": "Break down to fundamental truths and rebuild from scratch",
                "best_for": ["radical innovation", "problem reframing", "disruptive ideas"]
            },
            {
                "name": "reverse_engineering",
                "description": "Study successful solutions and adapt core principles",
                "best_for": ["competitive analysis", "benchmarking", "cross-industry innovation"]
            }
        ]

    def get_available_actions(self) -> List[Dict[str, str]]:
        """Get available ideation actions"""
        return [
            {
                "name": "brainstorm",
                "description": "Generate diverse ideas using creative techniques"
            },
            {
                "name": "analyze_trends",
                "description": "Analyze current and emerging trends"
            },
            {
                "name": "competitive_analysis",
                "description": "Analyze competitors and identify strategic opportunities"
            },
            {
                "name": "market_opportunity",
                "description": "Identify market opportunities and assess potential"
            },
            {
                "name": "product_innovation",
                "description": "Generate innovative product ideas"
            },
            {
                "name": "business_model_innovation",
                "description": "Generate innovative business model ideas"
            }
        ]

    def get_available_innovation_levels(self) -> List[Dict[str, Any]]:
        """Get available innovation levels"""
        return [
            {
                "name": "incremental",
                "description": "Small improvements to existing products, services, or processes",
                "examples": ["Feature enhancement", "Process optimization", "UI/UX improvements"]
            },
            {
                "name": "disruptive",
                "description": "Significant changes that create new markets or value networks",
                "examples": ["Digital transformation", "New business models", "Platform innovations"]
            },
            {
                "name": "radical",
                "description": "Groundbreaking innovations that transform entire industries",
                "examples": ["New technology categories", "Paradigm shifts", "Breakthrough inventions"]
            }
        ]

    async def get_options(self) -> Dict[str, Any]:
        """Get available options for ideation"""
        return {
            "actions": self.get_available_actions(),
            "templates": self.get_available_templates(),
            "innovation_levels": self.get_available_innovation_levels()
        }

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(IdeationState)

        workflow.add_node("generate", self._generate)
        workflow.add_node("enhance", self._enhance)

        workflow.add_edge(START, "generate")
        workflow.add_conditional_edges(
            "generate",
            self._should_enhance,
            {
                "enhance": "enhance",
                "end": END
            }
        )
        workflow.add_edge("enhance", END)

        return workflow.compile()

    def _should_enhance(self, state: IdeationState) -> str:
        """Determine if enhancement is needed"""
        if state.get("enhance", False):
            return "enhance"
        return "end"

    async def _generate(self, state: IdeationState) -> IdeationState:
        """Generate ideas based on action type"""
        try:
            action = state.get("action", "brainstorm")
            template = state.get("template")
            self.logger.info(f"IdeationAgent._generate - Action: {action}, Template: {template}")
            
            prompt = build_ideation_prompt(
                action=action,
                topic=state.get("topic", ""),
                template=template,
                industry=state.get("industry"),
                target_audience=state.get("target_audience"),
                constraints=state.get("constraints"),
                innovation_level=state.get("innovation_level", "incremental"),
                quantity=state.get("quantity", 10),
                context=state.get("context")
            )
            
            self.logger.info(f"Prompt (first 500 chars): {prompt[:500]}")

            result = await self.client.generate_json(
                prompt=prompt,
                system_prompt="You are an expert innovation consultant generating creative ideas and strategic insights for businesses."
            )
            
            self.logger.info(f"Result from generate_json: {result.keys()}, Ideas: {result.get('ideas') is not None}")

            response = {
                **state,
                "insights": result.get("insights", []),
                "recommendations": result.get("recommendations", []),
                "template": template
            }

            if action == "brainstorm":
                response["ideas"] = [{"id": str(uuid.uuid4()), **idea} for idea in result.get("ideas", [])]
            elif action == "analyze_trends":
                response["trend_analysis"] = result.get("trends", [])
            elif action == "competitive_analysis":
                response["competitor_analysis"] = result.get("competitors", [])
            elif action == "market_opportunity":
                response["market_opportunities"] = result.get("opportunities", [])
            elif action in ["product_innovation", "business_model_innovation"]:
                response["ideas"] = [{"id": str(uuid.uuid4()), **idea} for idea in result.get("ideas", [])]

            return response
        except Exception as e:
            return {
                **state,
                "error": f"Ideation generation failed: {str(e)}"
            }

    async def _enhance(self, state: IdeationState) -> IdeationState:
        """Enhance ideas with deeper analysis"""
        try:
            ideas = state.get("ideas", [])
            if not ideas:
                return state

            enhancement_prompt = IDEA_ENHANCEMENT_PROMPT.format(
                ideas=str(ideas),
                topic=state.get("topic", ""),
                industry=state.get("industry", ""),
                target_audience=state.get("target_audience", "")
            )

            result = await self.client.generate_json(
                prompt=enhancement_prompt,
                system_prompt="You are an expert innovation analyst providing deep insights and strategic recommendations."
            )

            enhanced_ideas = [{"id": idea.get("id"), **enhancement} for idea, enhancement in zip(state.get("ideas", []), result.get("enhanced_ideas", []))]

            return {
                **state,
                "ideas": enhanced_ideas,
                "insights": state.get("insights", []) + result.get("insights", []),
                "recommendations": state.get("recommendations", []) + result.get("recommendations", []),
                "template": state.get("template")
            }
        except Exception as e:
            return {
                **state,
                "error": f"Idea enhancement failed: {str(e)}"
            }

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the ideation agent"""
        initial_state: IdeationState = {
            "action": input_data.get("action", "brainstorm"),
            "topic": input_data.get("topic", ""),
            "context": input_data.get("context"),
            "template": input_data.get("template"),
            "industry": input_data.get("industry"),
            "target_audience": input_data.get("target_audience"),
            "constraints": input_data.get("constraints"),
            "innovation_level": input_data.get("innovation_level", "incremental"),
            "quantity": input_data.get("quantity", 10),
            "enhance": input_data.get("enhance", False),
            "ideas": None,
            "trend_analysis": None,
            "competitor_analysis": None,
            "market_opportunities": None,
            "insights": None,
            "recommendations": None,
            "error": None
        }

        result = await self.graph.ainvoke(initial_state)

        if result.get("error"):
            return {
                "success": False,
                "error": result["error"]
            }

        response = {
            "success": True,
            "action": result.get("action"),
            "insights": result.get("insights"),
            "recommendations": result.get("recommendations"),
            "template_used": result.get("template")
        }

        if result.get("ideas"):
            response["ideas"] = result["ideas"]
        if result.get("trend_analysis"):
            response["trend_analysis"] = result["trend_analysis"]
        if result.get("competitor_analysis"):
            response["competitor_analysis"] = result["competitor_analysis"]
        if result.get("market_opportunities"):
            response["market_opportunities"] = result["market_opportunities"]

        return response
