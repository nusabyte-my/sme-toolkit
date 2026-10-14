"""Template Management API endpoints for ideation"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.ideation import (
    TemplateCategoryCreate,
    TemplateCategoryUpdate,
    TemplateCategoryResponse,
    IdeationTemplateCreate,
    IdeationTemplateUpdate,
    IdeationTemplateResponse,
    IdeationSessionResponse,
    IdeationResultResponse
)
from app.services.ideation_service import IdeationService
from app.auth import get_current_user

router = APIRouter()


def extract_tags(tags_field: Optional[Dict[str, Any]]) -> Optional[List[str]]:
    """Extract tags list from tags field"""
    if tags_field is None:
        return None
    if isinstance(tags_field, dict):
        return tags_field.get("tags")
    if isinstance(tags_field, list):
        return tags_field
    return None


def extract_json_field(json_field: Optional[Dict[str, Any]], key: str) -> Optional[Any]:
    """Extract a value from a JSON field"""
    if json_field is None:
        return None
    if isinstance(json_field, dict):
        return json_field.get(key)
    return None


@router.post("/categories", response_model=TemplateCategoryResponse)
async def create_template_category(
    category_data: TemplateCategoryCreate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new template category"""
    category = await IdeationService.create_template_category(
        db=db,
        user_id=current_user,
        name=category_data.name,
        description=category_data.description,
        color=category_data.color,
        icon=category_data.icon
    )
    return TemplateCategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        color=category.color,
        icon=category.icon,
        is_default=category.is_default,
        template_count=category.template_count,
        created_at=category.created_at.isoformat(),
        updated_at=category.updated_at.isoformat()
    )


@router.get("/categories", response_model=List[TemplateCategoryResponse])
async def get_template_categories(
    include_default: bool = Query(True, description="Include default categories"),
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all template categories for the user"""
    categories = await IdeationService.get_template_categories(
        db=db,
        user_id=current_user,
        include_default=include_default
    )
    return [
        TemplateCategoryResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            color=cat.color,
            icon=cat.icon,
            is_default=cat.is_default,
            template_count=cat.template_count,
            created_at=cat.created_at.isoformat(),
            updated_at=cat.updated_at.isoformat()
        )
        for cat in categories
    ]


@router.put("/categories/{category_id}", response_model=TemplateCategoryResponse)
async def update_template_category(
    category_id: str,
    category_data: TemplateCategoryUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a template category"""
    category = await IdeationService.update_template_category(
        db=db,
        category_id=category_id,
        user_id=current_user,
        name=category_data.name,
        description=category_data.description,
        color=category_data.color,
        icon=category_data.icon
    )
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return TemplateCategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        color=category.color,
        icon=category.icon,
        is_default=category.is_default,
        template_count=category.template_count,
        created_at=category.created_at.isoformat(),
        updated_at=category.updated_at.isoformat()
    )


@router.delete("/categories/{category_id}")
async def delete_template_category(
    category_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a template category"""
    success = await IdeationService.delete_template_category(
        db=db,
        category_id=category_id,
        user_id=current_user
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category deleted successfully"}


@router.post("/templates", response_model=IdeationTemplateResponse)
async def create_ideation_template(
    template_data: IdeationTemplateCreate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new ideation template"""
    template = await IdeationService.create_ideation_template(
        db=db,
        user_id=current_user,
        name=template_data.name,
        description=template_data.description,
        framework=template_data.framework,
        instructions=template_data.instructions,
        prompt_template=template_data.prompt_template,
        custom_instructions=template_data.custom_instructions,
        category_id=template_data.category_id,
        is_public=template_data.is_public,
        tags=template_data.tags
    )
    return IdeationTemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        framework=template.framework,
        instructions=template.instructions,
        prompt_template=template.prompt_template,
        custom_instructions=template.custom_instructions,
        category_id=template.category_id,
        is_public=template.is_public,
        is_default=template.is_default,
        tags=extract_tags(template.tags),
        usage_count=template.usage_count,
        rating=template.rating,
        created_at=template.created_at.isoformat(),
        updated_at=template.updated_at.isoformat()
    )


