from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import Field, BaseModel
import csv
import io
import uuid
from datetime import datetime

from app.auth import get_current_user
from app.database import get_db, Lead, BusinessProfile, LeadInteraction, SalesTask, FollowUpRule
from app.schemas.leads import (
    LeadCreate, LeadUpdate, LeadResponse, LeadListResponse,
    LeadRequest, LeadScoreResponse, LeadEmailResponse,
    SalesTaskCreate, SalesTaskUpdate, SalesTaskResponse, SalesTaskListResponse,
    FollowUpRuleCreate, FollowUpRuleUpdate, FollowUpRuleResponse, FollowUpRuleListResponse
)
from app.agents.orchestrator import get_orchestrator

router = APIRouter()


# --- Interaction Schemas ---

class LeadInteractionBase(BaseModel):
    interaction_type: str = Field(..., description="Type of interaction (email, call, meeting, note)")
    notes: Optional[str] = Field(None, description="Interaction notes")
    outcome: Optional[str] = Field(None, description="Interaction outcome")


class LeadInteractionCreate(LeadInteractionBase):
    pass


class LeadInteractionResponse(LeadInteractionBase):
    id: str
    lead_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Interaction Tracking Endpoints ---

@router.post("/{lead_id}/interactions", response_model=LeadInteractionResponse)
async def create_interaction(
    lead_id: str,
    interaction: LeadInteractionCreate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log an interaction with a lead"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.business_profile_id == profile.id))
    lead = result.scalars().first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db_interaction = LeadInteraction(
        lead_id=lead_id,
        **interaction.model_dump()
    )
    db.add(db_interaction)
    
    lead.last_contacted_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_interaction)
    return db_interaction


