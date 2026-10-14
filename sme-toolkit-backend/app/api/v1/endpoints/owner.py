"""Persistent owner portal. Approvals record review, never external publication."""
import asyncio
import json
import httpx
import re
from datetime import datetime, timezone
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError
from app.auth import get_current_user
from app.config import settings
from app.database import get_db, BusinessProfile, OwnerAgentRun, OwnerCampaign, OwnerTask, Lead, Employee, LeaveRequest, BookEntry, AutomationRule, AutomationRun
from app.services.owner_service import business, context_data, sales_summary, run_data, campaign_data, ledger_brief
from app.services.advisors import advisor_catalog, public_advisors, advisor_evidence, rules_output

router = APIRouter()


@router.get('/advisors')
async def list_advisors(actor=Depends(get_current_user)):
    return public_advisors()


class ContextInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    company_name: str = Field(min_length=1, max_length=160)
    industry: str = Field(default='', max_length=160)
    business_description: str = Field(default='', max_length=4000)
    products_services: str = Field(default='', max_length=4000)
    target_market: str = Field(default='', max_length=2000)
    brand_voice: str = Field(default='', max_length=1000)
    goals: str = Field(default='', max_length=2000)
    currency: str = Field(default='MYR', pattern=r'^[A-Z]{3}$')
    timezone: str = Field(default='Asia/Kuala_Lumpur', max_length=80)
    website: str = Field(default='', max_length=500)
    proof_points: str = Field(default='', max_length=4000)
    constraints: str = Field(default='', max_length=4000)
    logo_data_url: str = Field(default='', max_length=500000)

    @field_validator('timezone')
    @classmethod
    def valid_zone(cls, value):
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError('Use a valid IANA timezone, such as Asia/Kuala_Lumpur')
        return value

    @field_validator('website')
    @classmethod
    def valid_website(cls, value):
        if value:
            url = urlsplit(value)
            if url.scheme not in ('https', 'http') or not url.hostname or url.username or url.password:
                raise ValueError('Use an http(s) website URL without credentials')
        return value


class RunInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    kind: str = Field(min_length=1, max_length=60)
    objective: str = Field(min_length=3, max_length=16000)

    @field_validator('kind')
    @classmethod
    def known_advisor(cls, value):
        if value not in advisor_catalog():
            raise ValueError('Choose an advisor from the skill catalog')
        return value


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['approved', 'dismissed']


class CampaignInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=160)
    platform: str = Field(min_length=1, max_length=80)
    caption: str = Field(min_length=1, max_length=10000)
    scheduled_at: datetime | None = None

    @field_validator('scheduled_at')
    @classmethod
    def aware_date(cls, value):
        if value and value.tzinfo is None:
            raise ValueError('Planned time must include a timezone offset')
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value else None


class CampaignUpdate(CampaignInput):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    platform: str | None = Field(default=None, min_length=1, max_length=80)
    caption: str | None = Field(default=None, min_length=1, max_length=10000)
    status: Literal['draft', 'approved', 'archived'] | None = None


def capabilities(actor=''):
    keys = {'fiqstr-v2': settings.fiqstr_api_key, 'gemini': settings.gemini_api_key,
            'groq': settings.groq_api_key, 'mistral': settings.mistral_api_key, 'deepseek': settings.deepseek_api_key}
    name = None if actor.startswith('demo-') else next((name.strip() for name in settings.llm_provider_priority.split(',') if keys.get(name.strip())), None)
    return {'ai_available': name is not None, 'ai_provider': name,
            'publishing_available': False, 'marketplace_sync_available': False}


@router.get('/context')
async def get_context(actor=Depends(get_current_user), db=Depends(get_db)):
    return context_data(await business(db, actor, False))


@router.put('/context')
async def save_context(data: ContextInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor, False)
    if profile is None:
        profile = BusinessProfile(user_id=actor, company_name=data.company_name)
        db.add(profile)
    profile.company_name = data.company_name
    profile.industry = data.industry
    profile.website = data.website
    profile.meta_json = {**(profile.meta_json or {}), 'owner_context': data.model_dump()}
    profile.updated_at = datetime.utcnow()
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, 'Business context changed in another request. Reload and save again.')
    await db.refresh(profile)
    return context_data(profile)


