from typing import TypedDict, Optional, Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.lead_prompts import LEAD_SCORING_PROMPT, COLD_EMAIL_PROMPT


class LeadState(TypedDict):
    """State for Lead Manager agent"""
    action: Literal["score", "email", "analyze"]
    lead: Dict[str, Any]
    tone: str
    score: Optional[int]
    suggestions: Optional[str]
    email_subject: Optional[str]
    email_body: Optional[str]
    error: Optional[str]


class LeadAgent(BaseAgent):
    """LangGraph agent for Lead Management"""

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "leads"

    def get_actions(self) -> list:
        return ["score", "email", "analyze"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(LeadState)

        # Add nodes
        workflow.add_node("route_action", self._route_action)
        workflow.add_node("score_lead", self._score_lead)
        workflow.add_node("generate_email", self._generate_email)
        workflow.add_node("analyze_lead", self._analyze_lead)

        # Add edges
        workflow.add_edge(START, "route_action")
        workflow.add_conditional_edges(
            "route_action",
            self._get_action,
            {
                "score": "score_lead",
                "email": "generate_email",
                "analyze": "analyze_lead"
            }
        )
        workflow.add_edge("score_lead", END)
        workflow.add_edge("generate_email", END)
        workflow.add_edge("analyze_lead", END)

        return workflow.compile()

    def _get_action(self, state: LeadState) -> str:
        """Get the action to perform"""
        return state.get("action", "score")

    async def _route_action(self, state: LeadState) -> LeadState:
        """Route to appropriate action"""
        return state

    async def _score_lead(self, state: LeadState) -> LeadState:
        """Score a lead using AI"""
        try:
            lead = state["lead"]
            prompt = LEAD_SCORING_PROMPT.format(
                name=lead.get("name", "Unknown"),
                company=lead.get("company", "Unknown"),
                email=lead.get("email", ""),
                status=lead.get("status", "New"),
                engagement=lead.get("engagement", "Medium"),
                notes=lead.get("notes", "No notes")
            )

            result = await self.client.generate_json(prompt)

            return {
                **state,
                "score": result.get("score", 50),
                "suggestions": result.get("suggestions", "Follow up with the lead.")
            }

        except Exception as e:
            return {**state, "error": f"Lead scoring failed: {str(e)}"}

    async def _generate_email(self, state: LeadState) -> LeadState:
        """Generate a cold email for the lead"""
        try:
            lead = state["lead"]
            prompt = COLD_EMAIL_PROMPT.format(
                name=lead.get("name", "there"),
                company=lead.get("company", "your company"),
                notes=lead.get("notes", ""),
                tone=state.get("tone", "Professional")
            )

            result = await self.client.generate_json(prompt)

            return {
                **state,
                "email_subject": result.get("subject", "Following up"),
                "email_body": result.get("body", "")
            }

        except Exception as e:
            return {**state, "error": f"Email generation failed: {str(e)}"}

    async def _analyze_lead(self, state: LeadState) -> LeadState:
        """Deep analysis of lead (score + detailed insights)"""
        # First score the lead
        scored_state = await self._score_lead(state)

        if scored_state.get("error"):
            return scored_state

        # Add deeper analysis
        try:
            lead = state["lead"]
            prompt = f"""Provide a detailed analysis for this B2B lead:

Lead: {lead.get('name')} at {lead.get('company')}
Status: {lead.get('status')}
Engagement: {lead.get('engagement')}
Notes: {lead.get('notes')}
Initial Score: {scored_state.get('score')}

Provide:
1. Conversion probability assessment
2. Key buying signals or red flags
3. Recommended next 3 actions
4. Potential deal size indicators

Keep response concise but actionable."""

            analysis = await self.client.generate_text(prompt)

            return {
                **scored_state,
                "suggestions": analysis.strip()
            }

        except Exception as e:
            return {**scored_state, "error": f"Analysis failed: {str(e)}"}

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the lead agent"""
        initial_state: LeadState = {
            "action": input_data.get("action", "score"),
            "lead": input_data.get("lead", {}),
            "tone": input_data.get("tone", "Professional"),
            "score": None,
            "suggestions": None,
            "email_subject": None,
            "email_body": None,
            "error": None
        }

        result = await self.graph.ainvoke(initial_state)

        if result.get("error"):
            return {
                "success": False,
                "error": result["error"]
            }

        action = result["action"]

        if action == "email":
            return {
                "success": True,
                "action": "email",
                "subject": result.get("email_subject"),
                "email": result.get("email_body")
            }
        else:  # score or analyze
            return {
                "success": True,
                "action": action,
                "score": result.get("score"),
                "suggestions": result.get("suggestions")
            }
