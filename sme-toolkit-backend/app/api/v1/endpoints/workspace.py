"""Business documents, owner actions and CRM. All records belong to the authenticated business."""
from datetime import date, datetime, timezone
from urllib.parse import urlsplit
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select, func, or_
from app.auth import get_current_user
from app.database import get_db, WorkspaceDocument, OwnerTask, Lead
from app.services.owner_service import business, iso

router = APIRouter()
DocumentKind = Literal['canvas','strategy','ideation','seo','research']
FIELDS = {
    'canvas': {'partners','activities','resources','value','relationships','channels','customers','costs','revenue'},
    'strategy': {'goal','baseline','target','deadline','constraints','options','decision','evidence','next_action'},
    'ideation': {'problem','audience','idea','benefit','assumptions','experiment','metric','decision'},
    'seo': {'page_title','description','url','business_name','business_type','content_outline','keywords'},
    'research': {'question','segment','source_url','source_title','published_date','evidence','assumptions','conclusion'},
}

class DocumentInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    kind: DocumentKind
    title: str = Field(min_length=1,max_length=180)
    fields: dict[str,str]
    @field_validator('fields')
    @classmethod
    def bounded_fields(cls, value):
        if len(value)>15 or any(len(k)>40 or len(v)>12000 for k,v in value.items()):
            raise ValueError('Document fields exceed their size limit')
        for key in ('url','source_url'):
            if value.get(key):
                url=urlsplit(value[key])
                if url.scheme not in ('http','https') or not url.hostname or url.username or url.password:
                    raise ValueError(f'{key} must be an HTTP(S) URL without credentials')
        for key in ('deadline','published_date'):
            if value.get(key):date.fromisoformat(value[key])
        return value

class TaskInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str = Field(min_length=1,max_length=180)
    notes: str = Field(default='',max_length=4000)
    owner: str = Field(default='',max_length=120)
    due_date: date | None = None
    status: Literal['open','in_progress','done'] = 'open'

class LeadInput(BaseModel):
    model_config = ConfigDict(extra='forbid',str_strip_whitespace=True)
    name: str = Field(min_length=1,max_length=160)
    email: str = Field(default='',max_length=254)
    phone: str = Field(default='',max_length=60)
    company: str = Field(default='',max_length=160)
    lead_source: str = Field(default='',max_length=120)
    status: Literal['new','contacted','qualified','proposal','won','lost'] = 'new'
    notes: str = Field(default='',max_length=4000)
    next_follow_up_at: datetime | None = None
    @field_validator('email')
    @classmethod
    def valid_email(cls,value):
        if value and ('@' not in value or any(c.isspace() for c in value)):
            raise ValueError('Enter a valid email address or leave it blank')
        return value
    @field_validator('next_follow_up_at')
    @classmethod
    def utc_followup(cls,value):
        if value and value.tzinfo is None:
            raise ValueError('Follow-up time requires a timezone offset')
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value else None

async def owned(db,model,item_id,profile):
    row=await db.scalar(select(model).where(model.id==item_id,model.business_profile_id==profile.id))
    if not row:raise HTTPException(404,'Record not found')
    return row

def document_data(row):
    return dict(id=row.id,kind=row.kind,title=row.title,fields=row.fields,created_at=iso(row.created_at),updated_at=iso(row.updated_at))

def task_data(row):
    return {key:getattr(row,key) for key in ('id','title','notes','owner','due_date','status')} | {'created_at':iso(row.created_at),'updated_at':iso(row.updated_at)}

def lead_data(row):
    return {key:getattr(row,key) for key in ('id','name','email','phone','company','lead_source','status','notes')} | {'next_follow_up_at':iso(row.next_follow_up_at),'created_at':iso(row.created_at),'updated_at':iso(row.updated_at)}

@router.get('/documents')
async def documents(kind:DocumentKind, actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    rows=await db.scalars(select(WorkspaceDocument).where(WorkspaceDocument.business_profile_id==profile.id,WorkspaceDocument.kind==kind).order_by(WorkspaceDocument.updated_at.desc()).limit(100))
    return [document_data(row) for row in rows]

@router.post('/documents',status_code=201)
async def create_document(data:DocumentInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    if set(data.fields)-FIELDS[data.kind]:raise HTTPException(422,'Unsupported fields for this document')
    row=WorkspaceDocument(business_profile_id=profile.id,**data.model_dump())
    db.add(row);await db.commit();await db.refresh(row)
    return document_data(row)

@router.put('/documents/{item_id}')
async def save_document(item_id:str,data:DocumentInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);row=await owned(db,WorkspaceDocument,item_id,profile)
    if row.kind!=data.kind or set(data.fields)-FIELDS[data.kind]:raise HTTPException(422,'Document kind or fields do not match')
    row.title=data.title;row.fields=data.fields;row.updated_at=datetime.utcnow()
    await db.commit();await db.refresh(row)
    return document_data(row)

@router.get('/tasks')
async def tasks(actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    rows=await db.scalars(select(OwnerTask).where(OwnerTask.business_profile_id==profile.id).order_by(OwnerTask.created_at.desc()).limit(200))
    return [task_data(row) for row in rows]

@router.post('/tasks',status_code=201)
async def create_task(data:TaskInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    values=data.model_dump();values['due_date']=str(data.due_date) if data.due_date else None
    row=OwnerTask(business_profile_id=profile.id,**values)
    db.add(row);await db.commit();await db.refresh(row)
    return task_data(row)

@router.put('/tasks/{item_id}')
async def save_task(item_id:str,data:TaskInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);row=await owned(db,OwnerTask,item_id,profile)
    for key,value in data.model_dump().items():setattr(row,key,str(value) if key=='due_date' and value else value)
    row.updated_at=datetime.utcnow();await db.commit();await db.refresh(row)
    return task_data(row)

@router.get('/leads')
async def leads(search:str=Query('',max_length=160),status:str=Query('',max_length=20),page:int=Query(1,ge=1),actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);filters=[Lead.business_profile_id==profile.id]
    if search:filters.append(or_(Lead.name.icontains(search,autoescape=True),Lead.company.icontains(search,autoescape=True),Lead.email.icontains(search,autoescape=True)))
    if status:filters.append(Lead.status==status)
    total=await db.scalar(select(func.count()).select_from(Lead).where(*filters))
    rows=await db.scalars(select(Lead).where(*filters).order_by(Lead.updated_at.desc()).offset((page-1)*30).limit(30))
    stages=await db.execute(select(Lead.status,func.count()).where(Lead.business_profile_id==profile.id).group_by(Lead.status))
    overdue=await db.scalar(select(func.count()).select_from(Lead).where(Lead.business_profile_id==profile.id,Lead.status.notin_(['won','lost']),Lead.next_follow_up_at<datetime.utcnow()))
    return dict(items=[lead_data(row) for row in rows],total=total,page=page,size=30,stages=dict(stages.all()),overdue=overdue)

@router.post('/leads',status_code=201)
async def create_lead(data:LeadInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    row=Lead(business_profile_id=profile.id,**data.model_dump())
    db.add(row);await db.commit();await db.refresh(row)
    return lead_data(row)

@router.put('/leads/{item_id}')
async def save_lead(item_id:str,data:LeadInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);row=await owned(db,Lead,item_id,profile)
    for key,value in data.model_dump().items():setattr(row,key,value)
    row.updated_at=datetime.utcnow();await db.commit();await db.refresh(row)
    return lead_data(row)