@router.get('/overview')
async def overview(days: int = Query(30, ge=1, le=365), actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor, False)
    runs, campaigns, attention = [], [], []
    if profile:
        runs = (await db.scalars(select(OwnerAgentRun).where(OwnerAgentRun.business_profile_id == profile.id).order_by(OwnerAgentRun.created_at.desc()).limit(100))).all()
        campaigns = (await db.scalars(select(OwnerCampaign).where(OwnerCampaign.business_profile_id == profile.id).order_by(OwnerCampaign.updated_at.desc()).limit(100))).all()
    summary = await sales_summary(db, profile, days)
    context = context_data(profile)
    if not context or not all(context[k] for k in ('products_services', 'target_market', 'goals')):
        attention.append(dict(id='context', title='Complete your business context', detail='Products, customers and goals keep agent recommendations relevant.', view='profiles'))
    if not summary['orders']:
        attention.append(dict(id='sales', title='Add your first recorded sale', detail='Revenue and channel comparisons use your saved ledger, not sample data.', view='sales'))
    if summary['pending_orders']:
        attention.append(dict(id='pending', title=f"{summary['pending_orders']} orders need attention", detail='Review payment and fulfilment before marking an order completed.', view='sales'))
    if any(run.status == 'needs_review' for run in runs):
        attention.append(dict(id='reviews', title='Review agent findings', detail='Approve useful findings or dismiss them. No external action runs automatically.', view='agent_forge'))
    if any(run.status == 'failed' for run in runs):
        attention.append(dict(id='failed-runs', title='Agent generation needs attention', detail='Review failed runs and provider configuration. Existing drafts are unchanged.', view='agent_forge'))
    if profile:
        open_tasks = await db.scalar(select(func.count()).select_from(OwnerTask).where(OwnerTask.business_profile_id==profile.id,OwnerTask.status!='done'))
        if open_tasks:
            attention.append(dict(id='tasks',title=f'{open_tasks} owner actions open',detail='Assign responsibility, track due dates and close completed actions.',view='quickwins'))
    if any(c.status == 'draft' for c in campaigns):
        attention.append(dict(id='drafts', title='Review marketing drafts', detail='Edit and approve content before using it on your chosen channel.', view='social_studio'))
    operations = dict(employees=0, pending_leave=0, journal_entries=0, enabled_rules=0, latest_automation=None)
    if profile:
        operations['employees'] = await db.scalar(select(func.count()).select_from(Employee).where(Employee.business_profile_id==profile.id,Employee.status!='inactive'))
        operations['pending_leave'] = await db.scalar(select(func.count()).select_from(LeaveRequest).where(LeaveRequest.business_profile_id==profile.id,LeaveRequest.status=='pending'))
        operations['journal_entries'] = await db.scalar(select(func.count()).select_from(BookEntry).where(BookEntry.business_profile_id==profile.id))
        operations['enabled_rules'] = await db.scalar(select(func.count()).select_from(AutomationRule).where(AutomationRule.business_profile_id==profile.id,AutomationRule.enabled.is_(True)))
        latest = await db.scalar(select(AutomationRun).where(AutomationRun.business_profile_id==profile.id).order_by(AutomationRun.created_at.desc()).limit(1))
        if latest: operations['latest_automation'] = {'summary':latest.summary,'status':latest.status}
        if operations['pending_leave']:
            attention.append(dict(id='leave',title=f"{operations['pending_leave']} leave requests await review",detail='Check availability and review each request. No leave is approved automatically.',view='hr'))
    return dict(context=context, sales=summary, agents=[run_data(r) for r in runs],
                campaigns=[campaign_data(c) for c in campaigns], attention=attention, capabilities=capabilities(actor), operations=operations)


