"""BMC Expert Agent - Conversational Business Model Canvas discovery"""

from typing import TypedDict, Optional, Dict, List, Any
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.prompts.bmc_expert_prompts import (
    BMC_EXPERT_SYSTEM_PROMPT,
    CONVERSATION_PROMPT,
    CONTEXT_EXTRACTION_PROMPT,
    READINESS_CHECK_PROMPT,
    WIZARD_SUGGESTIONS_PROMPT,
    INITIAL_GREETING_PROMPT
)


class BMCExpertState(TypedDict):
    """State for BMC Expert agent"""
    action: str  # 'chat', 'extract', 'check_readiness', 'suggest', 'greet'
    session_id: Optional[str]
    conversation_history: List[Dict[str, str]]
    user_message: Optional[str]
    extracted_context: Dict[str, Any]
    response: Optional[str]
    suggestions: List[str]
    follow_up_questions: List[str]
    ready_for_wizard: bool
    wizard_prefill: Optional[Dict[str, Any]]
    step_id: Optional[str]  # For wizard suggestions
    step_focus: Optional[str]
    current_inputs: Optional[Dict[str, str]]
    error: Optional[str]


class BMCExpertAgent(BaseAgent):
    """
    Expert agent for Business Model Canvas creation through
    conversational discovery and guided wizard flow.
    """

    def __init__(self):
        self.client = get_gemini_client()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "bmc_expert"

    def get_actions(self) -> list:
        return ["chat", "extract", "check_readiness", "suggest", "greet"]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(BMCExpertState)

        # Add nodes
        workflow.add_node("route_action", self._route_action)
        workflow.add_node("generate_greeting", self._generate_greeting)
        workflow.add_node("process_chat", self._process_chat)
        workflow.add_node("extract_context", self._extract_context)
        workflow.add_node("check_readiness", self._check_readiness)
        workflow.add_node("generate_suggestions", self._generate_suggestions)

        # Add edges
        workflow.add_edge(START, "route_action")
        workflow.add_conditional_edges(
            "route_action",
            self._get_action_route,
            {
                "greet": "generate_greeting",
                "chat": "process_chat",
                "extract": "extract_context",
                "check_readiness": "check_readiness",
                "suggest": "generate_suggestions"
            }
        )
        workflow.add_edge("generate_greeting", END)
        workflow.add_edge("process_chat", END)
        workflow.add_edge("extract_context", END)
        workflow.add_edge("check_readiness", END)
        workflow.add_edge("generate_suggestions", END)

        return workflow.compile()

    def _get_action_route(self, state: BMCExpertState) -> str:
        """Route to appropriate action handler"""
        return state.get("action", "chat")

    async def _route_action(self, state: BMCExpertState) -> BMCExpertState:
        """Passthrough node for routing"""
        return state

    async def _generate_greeting(self, state: BMCExpertState) -> BMCExpertState:
        """Generate initial greeting for new conversation"""
        try:
            result = await self.client.generate_json(
                prompt=INITIAL_GREETING_PROMPT,
                system_prompt=BMC_EXPERT_SYSTEM_PROMPT
            )

            greeting = result.get("greeting", "Hello! I'm here to help you build your Business Model Canvas.")
            initial_question = result.get("initial_question", "Tell me about your business idea.")

            return {
                **state,
                "response": f"{greeting}\n\n{initial_question}",
                "suggestions": [],
                "follow_up_questions": [initial_question]
            }
        except Exception as e:
            return {
                **state,
                "error": f"Failed to generate greeting: {str(e)}",
                "response": "Hello! I'm here to help you build your Business Model Canvas. Tell me about your business idea - what problem are you solving and for whom?"
            }

    async def _process_chat(self, state: BMCExpertState) -> BMCExpertState:
        """Process a chat message and generate response"""
        try:
            # Format conversation history
            history_text = ""
            for msg in state.get("conversation_history", []):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"{role.upper()}: {content}\n"

            # Determine missing areas
            extracted = state.get("extracted_context", {})
            bmc_blocks = [
                "keyPartners", "keyActivities", "keyResources", "valuePropositions",
                "customerRelationships", "channels", "customerSegments", "costStructure", "revenueStreams"
            ]
            missing_areas = []
            for block in bmc_blocks:
                block_data = extracted.get(block, {})
                if not block_data or not block_data.get("items"):
                    missing_areas.append(block)

            prompt = CONVERSATION_PROMPT.format(
                conversation_history=history_text,
                user_message=state.get("user_message", ""),
                extracted_info=str(extracted),
                missing_areas=", ".join(missing_areas) if missing_areas else "None - good coverage!"
            )

            result = await self.client.generate_json(
                prompt=prompt,
                system_prompt=BMC_EXPERT_SYSTEM_PROMPT
            )

            response = result.get("response", "Thank you for sharing. Could you tell me more?")
            suggestions = result.get("suggestions", [])
            extracted_this_turn = result.get("extracted_this_turn", {})

            # Merge newly extracted info
            updated_context = {**extracted}
            for key, value in extracted_this_turn.items():
                if key in bmc_blocks:
                    if key not in updated_context:
                        updated_context[key] = {"items": [], "confidence": 0.5}
                    if isinstance(value, list):
                        updated_context[key]["items"].extend(value)
                    elif isinstance(value, str):
                        updated_context[key]["items"].append(value)
                else:
                    updated_context[key] = value

            return {
                **state,
                "response": response,
                "suggestions": suggestions,
                "extracted_context": updated_context,
                "follow_up_questions": []
            }
        except Exception as e:
            return {
                **state,
                "error": f"Chat processing failed: {str(e)}",
                "response": "I understand. Could you tell me a bit more about that?"
            }

    async def _extract_context(self, state: BMCExpertState) -> BMCExpertState:
        """Extract structured context from conversation"""
        try:
            # Format full conversation
            conversation_text = ""
            for msg in state.get("conversation_history", []):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                conversation_text += f"{role.upper()}: {content}\n"

            prompt = CONTEXT_EXTRACTION_PROMPT.format(conversation=conversation_text)

            result = await self.client.generate_json(
                prompt=prompt,
                system_prompt=BMC_EXPERT_SYSTEM_PROMPT
            )

            # Prepare wizard prefill data
            wizard_prefill = {}
            bmc_blocks = [
                "keyPartners", "keyActivities", "keyResources", "valuePropositions",
                "customerRelationships", "channels", "customerSegments", "costStructure", "revenueStreams"
            ]
            for block in bmc_blocks:
                block_data = result.get(block, {})
                items = block_data.get("items", [])
                if items:
                    wizard_prefill[block] = "\n".join(items)

            return {
                **state,
                "extracted_context": result,
                "ready_for_wizard": result.get("ready_for_wizard", False),
                "wizard_prefill": wizard_prefill
            }
        except Exception as e:
            return {
                **state,
                "error": f"Context extraction failed: {str(e)}"
            }

    async def _check_readiness(self, state: BMCExpertState) -> BMCExpertState:
        """Check if conversation is ready for wizard"""
        try:
            # Format conversation history
            history_text = ""
            for msg in state.get("conversation_history", []):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"{role.upper()}: {content}\n"

            prompt = READINESS_CHECK_PROMPT.format(
                extracted_context=str(state.get("extracted_context", {})),
                conversation_history=history_text
            )

            result = await self.client.generate_json(
                prompt=prompt,
                system_prompt=BMC_EXPERT_SYSTEM_PROMPT
            )

            ready = result.get("ready", False)
            suggested_question = result.get("suggested_question")

            return {
                **state,
                "ready_for_wizard": ready,
                "response": result.get("recommendation", ""),
                "follow_up_questions": [suggested_question] if suggested_question else [],
                "suggestions": result.get("strong_areas", [])
            }
        except Exception as e:
            return {
                **state,
                "error": f"Readiness check failed: {str(e)}"
            }

    async def _generate_suggestions(self, state: BMCExpertState) -> BMCExpertState:
        """Generate AI suggestions for wizard step"""
        try:
            # Build context from extracted info
            business_context = state.get("extracted_context", {})
            metadata = business_context.get("metadata", {})

            # Determine step focus
            step_focus_map = {
                "value": "Value Proposition and Customer Segments",
                "operations": "Key Activities, Resources, and Partners",
                "customer": "Channels and Customer Relationships",
                "finance": "Revenue Streams and Cost Structure"
            }
            step_focus = step_focus_map.get(state.get("step_id", ""), "Business Model")

            # Determine fields for this step
            step_fields_map = {
                "value": ["valuePropositions", "customerSegments"],
                "operations": ["keyActivities", "keyResources", "keyPartners"],
                "customer": ["channels", "customerRelationships"],
                "finance": ["revenueStreams", "costStructure"]
            }
            fields = step_fields_map.get(state.get("step_id", ""), [])

            prompt = WIZARD_SUGGESTIONS_PROMPT.format(
                business_context=str(business_context),
                step_id=state.get("step_id", ""),
                step_focus=step_focus,
                fields=", ".join(fields),
                current_inputs=str(state.get("current_inputs", {}))
            )

            result = await self.client.generate_json(
                prompt=prompt,
                system_prompt=BMC_EXPERT_SYSTEM_PROMPT
            )

            return {
                **state,
                "suggestions": result.get("field_suggestions", {}),
                "response": result.get("insights", "")
            }
        except Exception as e:
            return {
                **state,
                "error": f"Suggestion generation failed: {str(e)}"
            }

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the BMC expert agent"""
        initial_state: BMCExpertState = {
            "action": input_data.get("action", "chat"),
            "session_id": input_data.get("session_id"),
            "conversation_history": input_data.get("conversation_history", []),
            "user_message": input_data.get("message"),
            "extracted_context": input_data.get("extracted_context", {}),
            "response": None,
            "suggestions": [],
            "follow_up_questions": [],
            "ready_for_wizard": False,
            "wizard_prefill": None,
            "step_id": input_data.get("step_id"),
            "step_focus": input_data.get("step_focus"),
            "current_inputs": input_data.get("current_inputs"),
            "error": None
        }

        result = await self.graph.ainvoke(initial_state)

        if result.get("error"):
            return {
                "success": False,
                "error": result["error"],
                "response": result.get("response")
            }

        return {
            "success": True,
            "response": result.get("response"),
            "suggestions": result.get("suggestions", []),
            "follow_up_questions": result.get("follow_up_questions", []),
            "extracted_context": result.get("extracted_context", {}),
            "ready_for_wizard": result.get("ready_for_wizard", False),
            "wizard_prefill": result.get("wizard_prefill")
        }
