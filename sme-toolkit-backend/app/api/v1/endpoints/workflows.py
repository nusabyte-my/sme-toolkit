"""Owner-scoped automation schedules, dry runs and durable activity logs."""
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.auth import get_current_user
from app.config import settings
from app.database import get_db, AutomationRule, AutomationRun
from app.services.owner_service import business
from app.agents.workflow_engine import TEMPLATES, rule_data, log_data, preview_rule, run_rule, utc_now

router = APIRouter()


class RuleInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    template_key: str
    enabled: bool = False
    interval_hours: Literal[1, 6, 24, 168] = 24

    @field_validator('template_key')
    @classmethod
    def supported_template(cls, value):
        if value not in TEMPLATES:
            raise ValueError('Choose a supported internal automation template')
        return value


async def owned_rule(db, actor, rule_id):
    profile = await business(db, actor)
    rule = await db.scalar(select(AutomationRule).where(AutomationRule.id == rule_id, AutomationRule.business_profile_id == profile.id))
    if not rule:
        raise HTTPException(404, 'Automation not found')
    return profile, rule


@router.get('/')
async def overview(actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    rules = (await db.scalars(select(AutomationRule).where(AutomationRule.business_profile_id == profile.id).order_by(AutomationRule.created_at))).all()
    logs = await db.scalars(select(AutomationRun).where(AutomationRun.business_profile_id == profile.id).order_by(AutomationRun.created_at.desc()).limit(100))
    return {'templates': [{'key': key, **value} for key, value in TEMPLATES.items()],
            'rules': [rule_data(row) for row in rules], 'logs': [log_data(row) for row in logs],
            'scheduler': {'enabled': settings.automation_scheduler_enabled, 'poll_seconds': settings.automation_poll_seconds},
            'notice': 'Opt-in internal checks only. Schedules run while the backend is running. No paid AI calls, messages, publishing or budget changes.'}


@router.post('/rules', status_code=201)
async def create_rule(data: RuleInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = AutomationRule(business_profile_id=profile.id, template_key=data.template_key, enabled=data.enabled,
                         interval_hours=data.interval_hours, next_run_at=utc_now())
    db.add(row)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, 'This automation already exists for your business. Edit its schedule instead.')
    await db.refresh(row)
    return rule_data(row)


@router.put('/rules/{rule_id}')
async def save_rule(rule_id: str, data: RuleInput, actor=Depends(get_current_user), db=Depends(get_db)):
    _, row = await owned_rule(db, actor, rule_id)
    if row.template_key != data.template_key:
        raise HTTPException(422, 'An existing automation cannot change its template.')
    if row.interval_hours != data.interval_hours or (data.enabled and not row.enabled):
        row.next_run_at = utc_now()
    row.interval_hours = data.interval_hours
    row.enabled = data.enabled
    row.updated_at = utc_now()
    await db.commit()
    await db.refresh(row)
    return rule_data(row)


@router.get('/preview/{template_key}')
async def preview(template_key: str, actor=Depends(get_current_user), db=Depends(get_db)):
    if template_key not in TEMPLATES:
        raise HTTPException(404, 'Automation template not found')
    return await preview_rule(db, await business(db, actor), template_key)


@router.post('/rules/{rule_id}/check')
async def check(rule_id: str, actor=Depends(get_current_user), db=Depends(get_db)):
    profile, rule = await owned_rule(db, actor, rule_id)
    if not rule.enabled:
        raise HTTPException(409, 'Enable this rule before running it. Preview is available while paused.')
    try:
        return await run_rule(db, rule.id, profile.id, force=True)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, 'Another check already recorded this cadence slot. Refresh activity; no duplicate task was created.')