@router.get("/templates", response_model=List[IdeationTemplateResponse])
async def get_ideation_templates(
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    is_public: bool = Query(False, description="Include public templates"),
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all ideation templates for the user"""
    templates = await IdeationService.get_ideation_templates(
        db=db,
        user_id=current_user,
        category_id=category_id,
        is_public=is_public
    )
    return [
        IdeationTemplateResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            framework=t.framework,
            instructions=t.instructions,
            prompt_template=t.prompt_template,
            custom_instructions=t.custom_instructions,
            category_id=t.category_id,
            is_public=t.is_public,
            is_default=t.is_default,
            tags=extract_tags(t.tags),
            usage_count=t.usage_count,
            rating=t.rating,
            created_at=t.created_at.isoformat(),
            updated_at=t.updated_at.isoformat()
        )
        for t in templates
    ]


@router.put("/templates/{template_id}", response_model=IdeationTemplateResponse)
async def update_ideation_template(
    template_id: str,
    template_data: IdeationTemplateUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an ideation template"""
    template = await IdeationService.update_ideation_template(
        db=db,
        template_id=template_id,
        user_id=current_user,
        name=template_data.name,
        description=template_data.description,
        framework=template_data.framework,
        instructions=template_data.instructions,
        prompt_template=template_data.prompt_template,
        custom_instructions=template_data.custom_instructions,
        category_id=template_data.category_id,
        is_public=template_data.is_public,
        tags=template_data.tags
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return IdeationTemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        framework=template.framework,
        instructions=template.instructions,
        prompt_template=template.prompt_template,
        custom_instructions=template.custom_instructions,
        category_id=template.category_id,
        is_public=template.is_public,
        is_default=template.is_default,
        tags=extract_tags(template.tags),
        usage_count=template.usage_count,
        rating=template.rating,
        created_at=template.created_at.isoformat(),
        updated_at=template.updated_at.isoformat()
    )


@router.delete("/templates/{template_id}")
async def delete_ideation_template(
    template_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an ideation template"""
    success = await IdeationService.delete_ideation_template(
        db=db,
        template_id=template_id,
        user_id=current_user
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"message": "Template deleted successfully"}


@router.get("/sessions", response_model=List[IdeationSessionResponse])
async def get_ideation_sessions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get ideation sessions for the user"""
    sessions = await IdeationService.get_ideation_sessions(
        db=db,
        user_id=current_user,
        limit=limit,
        offset=offset
    )
    return [
        IdeationSessionResponse(
            id=s.id,
            action=s.action,
            topic=s.topic,
            template_name=s.template_name,
            innovation_level=s.innovation_level,
            quantity=s.quantity,
            enhance_enabled=s.enhance_enabled,
            status=s.status,
            ideas_count=s.ideas_count,
            insights_count=s.insights_count,
            recommendations_count=s.recommendations_count,
            started_at=s.started_at.isoformat(),
            completed_at=s.completed_at.isoformat() if s.completed_at else None,
            duration_seconds=s.duration_seconds
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}/results", response_model=List[IdeationResultResponse])
async def get_session_results(
    session_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get ideation results for a session"""
    results = await IdeationService.get_ideation_results(
        db=db,
        session_id=session_id,
        user_id=current_user
    )
    return [
        IdeationResultResponse(
            id=r.id,
            session_id=r.session_id,
            title=r.title,
            description=r.description,
            category=r.category,
            impact=r.impact,
            effort=r.effort,
            innovation_type=r.innovation_type,
            feasibility_score=r.feasibility_score,
            novelty_score=r.novelty_score,
            value_score=r.value_score,
            overall_score=r.overall_score,
            tags=extract_json_field(r.tags, "tags"),
            implementation_steps=extract_json_field(r.implementation_steps, "steps"),
            risks=extract_json_field(r.risks, "risks"),
            metrics=extract_json_field(r.metrics, "metrics"),
            is_favorite=r.is_favorite,
            notes=r.notes,
            created_at=r.created_at.isoformat()
        )
        for r in results
    ]


@router.post("/results/{result_id}/favorite", response_model=IdeationResultResponse)
async def toggle_result_favorite(
    result_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle favorite status for an ideation result"""
    result = await IdeationService.toggle_favorite_result(
        db=db,
        result_id=result_id,
        user_id=current_user
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return IdeationResultResponse(
        id=result.id,
        session_id=result.session_id,
        title=result.title,
        description=result.description,
        category=result.category,
        impact=result.impact,
        effort=result.effort,
        innovation_type=result.innovation_type,
        feasibility_score=result.feasibility_score,
        novelty_score=result.novelty_score,
        value_score=result.value_score,
        overall_score=result.overall_score,
        tags=extract_json_field(result.tags, "tags"),
        implementation_steps=extract_json_field(result.implementation_steps, "steps"),
        risks=extract_json_field(result.risks, "risks"),
        metrics=extract_json_field(result.metrics, "metrics"),
        is_favorite=result.is_favorite,
        notes=result.notes,
        created_at=result.created_at.isoformat()
    )


@router.put("/results/{result_id}/notes", response_model=IdeationResultResponse)
async def update_result_notes(
    result_id: str,
    notes: str = Query(..., description="Notes to add"),
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update notes for an ideation result"""
    result = await IdeationService.update_result_notes(
        db=db,
        result_id=result_id,
        user_id=current_user,
        notes=notes
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return IdeationResultResponse(
        id=result.id,
        session_id=result.session_id,
        title=result.title,
        description=result.description,
        category=result.category,
        impact=result.impact,
        effort=result.effort,
        innovation_type=result.innovation_type,
        feasibility_score=result.feasibility_score,
        novelty_score=result.novelty_score,
        value_score=result.value_score,
        overall_score=result.overall_score,
        tags=result.tags.get("tags") if result.tags else None,
        implementation_steps=result.implementation_steps.get("steps") if result.implementation_steps else None,
        risks=result.risks.get("risks") if result.risks else None,
        metrics=result.metrics.get("metrics") if result.metrics else None,
        is_favorite=result.is_favorite,
        notes=result.notes,
        created_at=result.created_at.isoformat()
    )