@router.get('/runs')
async def list_runs(actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    rows = await db.scalars(select(OwnerAgentRun).where(OwnerAgentRun.business_profile_id == profile.id).order_by(OwnerAgentRun.created_at.desc()).limit(100))
    return [run_data(row) for row in rows]


@router.post('/runs', status_code=201)
async def execute_run(data: RunInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    context = context_data(profile)
    skill = advisor_catalog()[data.kind]
    evidence = await advisor_evidence(db, profile, data.kind)
    snapshot = {**context, '_advisor': {'name': skill['name'], 'version': skill['version'], 'mode': skill['mode']}, '_evidence': {**evidence, 'issues': evidence['issues'][:100]}}
    row = OwnerAgentRun(business_profile_id=profile.id, kind=data.kind, objective=data.objective,
                        context_snapshot=snapshot, provider='rules', status='needs_review')
    if skill['mode'] == 'llm':
        if actor.startswith('demo-'):
            raise HTTPException(403, 'Paid AI generation is disabled in the demo. Run an evidence-rule advisor or edit the sample drafts.')
        name = capabilities(actor)['ai_provider']
        if not name:
            raise HTTPException(503, 'No AI provider is configured. You can still write and save a marketing draft manually.')
        from app.providers.router import get_provider_router
        from app.providers.base import LLMRequest
        provider_router = get_provider_router()
        provider = provider_router.llm_providers.get(name)
        if not provider or name == 'mock':
            raise HTTPException(503, 'The configured AI provider is unavailable. Save a manual draft or configure the provider on the server.')
        limit = await provider_router.rate_limiter.check_rate_limit(actor, 'free', 'llm')
        if not limit.allowed:
            raise HTTPException(429, 'AI request limit reached. Try later or write a manual draft.')
        row.provider = name
        request = LLMRequest(prompt=json.dumps({'business_context': context, 'evidence': evidence, 'objective': data.objective}, ensure_ascii=False), user_id=actor,
                             system_prompt=skill['instructions'], max_tokens=4096)
        try:
            if name == 'gemini':
                model = settings.gemini_text_model
                if not re.fullmatch(r'[A-Za-z0-9._-]+', model):
                    raise ValueError('Invalid text model configuration')
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(
                        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                        headers={'x-goog-api-key': settings.gemini_api_key},
                        json={'systemInstruction': {'parts': [{'text': request.system_prompt}]},
                              'contents': [{'parts': [{'text': request.prompt}]}],
                              'generationConfig': {'maxOutputTokens': 2048, 'temperature': 0.7}},
                    )
                response.raise_for_status()
                payload = response.json()
                output = '\n'.join(part['text'] for candidate in payload.get('candidates', [])
                                   for part in candidate.get('content', {}).get('parts', [])
                                   if part.get('text') and not part.get('thought'))
            else:
                result = await asyncio.wait_for(provider.execute(request), timeout=70)
                output = result.content if result.success else ''
            if not output or not output.strip() or output.startswith('[ERROR]'):
                raise ValueError('Provider returned no usable content')
            row.output = output[:20000]
            await provider_router.rate_limiter.increment_usage(actor, 'llm')
        except httpx.HTTPStatusError as exc:
            row.status = 'failed'
            row.output = ''
            payload = exc.response.json() if exc.response.headers.get('content-type', '').startswith('application/json') else {}
            reasons = [entry.get('reason') for entry in payload.get('error', {}).get('details', []) if isinstance(entry, dict)]
            row.error = ('The configured Gemini API key is invalid. Update GEMINI_API_KEY on the server.'
                         if 'API_KEY_INVALID' in reasons else
                         f'AI provider rejected generation (HTTP {exc.response.status_code}). Check model access, quota and billing. Existing drafts are unchanged.')
        except Exception:
            row.status = 'failed'
            row.output = ''
            row.error = 'AI generation failed. Your business data is unchanged. Retry or write a manual draft.'
    else:
        row.output = rules_output(data.kind, data.objective, context, evidence)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return run_data(row)


@router.patch('/runs/{run_id}')
async def review_run(run_id: str, data: ReviewInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await db.scalar(select(OwnerAgentRun).where(OwnerAgentRun.id == run_id, OwnerAgentRun.business_profile_id == profile.id))
    if not row:
        raise HTTPException(404, 'Agent run not found')
    if row.status == data.status:
        return run_data(row)
    result = await db.execute(update(OwnerAgentRun).where(OwnerAgentRun.id == run_id, OwnerAgentRun.business_profile_id == profile.id, OwnerAgentRun.status == 'needs_review').values(status=data.status))
    if not result.rowcount:
        raise HTTPException(409, 'Only findings awaiting review can be approved or dismissed.')
    await db.commit()
    await db.refresh(row)
    return run_data(row)


@router.get('/campaigns')
async def list_campaigns(actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    rows = await db.scalars(select(OwnerCampaign).where(OwnerCampaign.business_profile_id == profile.id).order_by(OwnerCampaign.updated_at.desc()).limit(100))
    return [campaign_data(row) for row in rows]


@router.post('/campaigns', status_code=201)
async def create_campaign(data: CampaignInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = OwnerCampaign(business_profile_id=profile.id, **data.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return campaign_data(row)


@router.patch('/campaigns/{campaign_id}')
async def edit_campaign(campaign_id: str, data: CampaignUpdate, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await db.scalar(select(OwnerCampaign).where(OwnerCampaign.id == campaign_id, OwnerCampaign.business_profile_id == profile.id))
    if not row:
        raise HTTPException(404, 'Campaign not found')
    values = data.model_dump(exclude_unset=True)
    if any(values.get(k) is None for k in values if k != 'scheduled_at'):
        raise HTTPException(422, 'Only planned time may be cleared.')
    if row.status == 'archived' and values.get('status') != 'draft':
        raise HTTPException(409, 'Restore an archived campaign to draft before editing.')
    if any(k in values for k in ('title', 'platform', 'caption', 'scheduled_at')):
        values['status'] = 'draft'  # Editing invalidates prior approval.
    for key, value in values.items():
        setattr(row, key, value)
    row.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(row)
    return campaign_data(row)
