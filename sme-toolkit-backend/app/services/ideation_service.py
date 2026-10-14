"""Service layer for ideation template customization and management"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from datetime import datetime
import uuid

from app.database import (
    TemplateCategory,
    IdeationTemplate,
    IdeationSession,
    IdeationResult
)


class IdeationService:
    """Service for managing ideation templates, categories, sessions, and results"""

    @staticmethod
    async def create_template_category(
        db: AsyncSession,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        business_profile_id: Optional[str] = None
    ) -> TemplateCategory:
        """Create a new template category"""
        category = TemplateCategory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            business_profile_id=business_profile_id,
            name=name,
            description=description,
            color=color,
            icon=icon,
            is_default=False,
            template_count=0
        )
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def get_template_categories(
        db: AsyncSession,
        user_id: str,
        business_profile_id: Optional[str] = None,
        include_default: bool = True
    ) -> List[TemplateCategory]:
        """Get all template categories for a user"""
        conditions = [TemplateCategory.user_id == user_id]
        
        if include_default:
            conditions.append(TemplateCategory.is_default == True)
        
        query = select(TemplateCategory).where(or_(*conditions))
        
        if business_profile_id:
            query = query.where(
                or_(
                    TemplateCategory.business_profile_id == business_profile_id,
                    TemplateCategory.business_profile_id.is_(None)
                )
            )
        
        result = await db.execute(query.order_by(TemplateCategory.name))
        return result.scalars().all()

    @staticmethod
    async def update_template_category(
        db: AsyncSession,
        category_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None
    ) -> Optional[TemplateCategory]:
        """Update a template category"""
        query = select(TemplateCategory).where(
            and_(
                TemplateCategory.id == category_id,
                TemplateCategory.user_id == user_id,
                TemplateCategory.is_default == False
            )
        )
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            return None
        
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        if color is not None:
            category.color = color
        if icon is not None:
            category.icon = icon
        
        category.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete_template_category(
        db: AsyncSession,
        category_id: str,
        user_id: str
    ) -> bool:
        """Delete a template category"""
        query = select(TemplateCategory).where(
            and_(
                TemplateCategory.id == category_id,
                TemplateCategory.user_id == user_id,
                TemplateCategory.is_default == False
            )
        )
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            return False
        
        await db.delete(category)
        await db.commit()
        return True

    @staticmethod
    async def create_ideation_template(
        db: AsyncSession,
        user_id: str,
        name: str,
        framework: str,
        instructions: str,
        prompt_template: str,
        description: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        category_id: Optional[str] = None,
        is_public: bool = False,
        tags: Optional[List[str]] = None,
        business_profile_id: Optional[str] = None
    ) -> IdeationTemplate:
        """Create a new ideation template"""
        template = IdeationTemplate(
            id=str(uuid.uuid4()),
            user_id=user_id,
            business_profile_id=business_profile_id,
            category_id=category_id,
            name=name,
            description=description,
            framework=framework,
            instructions=instructions,
            prompt_template=prompt_template,
            custom_instructions=custom_instructions,
            is_public=is_public,
            is_default=False,
            tags={"tags": tags} if tags else None,
            usage_count=0
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        if category_id:
            await IdeationService._update_category_template_count(db, category_id)
        
        return template

    @staticmethod
    async def get_ideation_templates(
        db: AsyncSession,
        user_id: str,
        category_id: Optional[str] = None,
        is_public: bool = False,
        business_profile_id: Optional[str] = None
    ) -> List[IdeationTemplate]:
        """Get all ideation templates for a user"""
        query = select(IdeationTemplate).where(
            or_(
                IdeationTemplate.user_id == user_id,
                IdeationTemplate.is_public == True,
                IdeationTemplate.is_default == True
            )
        )
        
        if category_id:
            query = query.where(IdeationTemplate.category_id == category_id)
        
        if business_profile_id:
            query = query.where(
                or_(
                    IdeationTemplate.business_profile_id == business_profile_id,
                    IdeationTemplate.business_profile_id.is_(None)
                )
            )
        
        result = await db.execute(query.order_by(desc(IdeationTemplate.usage_count)))
        return result.scalars().all()

    @staticmethod
    async def update_ideation_template(
        db: AsyncSession,
        template_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        framework: Optional[str] = None,
        instructions: Optional[str] = None,
        prompt_template: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        category_id: Optional[str] = None,
        is_public: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[IdeationTemplate]:
        """Update an ideation template"""
        query = select(IdeationTemplate).where(
            and_(
                IdeationTemplate.id == template_id,
                IdeationTemplate.user_id == user_id,
                IdeationTemplate.is_default == False
            )
        )
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            return None
        
        old_category_id = template.category_id
        
        if name is not None:
            template.name = name
        if description is not None:
            template.description = description
        if framework is not None:
            template.framework = framework
        if instructions is not None:
            template.instructions = instructions
        if prompt_template is not None:
            template.prompt_template = prompt_template
        if custom_instructions is not None:
            template.custom_instructions = custom_instructions
        if category_id is not None:
            template.category_id = category_id
        if is_public is not None:
            template.is_public = is_public
        if tags is not None:
            template.tags = {"tags": tags}
        
        template.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(template)
        
        if old_category_id != category_id:
            if old_category_id:
                await IdeationService._update_category_template_count(db, old_category_id)
            if category_id:
                await IdeationService._update_category_template_count(db, category_id)
        
        return template

    @staticmethod
    async def delete_ideation_template(
        db: AsyncSession,
        template_id: str,
        user_id: str
    ) -> bool:
        """Delete an ideation template"""
        query = select(IdeationTemplate).where(
            and_(
                IdeationTemplate.id == template_id,
                IdeationTemplate.user_id == user_id,
                IdeationTemplate.is_default == False
            )
        )
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            return False
        
        category_id = template.category_id
        await db.delete(template)
        await db.commit()
        
        if category_id:
            await IdeationService._update_category_template_count(db, category_id)
        
        return True

    @staticmethod
    async def increment_template_usage(
        db: AsyncSession,
        template_id: str
    ) -> None:
        """Increment template usage count"""
        query = select(IdeationTemplate).where(IdeationTemplate.id == template_id)
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if template:
            template.usage_count += 1
            await db.commit()

    @staticmethod
    async def create_ideation_session(
        db: AsyncSession,
        user_id: str,
        action: str,
        topic: str,
        template_id: Optional[str] = None,
        template_name: Optional[str] = None,
        innovation_level: str = "incremental",
        quantity: int = 10,
        enhance_enabled: bool = False,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        custom_instructions: Optional[str] = None,
        business_profile_id: Optional[str] = None
    ) -> IdeationSession:
        """Create a new ideation session"""
        session = IdeationSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            business_profile_id=business_profile_id,
            template_id=template_id,
            action=action,
            topic=topic,
            template_name=template_name,
            innovation_level=innovation_level,
            quantity=quantity,
            enhance_enabled=enhance_enabled,
            industry=industry,
            target_audience=target_audience,
            constraints={"constraints": constraints} if constraints else None,
            custom_instructions=custom_instructions,
            status="pending",
            ideas_count=0,
            insights_count=0,
            recommendations_count=0
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        if template_id:
            await IdeationService.increment_template_usage(db, template_id)
        
        return session

    @staticmethod
    async def update_ideation_session(
        db: AsyncSession,
        session_id: str,
        status: Optional[str] = None,
        error_message: Optional[str] = None,
        ideas_count: Optional[int] = None,
        insights_count: Optional[int] = None,
        recommendations_count: Optional[int] = None,
        completed: bool = False
    ) -> Optional[IdeationSession]:
        """Update an ideation session"""
        query = select(IdeationSession).where(IdeationSession.id == session_id)
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        if status is not None:
            session.status = status
        if error_message is not None:
            session.error_message = error_message
        if ideas_count is not None:
            session.ideas_count = ideas_count
        if insights_count is not None:
            session.insights_count = insights_count
        if recommendations_count is not None:
            session.recommendations_count = recommendations_count
        
        if completed:
            session.completed_at = datetime.utcnow()
            if session.started_at:
                duration = (session.completed_at - session.started_at).total_seconds()
                session.duration_seconds = int(duration)
        
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_ideation_sessions(
        db: AsyncSession,
        user_id: str,
        business_profile_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[IdeationSession]:
        """Get ideation sessions for a user"""
        query = select(IdeationSession).where(IdeationSession.user_id == user_id)
        
        if business_profile_id:
            query = query.where(IdeationSession.business_profile_id == business_profile_id)
        
        result = await db.execute(
            query.order_by(desc(IdeationSession.started_at)).limit(limit).offset(offset)
        )
        return result.scalars().all()

    @staticmethod
    async def create_ideation_result(
        db: AsyncSession,
        session_id: str,
        user_id: str,
        title: str,
        description: str,
        impact: str,
        effort: str,
        innovation_type: str,
        feasibility_score: int,
        novelty_score: int,
        value_score: int,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        implementation_steps: Optional[List[str]] = None,
        risks: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None
    ) -> IdeationResult:
        """Create a new ideation result"""
        overall_score = int((feasibility_score + novelty_score + value_score) / 3)
        
        result = IdeationResult(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            impact=impact,
            effort=effort,
            innovation_type=innovation_type,
            feasibility_score=feasibility_score,
            novelty_score=novelty_score,
            value_score=value_score,
            overall_score=overall_score,
            tags={"tags": tags} if tags else None,
            implementation_steps={"steps": implementation_steps} if implementation_steps else None,
            risks={"risks": risks} if risks else None,
            metrics={"metrics": metrics} if metrics else None,
            is_favorite=False
        )
        db.add(result)
        await db.commit()
        await db.refresh(result)
        return result

    @staticmethod
    async def get_ideation_results(
        db: AsyncSession,
        session_id: str,
        user_id: str
    ) -> List[IdeationResult]:
        """Get ideation results for a session"""
        query = select(IdeationResult).where(
            and_(
                IdeationResult.session_id == session_id,
                IdeationResult.user_id == user_id
            )
        )
        result = await db.execute(query.order_by(desc(IdeationResult.overall_score)))
        return result.scalars().all()

    @staticmethod
    async def toggle_favorite_result(
        db: AsyncSession,
        result_id: str,
        user_id: str
    ) -> Optional[IdeationResult]:
        """Toggle favorite status for an ideation result"""
        query = select(IdeationResult).where(
            and_(
                IdeationResult.id == result_id,
                IdeationResult.user_id == user_id
            )
        )
        result = await db.execute(query)
        ideation_result = result.scalar_one_or_none()
        
        if not ideation_result:
            return None
        
        ideation_result.is_favorite = not ideation_result.is_favorite
        await db.commit()
        await db.refresh(ideation_result)
        return ideation_result

    @staticmethod
    async def update_result_notes(
        db: AsyncSession,
        result_id: str,
        user_id: str,
        notes: str
    ) -> Optional[IdeationResult]:
        """Update notes for an ideation result"""
        query = select(IdeationResult).where(
            and_(
                IdeationResult.id == result_id,
                IdeationResult.user_id == user_id
            )
        )
        result = await db.execute(query)
        ideation_result = result.scalar_one_or_none()
        
        if not ideation_result:
            return None
        
        ideation_result.notes = notes
        await db.commit()
        await db.refresh(ideation_result)
        return ideation_result

    @staticmethod
    async def _update_category_template_count(
        db: AsyncSession,
        category_id: str
    ) -> None:
        """Update template count for a category"""
        count_query = select(func.count(IdeationTemplate.id)).where(
            IdeationTemplate.category_id == category_id
        )
        result = await db.execute(count_query)
        count = result.scalar()
        
        update_query = select(TemplateCategory).where(TemplateCategory.id == category_id)
        category_result = await db.execute(update_query)
        category = category_result.scalar_one_or_none()
        
        if category:
            category.template_count = count or 0
            category.updated_at = datetime.utcnow()
            await db.commit()
