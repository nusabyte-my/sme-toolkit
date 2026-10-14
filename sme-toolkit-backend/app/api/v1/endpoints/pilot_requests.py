"""Public pilot intake; private admin review. No email or booking is implied."""
import hashlib
import hmac
import re
from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.exc import IntegrityError

from app.auth import get_admin_user
from app.config import settings
from app.database import PilotIntakeLimit, PilotRequest, get_db

router = APIRouter()


class PilotInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    submission_id: UUID
    name: str = Field(min_length=2, max_length=100)
    company: str = Field(min_length=2, max_length=160)
    email: str = Field(min_length=5, max_length=254)
    workflow: Literal['sales', 'billing', 'marketing', 'agents', 'enterprise']
    goal: str = Field(min_length=15, max_length=1500)
    consent: bool = Field(strict=True)
    website_url: str = Field(default='', max_length=200)

    @field_validator('email')
    @classmethod
    def email_address(cls, value):
        if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", value):
            raise ValueError('Enter a valid email address, such as name@company.com')
        return value.lower()

    @field_validator('name', 'company', 'goal')
    @classmethod
    def plain_text(cls, value):
        if any(ord(char) < 32 and char not in '\n\t' for char in value):
            raise ValueError('Remove unsupported control characters')
        return value

    @field_validator('consent')
    @classmethod
    def contact_permission(cls, value):
        if not value:
            raise ValueError('Allow contact about this enquiry before sending')
        return value


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['new', 'contacted', 'closed']


def fields(data):
    return data.model_dump(include={'name', 'company', 'email', 'workflow', 'goal'})


def receipt(row):
    return {'reference': row.id, 'status': 'received'}


def item(row):
    return {key: getattr(row, key) for key in ('id', 'name', 'company', 'email', 'workflow', 'goal', 'status')} | {
        'created_at': row.created_at.isoformat() + 'Z',
        'contact_consent_at': row.contact_consent_at.isoformat() + 'Z',
    }


async def limit_intake(db, request, email):
    now = datetime.utcnow()
    hour = now.replace(minute=0, second=0, microsecond=0)
    day = hour.replace(hour=0)
    # Only trust the ASGI peer. Forwarded headers require an explicitly trusted deployment proxy.
    peer = request.client.host if request.client else 'unknown'
    digest = lambda value: hmac.new(settings.jwt_secret_key.encode(), value.encode(), hashlib.sha256).hexdigest()
    quotas = [('global', hour, 100, timedelta(hours=1)), ('peer:' + digest(peer), hour, 10, timedelta(hours=1)),
              ('email:' + digest(email), day, 3, timedelta(days=1))]
    await db.execute(delete(PilotIntakeLimit).where(PilotIntakeLimit.expires_at <= now))
    insert = sqlite_insert if db.bind.dialect.name == 'sqlite' else postgres_insert
    for subject, start, maximum, duration in quotas:
        key = subject + ':' + start.isoformat()
        await db.execute(insert(PilotIntakeLimit).values(key=key, count=0, expires_at=start + duration).on_conflict_do_nothing(index_elements=['key']))
        claimed = await db.execute(update(PilotIntakeLimit).where(PilotIntakeLimit.key == key, PilotIntakeLimit.count < maximum).values(count=PilotIntakeLimit.count + 1))
        if not claimed.rowcount:
            await db.rollback()
            seconds = max(1, int((start + duration - now).total_seconds()))
            raise HTTPException(429, 'Too many pilot enquiries. Please wait before sending another request.', headers={'Retry-After': str(seconds)})


@router.post('', status_code=201, openapi_extra={'requestBody': {'required': True, 'content': {'application/json': {'schema': PilotInput.model_json_schema()}}}})
async def submit(request: Request, response: Response, db=Depends(get_db)):
    if request.headers.get('content-type', '').split(';')[0] != 'application/json':
        raise HTTPException(415, 'Send the enquiry as JSON.')
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > 12000:
            raise HTTPException(413, 'This enquiry is too large. Keep the goal under 1,500 characters.')
        raw.extend(chunk)
    try:
        data = PilotInput.model_validate_json(raw)
    except ValidationError as exc:
        raise HTTPException(422, [{'loc': ['body', *error['loc']], 'msg': error['msg']} for error in exc.errors(include_input=False, include_context=False)])
    if data.website_url:
        raise HTTPException(400, 'This enquiry could not be accepted. Leave the website field blank.')
    existing = await db.get(PilotRequest, str(data.submission_id))
    if existing:
        if any(getattr(existing, key) != value for key, value in fields(data).items()):
            raise HTTPException(409, 'This submission reference already exists with different details. Reload before starting another enquiry.')
        response.status_code = 200
        return receipt(existing)
    await limit_intake(db, request, data.email)
    row = PilotRequest(id=str(data.submission_id), **fields(data))
    db.add(row)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        existing = await db.get(PilotRequest, str(data.submission_id))
        if not existing or any(getattr(existing, key) != value for key, value in fields(data).items()):
            raise HTTPException(409, 'The enquiry could not be saved with this reference.')
        response.status_code = 200
        return receipt(existing)
    return receipt(row)


@router.get('')
async def inbox(response: Response, state: Literal['all', 'new', 'contacted', 'closed'] = 'new', limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0), actor=Depends(get_admin_user), db=Depends(get_db)):
    response.headers['Cache-Control'] = 'no-store'
    query = select(PilotRequest)
    if state != 'all':
        query = query.where(PilotRequest.status == state)
    rows = list(await db.scalars(query.order_by(PilotRequest.created_at.desc(), PilotRequest.id).offset(offset).limit(limit + 1)))
    return {'items': [item(row) for row in rows[:limit]], 'has_more': len(rows) > limit}


@router.patch('/{request_id}')
async def review(request_id: str, data: ReviewInput, response: Response, actor=Depends(get_admin_user), db=Depends(get_db)):
    row = await db.get(PilotRequest, request_id)
    if not row:
        raise HTTPException(404, 'Pilot enquiry not found.')
    row.status = data.status
    row.updated_at = datetime.utcnow()
    await db.commit()
    response.headers['Cache-Control'] = 'no-store'
    return item(row)


@router.delete('/{request_id}', status_code=204)
async def erase(request_id: str, actor=Depends(get_admin_user), db=Depends(get_db)):
    row = await db.get(PilotRequest, request_id)
    if not row:
        raise HTTPException(404, 'Pilot enquiry not found.')
    await db.delete(row)
    await db.commit()
