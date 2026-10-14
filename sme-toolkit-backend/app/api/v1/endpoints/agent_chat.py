"""Persistent chat, guided/AI agent creation, tool permissions and explicit mutation approval."""
from datetime import datetime, timedelta, timezone
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import select, update, func
from app.auth import get_current_user
from app.database import (get_db, BusinessAgent, AgentConversation, AgentMessage, AgentProposal, OwnerTask,
                          AgentChannel, AgentScheduleRun, BusinessProfile, async_session_maker)
from app.services.owner_service import business, iso
from app.services.agent_runtime import AgentSpec, TOOLS, agent_data, execute_turn, propose
from app.api.v1.endpoints.bookkeeping import lock_books

router=APIRouter()


class ConversationInput(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    title:str=Field(default='New conversation',min_length=1,max_length=160)
    agent_id:str|None=Field(default=None,max_length=50)


class MessageInput(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    content:str=Field(min_length=1,max_length=12000)
    mode:Literal['guided','ai']='guided'


class ProposalInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    action:Literal['approve','reject']
    payload:dict|None=None


async def owned_conversation(db,profile,cid):
    row=await db.scalar(select(AgentConversation).where(AgentConversation.id==cid,AgentConversation.business_profile_id==profile.id))
    if not row:raise HTTPException(404,'Conversation not found.')
    return row


async def owned_agent(db,profile,aid):
    row=await db.scalar(select(BusinessAgent).where(BusinessAgent.id==aid,BusinessAgent.business_profile_id==profile.id))
    if not row:raise HTTPException(404,'Agent not found.')
    return row


async def conversation_data(db,row):
    messages=list(await db.scalars(select(AgentMessage).where(AgentMessage.conversation_id==row.id).order_by(AgentMessage.created_at.desc(),AgentMessage.id).limit(100)))
    proposals=await db.scalars(select(AgentProposal).where(AgentProposal.conversation_id==row.id).order_by(AgentProposal.created_at.desc()).limit(50))
    return {'id':row.id,'title':row.title,'agent_id':row.agent_id,'busy':bool(row.busy_until and row.busy_until>datetime.utcnow()),
            'messages':[{'id':m.id,'role':m.role,'content':m.content,'trace':m.trace,'created_at':iso(m.created_at)} for m in reversed(messages)],
            'proposals':[{k:getattr(p,k) for k in ('id','kind','payload','status','result')} for p in proposals],
            'builder_stage':(row.builder_state or {}).get('stage')}


@router.get('/')
async def overview(actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    from app.api.v1.endpoints.owner import capabilities
    agents=await db.scalars(select(BusinessAgent).where(BusinessAgent.business_profile_id==profile.id).order_by(BusinessAgent.created_at))
    conversations=await db.scalars(select(AgentConversation).where(AgentConversation.business_profile_id==profile.id).order_by(AgentConversation.updated_at.desc()).limit(50))
    return {'agents':[agent_data(a) for a in agents], 'conversations':[{'id':c.id,'title':c.title,'agent_id':c.agent_id,'updated_at':iso(c.updated_at)} for c in conversations],
            'tools':[{'name':name,'description':description} for name,description in TOOLS.items()], 'ai_available':capabilities(actor)['ai_available'],
            'notice':'Guided mode is deterministic, not an AI simulation. AI mode uses your configured provider, up to five tool steps per turn. Business writes require approval. No shell, code execution, arbitrary URL tools or autonomous payments.'}


@router.post('/conversations',status_code=201)
async def create_conversation(data:ConversationInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    if data.agent_id:await owned_agent(db,profile,data.agent_id)
    row=AgentConversation(business_profile_id=profile.id,agent_id=data.agent_id,title=data.title,builder_state={})
    db.add(row);await db.commit();return await conversation_data(db,row)


@router.get('/conversations/{conversation_id}')
async def get_conversation(conversation_id:str,actor=Depends(get_current_user),db=Depends(get_db)):
    return await conversation_data(db,await owned_conversation(db,await business(db,actor),conversation_id))


@router.post('/conversations/{conversation_id}/messages')
async def send_message(conversation_id:str,data:MessageInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);conversation=await owned_conversation(db,profile,conversation_id)
    if conversation.agent_id:
        agent=await owned_agent(db,profile,conversation.agent_id)
        if not agent.enabled:raise HTTPException(409,'This agent is paused. Enable it before sending a message.')
    await execute_turn(db,profile,conversation,data.content,data.mode)
    await db.refresh(conversation)
    return await conversation_data(db,conversation)


@router.post('/conversations/{conversation_id}/agent-spec')
async def propose_spec(conversation_id:str,data:AgentSpec,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);conversation=await owned_conversation(db,profile,conversation_id)
    if conversation.agent_id:raise HTTPException(409,'Create agents in a builder conversation.')
    await propose(db,profile,conversation,'create_agent',data.model_dump())
    db.add(AgentMessage(conversation_id=conversation.id,role='assistant',content='Agent specification prepared. Review and approve it below.',trace=[]))
    await db.commit();return await conversation_data(db,conversation)


@router.put('/agents/{agent_id}')
async def save_agent(agent_id:str,data:AgentSpec,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);row=await owned_agent(db,profile,agent_id)
    if data.interval_hours and not data.schedule_prompt.strip():raise HTTPException(422,'A scheduled agent needs a prompt or /run command.')
    # Scheduled runs are deterministic evidence/tool commands; paid AI never starts merely because a timer fired.
    if data.interval_hours and not (data.schedule_prompt.strip()=='/run' or data.schedule_prompt.strip().startswith('/review ')):
        raise HTTPException(422,'Scheduled work supports /run or /review advisor_name. Run free-form AI requests interactively.')
    for key,value in data.model_dump().items():setattr(row,key,value)
    row.updated_at=datetime.utcnow();row.next_run_at=datetime.utcnow()+timedelta(hours=data.interval_hours) if data.enabled and data.interval_hours else None
    await db.commit();return agent_data(row)


@router.post('/proposals/{proposal_id}')
async def decide_proposal(proposal_id:str,data:ProposalInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);await lock_books(db,profile)
    row=await db.scalar(select(AgentProposal).where(AgentProposal.id==proposal_id,AgentProposal.business_profile_id==profile.id))
    if not row:raise HTTPException(404,'Proposal not found.')
    if row.status!='pending':raise HTTPException(409,'This proposal has already been reviewed.')
    if data.action=='reject':row.status='rejected'
    else:
        payload=data.payload if data.payload is not None else row.payload
        from app.api.v1.endpoints.workspace import TaskInput
        from app.api.v1.endpoints.billing import DocumentInput
        schema={'create_agent':AgentSpec,'create_task':TaskInput,'create_document':DocumentInput}.get(row.kind)
        if not schema:raise HTTPException(422,'Unsupported proposal.')
        try: payload=schema.model_validate(payload).model_dump(mode='json')
        except ValidationError:raise HTTPException(422,'The proposal fields are invalid. Check names, dates, allowed tools and document values.')
        conversation=await db.get(AgentConversation,row.conversation_id)
        if conversation.agent_id:
            source=await owned_agent(db,profile,conversation.agent_id)
            required={'create_task':'propose_task','create_document':'propose_document'}.get(row.kind)
            if not source.enabled or not required or required not in source.tools:
                raise HTTPException(403,'This agent no longer has permission for the proposed action. Reject it or restore its permitted tool explicitly.')
        if row.kind=='create_agent':
            spec=AgentSpec.model_validate(payload)
            if spec.interval_hours and spec.schedule_prompt.strip()!='/run' and not spec.schedule_prompt.strip().startswith('/review '):
                raise HTTPException(422,'Scheduled prompts must be /run or /review advisor_name.')
            agent=BusinessAgent(business_profile_id=profile.id,**spec.model_dump(),next_run_at=datetime.utcnow()+timedelta(hours=spec.interval_hours) if spec.enabled and spec.interval_hours else None)
            db.add(agent);await db.flush();row.result={'agent_id':agent.id,'name':agent.name}
        elif row.kind=='create_task':
            from app.api.v1.endpoints.workspace import TaskInput
            task=TaskInput.model_validate(payload);values=task.model_dump();values['due_date']=str(task.due_date) if task.due_date else None
            created=OwnerTask(business_profile_id=profile.id,**values);db.add(created);await db.flush();row.result={'task_id':created.id}
        elif row.kind=='create_document':
            from app.api.v1.endpoints.billing import DocumentInput, create_document_record
            document=await create_document_record(db,profile,DocumentInput.model_validate(payload));row.result={'document_id':document.id,'number':document.number}
        else:raise HTTPException(422,'Unsupported proposal.')
        row.payload=payload;row.status='approved'
    await db.commit()
    return {'id':row.id,'status':row.status,'result':row.result}


async def check_agent_schedules(session_factory=async_session_maker,now=None):
    now=now or datetime.utcnow()
    async with session_factory() as db:
        ids=list(await db.scalars(select(BusinessAgent.id).where(BusinessAgent.enabled.is_(True),BusinessAgent.interval_hours>0,BusinessAgent.next_run_at<=now).limit(50)))
    for aid in ids:
        async with session_factory() as db:
            agent=await db.get(BusinessAgent,aid)
            if not agent:continue
            seconds=agent.interval_hours*3600;slot=f'{agent.interval_hours}:'+str(int(now.replace(tzinfo=timezone.utc).timestamp())//seconds)
            claim=await db.execute(update(BusinessAgent).where(BusinessAgent.id==aid,BusinessAgent.enabled.is_(True),BusinessAgent.next_run_at<=now).values(next_run_at=now+timedelta(hours=agent.interval_hours)))
            if not claim.rowcount:await db.rollback();continue
            if await db.scalar(select(AgentScheduleRun.id).where(AgentScheduleRun.agent_id==aid,AgentScheduleRun.slot==slot)):
                await db.commit();continue
            conversation=AgentConversation(business_profile_id=agent.business_profile_id,agent_id=aid,title='Scheduled: '+agent.name,builder_state={})
            db.add(conversation);await db.flush();db.add(AgentScheduleRun(agent_id=aid,slot=slot,conversation_id=conversation.id));await db.commit()
            profile=await db.get(BusinessProfile,agent.business_profile_id)
            await execute_turn(db,profile,conversation,agent.schedule_prompt or '/run','guided')