@router.get("/{lead_id}/interactions", response_model=List[LeadInteractionResponse])
async def list_interactions(
    lead_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all interactions for a lead"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.business_profile_id == profile.id))
    lead = result.scalars().first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    result = await db.execute(
        select(LeadInteraction).where(LeadInteraction.lead_id == lead_id).order_by(LeadInteraction.created_at.desc())
    )
    interactions = result.scalars().all()
    return interactions


async def get_business_profile(db: AsyncSession, user_id: str) -> BusinessProfile:
    result = await db.execute(select(BusinessProfile).where(BusinessProfile.user_id == user_id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    return profile


@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new lead"""
    profile = await get_business_profile(db, current_user)
    
    db_lead = Lead(
        **lead.model_dump(),
        business_profile_id=profile.id
    )
    db.add(db_lead)
    await db.commit()
    await db.refresh(db_lead)
    return db_lead


@router.get("/", response_model=LeadListResponse)
async def list_leads(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List leads with filtering and pagination"""
    profile = await get_business_profile(db, current_user)
    
    query = select(Lead).where(Lead.business_profile_id == profile.id)
    
    if status:
        query = query.where(Lead.status == status)
    
    if search:
        query = query.where(Lead.name.ilike(f"%{search}%") | Lead.company.ilike(f"%{search}%"))
    
    # Calculate total (simplification for async)
    # real impl might want a separate count query
    result = await db.execute(query)
    all_items = result.scalars().all()
    total = len(all_items)
    
    # Pagination in memory for simplicity (or modify query)
    start = (page - 1) * size
    items = all_items[start : start + size]
    
    return LeadListResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )


@router.get("/export")
async def export_leads(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export leads as CSV"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(select(Lead).where(Lead.business_profile_id == profile.id))
    leads = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "email", "phone", "company", "lead_source", "status", "notes"])
    
    for lead in leads:
        writer.writerow([
            lead.id, lead.name, lead.email, lead.phone, lead.company, 
            lead.lead_source, lead.status, lead.notes
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"}
    )


@router.post("/import")
async def import_leads(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Import leads from CSV"""
    profile = await get_business_profile(db, current_user)
    
    content = await file.read()
    text = content.decode()
    reader = csv.DictReader(io.StringIO(text))
    
    count = 0
    for row in reader:
        # Basic validation
        if not row.get("name"):
            continue
            
        lead = Lead(
            name=row.get("name"),
            email=row.get("email"),
            phone=row.get("phone"),
            company=row.get("company"),
            lead_source=row.get("source") or row.get("lead_source"),
            status=row.get("status", "new"),
            notes=row.get("notes"),
            business_profile_id=profile.id
        )
        db.add(lead)
        count += 1
    
    await db.commit()
    return {"success": True, "imported": count}


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific lead"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.business_profile_id == profile.id))
    lead = result.scalars().first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_update: LeadUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a lead"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.business_profile_id == profile.id))
    db_lead = result.scalars().first()
    
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lead, key, value)
    
    await db.commit()
    await db.refresh(db_lead)
    return db_lead


@router.post("/{lead_id}/assign")
async def assign_lead(
    lead_id: str,
    agent_id: str = Query(..., description="Agent ID to assign"),
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign a lead to an agent"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.business_profile_id == profile.id))
    db_lead = result.scalars().first()
    
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db_lead.assigned_agent_id = agent_id
    await db.commit()
    return {"success": True, "message": f"Assigned to agent {agent_id}"}


# --- Sales Task Endpoints ---

@router.post("/{lead_id}/tasks", response_model=SalesTaskResponse)
async def create_sales_task(
    lead_id: str,
    task: SalesTaskCreate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a sales task for a lead"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.business_profile_id == profile.id))
    lead = result.scalars().first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db_task = SalesTask(
        **task.model_dump(exclude={"business_profile_id"}),
        lead_id=lead_id,
        business_profile_id=profile.id,
        assigned_by=current_user
    )
    db.add(db_task)
    
    lead.next_follow_up_at = task.due_date
    
    await db.commit()
    await db.refresh(db_task)
    return db_task


@router.get("/{lead_id}/tasks", response_model=SalesTaskListResponse)
async def list_sales_tasks(
    lead_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List sales tasks for a lead"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.business_profile_id == profile.id))
    lead = result.scalars().first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    query = select(SalesTask).where(SalesTask.lead_id == lead_id)
    
    if status:
        query = query.where(SalesTask.status == status)
    
    query = query.order_by(SalesTask.due_date.asc())
    
    result = await db.execute(query)
    all_items = result.scalars().all()
    total = len(all_items)
    
    start = (page - 1) * size
    items = all_items[start : start + size]
    
    return SalesTaskListResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )


@router.put("/tasks/{task_id}", response_model=SalesTaskResponse)
async def update_sales_task(
    task_id: str,
    task_update: SalesTaskUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a sales task"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(
        select(SalesTask).join(Lead).where(
            SalesTask.id == task_id,
            Lead.business_profile_id == profile.id
        )
    )
    db_task = result.scalars().first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Sales task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    if task_update.status == "completed" and not db_task.completed_at:
        db_task.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_task)
    return db_task


@router.delete("/tasks/{task_id}")
async def delete_sales_task(
    task_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a sales task"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(
        select(SalesTask).join(Lead).where(
            SalesTask.id == task_id,
            Lead.business_profile_id == profile.id
        )
    )
    db_task = result.scalars().first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Sales task not found")
    
    await db.delete(db_task)
    await db.commit()
    return {"success": True, "message": "Task deleted"}


# --- Follow Up Rule Endpoints ---

@router.post("/follow-up-rules", response_model=FollowUpRuleResponse)
async def create_follow_up_rule(
    rule: FollowUpRuleCreate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a follow-up rule"""
    profile = await get_business_profile(db, current_user)
    
    db_rule = FollowUpRule(
        **rule.model_dump(exclude={"business_profile_id"}),
        business_profile_id=profile.id
    )
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.get("/follow-up-rules", response_model=FollowUpRuleListResponse)
async def list_follow_up_rules(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List follow-up rules"""
    profile = await get_business_profile(db, current_user)
    
    query = select(FollowUpRule).where(FollowUpRule.business_profile_id == profile.id)
    
    if is_active is not None:
        query = query.where(FollowUpRule.is_active == is_active)
    
    query = query.order_by(FollowUpRule.created_at.desc())
    
    result = await db.execute(query)
    all_items = result.scalars().all()
    total = len(all_items)
    
    start = (page - 1) * size
    items = all_items[start : start + size]
    
    return FollowUpRuleListResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )


@router.put("/follow-up-rules/{rule_id}", response_model=FollowUpRuleResponse)
async def update_follow_up_rule(
    rule_id: str,
    rule_update: FollowUpRuleUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a follow-up rule"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(
        select(FollowUpRule).where(
            FollowUpRule.id == rule_id,
            FollowUpRule.business_profile_id == profile.id
        )
    )
    db_rule = result.scalars().first()
    
    if not db_rule:
        raise HTTPException(status_code=404, detail="Follow-up rule not found")
    
    update_data = rule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rule, key, value)
    
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.delete("/follow-up-rules/{rule_id}")
async def delete_follow_up_rule(
    rule_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a follow-up rule"""
    profile = await get_business_profile(db, current_user)
    
    result = await db.execute(
        select(FollowUpRule).where(
            FollowUpRule.id == rule_id,
            FollowUpRule.business_profile_id == profile.id
        )
    )
    db_rule = result.scalars().first()
    
    if not db_rule:
        raise HTTPException(status_code=404, detail="Follow-up rule not found")
    
    await db.delete(db_rule)
    await db.commit()
    return {"success": True, "message": "Follow-up rule deleted"}


# --- Existing Agent Endpoints ---

@router.post("/score", response_model=LeadScoreResponse)
async def score_lead(
    request: LeadRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Score a lead using AI analysis.
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="leads",
        action="score",
        data={"lead": request.lead.model_dump()}
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return LeadScoreResponse(
        success=True,
        score=result.get("score"),
        suggestions=result.get("suggestions")
    )


@router.post("/email", response_model=LeadEmailResponse)
async def generate_email(
    request: LeadRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generate a personalized cold email for a lead.
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="leads",
        action="email",
        data={
            "lead": request.lead.model_dump(),
            "tone": request.tone
        }
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return LeadEmailResponse(
        success=True,
        subject=result.get("subject"),
        email=result.get("email")
    )


@router.post("/analyze", response_model=LeadScoreResponse)
async def analyze_lead(
    request: LeadRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Deep analysis of a lead including score and detailed insights.
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.invoke(
        agent_name="leads",
        action="analyze",
        data={"lead": request.lead.model_dump()}
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return LeadScoreResponse(
        success=True,
        score=result.get("score"),
        suggestions=result.get("suggestions")
    )