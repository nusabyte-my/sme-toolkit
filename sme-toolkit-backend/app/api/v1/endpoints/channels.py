"""Owner channel settings and public authenticated provider callbacks."""
import hashlib
import hmac
import json
import re
import secrets
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.auth import get_current_user
from app.database import get_db, AgentChannel, BusinessAgent, ChannelMessage, ChannelOutbox
from app.services.owner_service import business
from app.services.channels import (encrypt, decrypt, channel_data, callback_url, verify_telegram, verify_whatsapp,
                                  register_telegram, ingest, send_outbox, cipher)
from app.config import settings

router=APIRouter()
webhook_router=APIRouter()


class ConnectInput(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    platform:Literal['telegram','whatsapp']
    agent_id:str=Field(min_length=1,max_length=50)
    token:str=Field(min_length=20,max_length=4000)
    phone_number_id:str=Field(default='',max_length=30)
    app_secret:str=Field(default='',max_length=200)

    @model_validator(mode='after')
    def meta_credentials(self):
        if self.platform=='whatsapp' and (not re.fullmatch(r'\d{5,30}',self.phone_number_id) or len(self.app_secret)<16):
            raise ValueError('WhatsApp needs a Meta phone-number ID and application secret for signature verification')
        return self


class ChannelSettings(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    agent_id:str=Field(min_length=1,max_length=50)
    paused:bool=False
    automation:Literal['manual','draft','auto_reply']='manual'
    response_mode:Literal['fixed','ai']='fixed'
    fixed_reply:str=Field(default='',max_length=3000)
    daily_limit:int=Field(default=50,ge=1,le=500)


class DraftInput(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    inbound_id:str|None=Field(default=None,max_length=50)
    peer:str=Field(min_length=1,max_length=80)
    content:str=Field(default='',max_length=3000)
    template_name:str=Field(default='',max_length=100,pattern=r'^[a-z0-9_]*$')
    template_language:str=Field(default='en_US',max_length=20,pattern=r'^[A-Za-z_]+$')
    template_parameters:list[str]=Field(default_factory=list,max_length=20)
    consent:bool=False

    @model_validator(mode='after')
    def content_present(self):
        if not self.content and not self.template_name:raise ValueError('Write a message or choose an approved WhatsApp template')
        if any(len(v)>1000 for v in self.template_parameters):raise ValueError('Template parameter exceeds 1000 characters')
        return self


class ReviewInput(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    action:Literal['send','reject']
    content:str|None=Field(default=None,min_length=1,max_length=3000)


async def channel_owned(db,profile,cid):
    row=await db.scalar(select(AgentChannel).where(AgentChannel.id==cid,AgentChannel.business_profile_id==profile.id))
    if not row:raise HTTPException(404,'Channel not found.')
    return row


async def agent_owned(db,profile,aid):
    row=await db.scalar(select(BusinessAgent).where(BusinessAgent.id==aid,BusinessAgent.business_profile_id==profile.id))
    if not row:raise HTTPException(404,'Agent not found.')
    return row


def no_demo(actor):
    if actor.startswith('demo-'):raise HTTPException(403,'External channels cannot be connected or sent from the demo. Sign in to your real owner workspace.')


def outbox_data(row):
    return {k:getattr(row,k) for k in ('id','channel_id','inbound_id','peer','content','template','status','provider_message_id','error')}


@router.get('/')
async def overview(actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    channels=list(await db.scalars(select(AgentChannel).where(AgentChannel.business_profile_id==profile.id).order_by(AgentChannel.created_at)))
    ids=[c.id for c in channels]
    inbound=await db.scalars(select(ChannelMessage).where(ChannelMessage.channel_id.in_(ids)).order_by(ChannelMessage.received_at.desc()).limit(100))
    outbox=await db.scalars(select(ChannelOutbox).where(ChannelOutbox.channel_id.in_(ids)).order_by(ChannelOutbox.created_at.desc()).limit(100))
    return {'channels':[channel_data(c) for c in channels], 'inbox':[{k:getattr(m,k) for k in ('id','channel_id','peer','content','status','error')} | {'received_at':m.received_at.isoformat()+'Z'} for m in inbound],
            'outbox':[outbox_data(m) for m in outbox], 'setup':{'encryption_ready':bool(settings.channel_encryption_key),'public_callback_configured':bool(settings.public_webhook_base_url),'demo':actor.startswith('demo-')},
            'notice':'Telegram uses verified Bot API tokens; WhatsApp uses Meta Cloud API, not a fake QR. Inbound automation defaults to manual. AI replies see only the selected agent’s public context. Sent means provider-accepted; WhatsApp delivery/read status comes from signed callbacks. Unknown delivery is never retried automatically.'}


@router.post('/',status_code=201)
async def connect(data:ConnectInput,actor=Depends(get_current_user),db=Depends(get_db)):
    no_demo(actor);profile=await business(db,actor);await agent_owned(db,profile,data.agent_id);cipher()
    if data.platform=='telegram':external_id,name=await verify_telegram(data.token)
    else:external_id,name=await verify_whatsapp(data.token,data.phone_number_id)
    existing=await db.scalar(select(AgentChannel).where(AgentChannel.platform==data.platform,AgentChannel.external_id==external_id))
    if existing and existing.business_profile_id!=profile.id:raise HTTPException(409,'This provider identity is already registered. Ask the administrator to review its ownership.')
    values={'token':data.token,'app_secret':data.app_secret}
    if existing:
        existing.credentials=encrypt(values);existing.agent_id=data.agent_id;existing.name=name;existing.status='verified';existing.automation='manual';row=existing
    else:
        row=AgentChannel(business_profile_id=profile.id,agent_id=data.agent_id,platform=data.platform,external_id=external_id,name=name,credentials=encrypt(values),
                         webhook_secret=secrets.token_urlsafe(32),verify_token=secrets.token_urlsafe(32),status='verified',automation='manual',response_mode='fixed',fixed_reply='',daily_limit=50)
        db.add(row)
    try:await db.commit()
    except IntegrityError:
        await db.rollback();raise HTTPException(409,'This provider identity was connected concurrently. Refresh channels.')
    return channel_data(row)


@router.post('/{channel_id}/register-webhook')
async def register(channel_id:str,actor=Depends(get_current_user),db=Depends(get_db)):
    no_demo(actor);row=await channel_owned(db,await business(db,actor),channel_id)
    if row.platform!='telegram':raise HTTPException(409,'For WhatsApp, enter this callback URL and verification token in the Meta application, then subscribe to messages.')
    await register_telegram(row)
    await db.execute(update(AgentChannel).where(AgentChannel.id==row.id,AgentChannel.status!='paused').values(status='connected'))
    await db.commit();await db.refresh(row);return channel_data(row)


@router.put('/{channel_id}')
async def configure(channel_id:str,data:ChannelSettings,actor=Depends(get_current_user),db=Depends(get_db)):
    no_demo(actor);profile=await business(db,actor);row=await channel_owned(db,profile,channel_id);agent=await agent_owned(db,profile,data.agent_id)
    await db.execute(update(AgentChannel).where(AgentChannel.id==row.id).values(name=AgentChannel.name))
    await db.refresh(row)
    if data.automation!='manual':
        if data.response_mode=='fixed' and not data.fixed_reply.strip():raise HTTPException(422,'Write a fixed response before enabling automation.')
        if data.response_mode=='ai' and not agent.public_context.strip():raise HTTPException(422,'Add explicitly public facts to the agent before enabling AI replies.')
        if data.response_mode=='ai':
            from app.api.v1.endpoints.owner import capabilities
            if not capabilities(actor)['ai_available']:raise HTTPException(503,'Configure a real text provider before enabling AI replies.')
    row.agent_id=agent.id;row.automation=data.automation;row.response_mode=data.response_mode;row.fixed_reply=data.fixed_reply;row.daily_limit=data.daily_limit
    row.status='paused' if data.paused else ('verified' if row.status=='paused' else row.status)
    await db.commit();return channel_data(row)


@router.post('/{channel_id}/outbox',status_code=201)
async def draft_message(channel_id:str,data:DraftInput,actor=Depends(get_current_user),db=Depends(get_db)):
    no_demo(actor);profile=await business(db,actor);channel=await channel_owned(db,profile,channel_id)
    if channel.platform=='whatsapp' and not re.fullmatch(r'\d{7,16}',data.peer):raise HTTPException(422,'WhatsApp recipient must include country code, digits only.')
    if channel.platform=='telegram' and not re.fullmatch(r'-?\d{1,20}',data.peer):raise HTTPException(422,'Use the numeric Telegram chat ID from a received message.')
    if data.inbound_id:
        inbound=await db.scalar(select(ChannelMessage).where(ChannelMessage.id==data.inbound_id,ChannelMessage.channel_id==channel.id,ChannelMessage.peer==data.peer))
        if not inbound:raise HTTPException(404,'Inbound message does not match this channel and recipient.')
    elif not data.consent:raise HTTPException(422,'Confirm recipient opt-in before composing an outbound message.')
    template=None
    if data.template_name:
        if channel.platform!='whatsapp':raise HTTPException(422,'Templates are available only for WhatsApp.')
        if not data.consent:raise HTTPException(422,'Confirm opt-in for this WhatsApp template.')
        template={'name':data.template_name,'language':{'code':data.template_language}}
        if data.template_parameters:template['components']=[{'type':'body','parameters':[{'type':'text','text':value} for value in data.template_parameters]}]
    row=ChannelOutbox(channel_id=channel.id,inbound_id=data.inbound_id,peer=data.peer,content=data.content,template=template,consent=data.consent,status='pending')
    db.add(row)
    try:await db.commit()
    except IntegrityError:
        await db.rollback();raise HTTPException(409,'A reply for this inbound message already exists. Review the outbox instead of duplicating it.')
    return outbox_data(row)


@router.post('/outbox/{message_id}/review')
async def review(message_id:str,data:ReviewInput,actor=Depends(get_current_user),db=Depends(get_db)):
    no_demo(actor);profile=await business(db,actor)
    row=await db.scalar(select(ChannelOutbox).join(AgentChannel,AgentChannel.id==ChannelOutbox.channel_id).where(ChannelOutbox.id==message_id,AgentChannel.business_profile_id==profile.id))
    if not row:raise HTTPException(404,'Message not found.')
    await db.execute(update(AgentChannel).where(AgentChannel.id==row.channel_id).values(name=AgentChannel.name))
    await db.refresh(row)
    if row.status!='pending':raise HTTPException(409,'Only a pending message can be sent or rejected. Check its existing delivery status.')
    if data.action=='reject':row.status='rejected';await db.commit()
    else:
        if data.content is not None:
            if row.template:raise HTTPException(422,'Template payloads cannot be edited as plain text. Reject and create a new template draft.')
            row.content=data.content
        await db.flush();row=await send_outbox(db,row.id,profile.id)
    return outbox_data(row)


@webhook_router.get('/{channel_id}')
async def verify_webhook(channel_id:str,request:Request,db=Depends(get_db)):
    channel=await db.get(AgentChannel,channel_id)
    token=request.query_params.get('hub.verify_token','')
    if not channel or channel.platform!='whatsapp' or request.query_params.get('hub.mode')!='subscribe' or not secrets.compare_digest(token,channel.verify_token):raise HTTPException(403,'Webhook verification failed.')
    challenge=request.query_params.get('hub.challenge','')
    if not challenge or len(challenge)>200:raise HTTPException(400,'Invalid verification challenge.')
    if channel.status!='paused':channel.status='connected'
    await db.commit();return Response(challenge,media_type='text/plain')


@webhook_router.post('/{channel_id}')
async def inbound_webhook(channel_id:str,request:Request,db=Depends(get_db)):
    channel=await db.get(AgentChannel,channel_id)
    if not channel:raise HTTPException(404,'Channel not found.')
    raw=bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw)>512000:raise HTTPException(413,'Webhook payload too large.')
    if channel.platform=='telegram':
        if not secrets.compare_digest(request.headers.get('X-Telegram-Bot-Api-Secret-Token',''),channel.webhook_secret):raise HTTPException(403,'Invalid webhook signature.')
    else:
        secret=decrypt(channel.credentials)['app_secret']
        expected='sha256='+hmac.new(secret.encode(),bytes(raw),hashlib.sha256).hexdigest()
        if not secrets.compare_digest(request.headers.get('X-Hub-Signature-256',''),expected):raise HTTPException(403,'Invalid webhook signature.')
    try:payload=json.loads(raw)
    except (ValueError,UnicodeDecodeError):raise HTTPException(400,'Invalid webhook JSON.')
    if not isinstance(payload,dict):raise HTTPException(400,'Invalid webhook body.')
    try:count=await ingest(db,channel,payload)
    except (TypeError,AttributeError,ValueError):
        await db.rollback();raise HTTPException(400,'Malformed provider message payload.')
    return {'received':count}
