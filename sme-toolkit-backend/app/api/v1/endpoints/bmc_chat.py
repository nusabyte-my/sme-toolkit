"""BMC Chat API endpoints - Conversational BMC discovery"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db, ConversationSession, ConversationPhase
from app.agents.bmc_expert_agent import BMCExpertAgent
from app.agents.bmc_orchestrator import get_bmc_orchestrator
from app.auth import get_current_user

router = APIRouter()

# Request/Response Models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CreateSessionRequest(BaseModel):
    initial_context: Optional[Dict[str, Any]] = None


class CreateSessionResponse(BaseModel):
    session_id: str
    greeting: str
    suggestions: List[str]


class SendMessageRequest(BaseModel):
    session_id: str
    message: str


class SendMessageResponse(BaseModel):
    session_id: str
    response: str
    suggestions: List[str]
    follow_up_questions: List[str]
    extracted_context: Dict[str, Any]
    ready_for_wizard: bool
    wizard_prefill: Optional[Dict[str, str]] = None


class SessionResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    extracted_context: Dict[str, Any]
    phase: str
    ready_for_wizard: bool
    created_at: str


class FinalizeSessionResponse(BaseModel):
    session_id: str
    extracted_context: Dict[str, Any]
    wizard_prefill: Dict[str, str]
    ready: bool


class WizardSuggestionsRequest(BaseModel):
    session_id: str
    step_id: str
    current_inputs: Optional[Dict[str, str]] = None


class WizardSuggestionsResponse(BaseModel):
    suggestions: Dict[str, List[str]]
    insights: str


class FullAnalysisRequest(BaseModel):
    bmc_data: Dict[str, List[str]]
    business_context: Optional[Dict[str, Any]] = None


class FullAnalysisResponse(BaseModel):
    success: bool
    growth_score: Optional[Dict[str, Any]] = None
    market_analysis: Optional[Dict[str, Any]] = None
    financial_analysis: Optional[Dict[str, Any]] = None
    operations_analysis: Optional[Dict[str, Any]] = None
    growth_analysis: Optional[Dict[str, Any]] = None
    ideation_results: Optional[Dict[str, Any]] = None
    strategy_recommendations: Optional[List[str]] = None
    action_items: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


# Initialize agent
bmc_expert = BMCExpertAgent()


@router.post("/session", response_model=CreateSessionResponse)
async def create_chat_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new BMC chat session and get initial greeting"""
    try:
        # Generate greeting
        result = await bmc_expert.invoke({
            "action": "greet"
        })

        greeting = result.get("response", "Hello! Let's build your Business Model Canvas. Tell me about your business idea.")

        # Create session in database
        session = ConversationSession(
            id=str(uuid.uuid4()),
            user_id=current_user,
            messages=[{
                "role": "assistant",
                "content": greeting,
                "timestamp": datetime.utcnow().isoformat()
            }],
            extracted_context=request.initial_context or {},
            phase=ConversationPhase.DISCOVERY,
            ready_for_wizard="false"
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return CreateSessionResponse(
            session_id=session.id,
            greeting=greeting,
            suggestions=result.get("suggestions", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get session details"""
    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == session_id,
            ConversationSession.user_id == current_user
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        session_id=session.id,
        messages=[ChatMessage(**msg) for msg in (session.messages or [])],
        extracted_context=session.extracted_context or {},
        phase=session.phase.value if session.phase else "discovery",
        ready_for_wizard=session.ready_for_wizard == "true",
        created_at=session.created_at.isoformat()
    )


@router.post("/message", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Send a message in the chat session"""
    # Get session
    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == request.session_id,
            ConversationSession.user_id == current_user
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Add user message to history
        messages = session.messages or []
        messages.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Process with BMC expert
        agent_result = await bmc_expert.invoke({
            "action": "chat",
            "session_id": session.id,
            "message": request.message,
            "conversation_history": messages,
            "extracted_context": session.extracted_context or {}
        })

        # Add assistant response
        response = agent_result.get("response", "Thank you for sharing. Could you tell me more?")
        messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Update session
        session.messages = messages
        session.extracted_context = agent_result.get("extracted_context", session.extracted_context)

        # Check readiness
        ready = agent_result.get("ready_for_wizard", False)
        session.ready_for_wizard = "true" if ready else "false"

        if ready:
            session.wizard_prefill = agent_result.get("wizard_prefill")
            session.phase = ConversationPhase.CONFIRMATION

        await db.commit()
        await db.refresh(session)

        return SendMessageResponse(
            session_id=session.id,
            response=response,
            suggestions=agent_result.get("suggestions", []),
            follow_up_questions=agent_result.get("follow_up_questions", []),
            extracted_context=session.extracted_context or {},
            ready_for_wizard=ready,
            wizard_prefill=agent_result.get("wizard_prefill")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.post("/session/{session_id}/finalize", response_model=FinalizeSessionResponse)
async def finalize_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Finalize conversation and extract context for wizard"""
    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == session_id,
            ConversationSession.user_id == current_user
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Run full context extraction
        agent_result = await bmc_expert.invoke({
            "action": "extract",
            "conversation_history": session.messages or []
        })

        # Update session
        session.extracted_context = agent_result.get("extracted_context", {})
        session.wizard_prefill = agent_result.get("wizard_prefill", {})
        session.ready_for_wizard = "true" if agent_result.get("ready_for_wizard") else "false"
        session.phase = ConversationPhase.CONFIRMATION

        await db.commit()
        await db.refresh(session)

        return FinalizeSessionResponse(
            session_id=session.id,
            extracted_context=session.extracted_context or {},
            wizard_prefill=session.wizard_prefill or {},
            ready=session.ready_for_wizard == "true"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to finalize session: {str(e)}")


@router.post("/wizard/suggestions", response_model=WizardSuggestionsResponse)
async def get_wizard_suggestions(
    request: WizardSuggestionsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get AI suggestions for a wizard step"""
    # Get session context
    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == request.session_id,
            ConversationSession.user_id == current_user
        )
    )
    session = result.scalar_one_or_none()

    extracted_context = session.extracted_context if session else {}

    try:
        agent_result = await bmc_expert.invoke({
            "action": "suggest",
            "step_id": request.step_id,
            "extracted_context": extracted_context,
            "current_inputs": request.current_inputs or {}
        })

        return WizardSuggestionsResponse(
            suggestions=agent_result.get("suggestions", {}),
            insights=agent_result.get("response", "")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.post("/analyze", response_model=FullAnalysisResponse)
async def run_full_analysis(
    request: FullAnalysisRequest,
    current_user: str = Depends(get_current_user)
):
    """Run full multi-agent analysis on BMC data"""
    try:
        orchestrator = get_bmc_orchestrator()

        result = await orchestrator.invoke({
            "user_id": current_user,
            "bmc_data": request.bmc_data,
            "business_context": request.business_context
        })

        if not result.get("success"):
            return FullAnalysisResponse(
                success=False,
                error=result.get("error", "Analysis failed")
            )

        return FullAnalysisResponse(
            success=True,
            growth_score=result.get("growth_score"),
            market_analysis=result.get("market_analysis"),
            financial_analysis=result.get("financial_analysis"),
            operations_analysis=result.get("operations_analysis"),
            growth_analysis=result.get("growth_analysis"),
            ideation_results=result.get("ideation_results"),
            strategy_recommendations=result.get("strategy_recommendations"),
            action_items=result.get("action_items")
        )

    except Exception as e:
        return FullAnalysisResponse(
            success=False,
            error=str(e)
        )
