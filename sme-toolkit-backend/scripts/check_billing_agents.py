"""Run: python scripts/check_billing_agents.py. Isolated SQLite, no paid model or real messages."""
import asyncio
import hashlib
import hmac
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cryptography.fernet import Fernet
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.auth import create_access_token
from app.config import settings
from app.database import (Base,get_db,BusinessProfile,BookEntry,BookLine,CommercialDocument,InvoicePayment,OwnerTask,
                          BusinessAgent,AgentConversation,AgentMessage,AgentProposal,AgentChannel,ChannelMessage,ChannelOutbox,AgentScheduleRun)
from app.api.v1.endpoints import owner,bookkeeping,billing,agent_chat,channels
from app.services import agent_runtime,channels as channel_service


async def check():
    with tempfile.TemporaryDirectory(prefix='sme-billing-agents-') as folder:
        engine=create_async_engine('sqlite+aiosqlite:///'+(Path(folder)/'check.db').as_posix(),poolclass=NullPool)
        session=async_sessionmaker(engine,expire_on_commit=False)
        original_key=settings.channel_encryption_key;original_url=settings.public_webhook_base_url
        settings.channel_encryption_key=Fernet.generate_key().decode();settings.public_webhook_base_url='https://callbacks.example.test'
        try:
            async with engine.begin() as connection:await connection.run_sync(Base.metadata.create_all)
            async def database():
                async with session() as db:yield db
            app=FastAPI()
            for router,prefix in [(owner.router,'owner'),(bookkeeping.router,'bookkeeping'),(billing.router,'billing'),(agent_chat.router,'agent-chat'),(channels.router,'channels')]:app.include_router(router,prefix='/api/v1/'+prefix)
            app.include_router(channels.webhook_router,prefix='/channels/webhook')
            app.dependency_overrides[get_db]=database
            headers=[{'Authorization':'Bearer '+create_access_token({'sub':a})} for a in ('billing-agent-a','billing-agent-b','demo-billing-agent')]
            async with AsyncClient(transport=ASGITransport(app=app),base_url='http://check') as client:
                async def call(method,path,payload=None,actor=0,status=200):
                    response=await client.request(method,path,json=payload,headers=headers[actor])
                    assert response.status_code==status,(path,response.status_code,response.text)
                    return response.json() if response.content else None
                for actor in range(3):await call('PUT','/api/v1/owner/context',{'company_name':f'Business {actor}','currency':'MYR','timezone':'Asia/Kuala_Lumpur'},actor=actor)
                customer=await call('POST','/api/v1/billing/customers',{'name':'Customer <script>bad()</script>','email':'customer@example.test'},status=201)
                other=await call('POST','/api/v1/billing/customers',{'name':'Other customer'},actor=1,status=201)
                today=date.today();until=today+timedelta(days=30)
                draft={'kind':'quotation','customer_id':customer['id'],'day':str(today),'due_date':str(until),
                       'lines':[{'description':'Consulting <img src=x>','quantity':'1.5','unit_price':'19.99','discount':'1.00','tax_percent':'6'}],'notes':'Owner supplied prices','terms':'Payment on receipt'}
                quote=await call('POST','/api/v1/billing/documents',draft,status=201)
                assert (quote['subtotal_cents'],quote['discount_cents'],quote['tax_cents'],quote['total_cents'])==(2999,100,174,3073)
                await call('POST','/api/v1/billing/documents',{**draft,'customer_id':other['id']},status=404)
                await call('POST','/api/v1/billing/documents',{**draft,'lines':[{'description':'Bad','quantity':'1','unit_price':'1','discount':'2'}]},status=422)
                await call('PUT',f"/api/v1/billing/documents/{quote['id']}",{**draft,'version':0},status=422)
                await call('POST',f"/api/v1/billing/documents/{quote['id']}/action",{'action':'issue'},actor=1,status=404)
                quote=await call('POST',f"/api/v1/billing/documents/{quote['id']}/action",{'action':'issue'})
                await call('PUT',f"/api/v1/billing/documents/{quote['id']}",{**draft,'version':quote['version']},status=409)
                await call('POST',f"/api/v1/billing/documents/{quote['id']}/action",{'action':'accept'},status=422)
                await call('POST',f"/api/v1/billing/documents/{quote['id']}/action",{'action':'accept','note':'Customer email reference A-1'})
                responses=await asyncio.gather(*[client.post(f"/api/v1/billing/documents/{quote['id']}/action",json={'action':'convert'},headers=headers[0]) for _ in range(2)])
                assert all(r.status_code==200 for r in responses)
                invoice=responses[0].json();assert invoice['id']==responses[1].json()['id'] and invoice['total_cents']==3073
                invoice=await call('POST',f"/api/v1/billing/documents/{invoice['id']}/action",{'action':'issue'})
                await call('POST',f"/api/v1/bookkeeping/entries/{invoice['journal_id']}/reverse",{'day':str(today),'reference':'WRONG-REV','reason':'Must go through invoice'},status=409)
                books=await call('GET','/api/v1/bookkeeping/');cash=next(a['id'] for a in books['accounts'] if a['code']=='1000')
                payment={'day':str(today),'reference':'P'*100,'amount':'10.00','account_id':cash}
                first=await call('POST',f"/api/v1/billing/documents/{invoice['id']}/payments",payment,status=201)
                await call('POST',f"/api/v1/billing/documents/{invoice['id']}/payments",payment,status=409)
                await call('POST',f"/api/v1/billing/documents/{invoice['id']}/payments",{**payment,'reference':'TOO-MUCH','amount':'50.00'},status=409)
                await call('POST',f"/api/v1/billing/documents/{invoice['id']}/payments",{**payment,'reference':'PAY-TWO','amount':'20.73'},status=201)
                current=(await call('GET','/api/v1/billing/'))['documents'];inv=next(d for d in current if d['id']==invoice['id'])
                assert inv['status']=='paid' and inv['balance_cents']==0 and inv['paid_cents']==3073
                await call('POST',f"/api/v1/billing/payments/{first['id']}/reverse",{'day':str(today),'reason':'Payment entered in error'})
                current=(await call('GET','/api/v1/billing/'))['documents'];inv=next(d for d in current if d['id']==invoice['id'])
                assert inv['status']=='issued' and inv['balance_cents']==1000
                recorded=next(p for p in (await call('GET','/api/v1/billing/'))['payments'] if p['id']==first['id'])
                assert recorded['reference']==payment['reference']
                await call('POST',f"/api/v1/billing/documents/{invoice['id']}/action",{'action':'void','note':'Still partially paid'},status=409)
                printed=await client.get(f"/api/v1/billing/documents/{invoice['id']}/print",headers=headers[0])
                assert printed.status_code==200 and '&lt;script&gt;' in printed.text and '<script>bad' not in printed.text and 'MYR 30.73' in printed.text
                await call('GET',f"/api/v1/billing/documents/{invoice['id']}/print",actor=1,status=404)
                assert not (await call('GET','/api/v1/billing/',actor=1))['documents']
                voidable=await call('POST','/api/v1/billing/documents',{**draft,'kind':'invoice'},status=201)
                voidable=await call('POST',f"/api/v1/billing/documents/{voidable['id']}/action",{'action':'issue'})
                voided=await call('POST',f"/api/v1/billing/documents/{voidable['id']}/action",{'action':'void','note':'V'*1000})
                assert voided['status']=='void' and voided['decision_note']=='V'*1000
                async with session() as db:
                    balances=(await db.execute(select(BookLine.entry_id,func.sum(BookLine.debit_cents),func.sum(BookLine.credit_cents)).group_by(BookLine.entry_id))).all()
                    assert all(a==b for _,a,b in balances)
                conversation=await call('POST','/api/v1/agent-chat/conversations',{'title':'Build sales agent'},status=201)
                cid=conversation['id']
                async def chat(text,mode='guided',conv=cid,actor=0):return await call('POST',f'/api/v1/agent-chat/conversations/{conv}/messages',{'content':text,'mode':mode},actor=actor)
                await chat('/create');await chat('Sales helper');await chat('Review invoices and propose owner follow-ups')
                result=await chat('billing_summary, propose_task')
                assert result['builder_stage'] is None and len(result['proposals'])==1
                assert not (await call('GET','/api/v1/agent-chat/'))['agents']
                proposal=result['proposals'][0]
                await call('POST',f"/api/v1/agent-chat/proposals/{proposal['id']}",{'action':'approve'},actor=1,status=404)
                approved=await call('POST',f"/api/v1/agent-chat/proposals/{proposal['id']}",{'action':'approve'})
                aid=approved['result']['agent_id']
                await call('POST',f"/api/v1/agent-chat/proposals/{proposal['id']}",{'action':'approve'},status=409)
                agent=(await call('GET','/api/v1/agent-chat/'))['agents'][0]
                agent_conv=await call('POST','/api/v1/agent-chat/conversations',{'title':'Sales helper work','agent_id':aid},status=201)
                result=await chat('/run',conv=agent_conv['id']);assert result['messages'][-1]['trace'][0]['tool']=='billing_summary'
                result=await chat('/create another agent',conv=agent_conv['id']);assert result['messages'][-1]['trace'][0]['status']=='failed'
                result=await chat('/review people_review',conv=agent_conv['id']);assert result['messages'][-1]['trace'][0]['status']=='failed'
                result=await chat('/task Follow up invoice INV',conv=agent_conv['id']);task_proposal=result['proposals'][0]
                async with session() as db:assert not await db.scalar(select(OwnerTask.id).where(OwnerTask.title=='Follow up invoice INV'))
                await call('POST',f"/api/v1/agent-chat/proposals/{task_proposal['id']}",{'action':'approve'})
                async with session() as db:assert await db.scalar(select(OwnerTask.id).where(OwnerTask.title=='Follow up invoice INV'))
                await call('GET',f'/api/v1/agent-chat/conversations/{cid}',actor=1,status=404)
                # Scripted model steps prove permission enforcement and real tool data, not remote model quality.
                async def disallowed(*args,**kwargs):return {'tool':'shell','arguments':{'command':'anything'}},'test-provider'
                with patch.object(agent_runtime,'model_reply',disallowed):
                    result=await chat('Execute a shell command','ai',agent_conv['id']);assert result['messages'][-1]['trace'][0]['status']=='failed'
                turn=0
                async def reasoning(*args,**kwargs):
                    nonlocal turn
                    turn+=1
                    if turn==1:return {'tool':'billing_summary','arguments':{}},'test-provider'
                    evidence=json.loads(args[2]['messages'][-1]['content'])
                    assert any(d['number']==invoice['number'] for d in evidence['documents'])
                    return {'reply':'The issued invoice has a remaining balance of MYR 10.00.'},'test-provider'
                with patch.object(agent_runtime,'model_reply',reasoning):
                    result=await chat('Review invoices','ai',agent_conv['id']);assert result['messages'][-1]['trace'][0]['tool']=='billing_summary' and '10.00' in result['messages'][-1]['content']
                spec={k:v for k,v in agent.items() if k not in ('id','next_run_at')};spec.update(interval_hours=1,schedule_prompt='/run')
                await call('PUT',f'/api/v1/agent-chat/agents/{aid}',spec)
                async with session() as db:
                    saved=await db.get(BusinessAgent,aid);saved.next_run_at=datetime.utcnow()-timedelta(seconds=1);await db.commit()
                await agent_chat.check_agent_schedules(session_factory=session)
                await agent_chat.check_agent_schedules(session_factory=session)
                async with session() as db:assert await db.scalar(select(func.count()).select_from(AgentScheduleRun))==1
                await call('POST','/api/v1/channels/',{'platform':'telegram','agent_id':aid,'token':'123456:abcdefghijklmnopqrstuv'},actor=2,status=403)
                sent_calls=[]
                async def provider(method,url,headers=None,payload=None,delivery=False):
                    if url.endswith('/getMe'):return {'ok':True,'result':{'id':123456,'is_bot':True,'username':'verified_test_bot'}}
                    if 'fields=id' in url:return {'id':'987654321','verified_name':'Verified Test WA'}
                    if url.endswith('/setWebhook'):
                        assert payload['secret_token'] and payload['url'].startswith('https://callbacks.example.test/channels/webhook/')
                        return {'ok':True,'result':True}
                    if delivery:
                        sent_calls.append(payload)
                        return {'ok':True,'result':{'message_id':len(sent_calls)}} if '/bot' in url else {'messages':[{'id':'wamid-'+str(len(sent_calls))}]}
                    raise AssertionError(url)
                with patch.object(channel_service,'request_provider',provider):
                    telegram=await call('POST','/api/v1/channels/',{'platform':'telegram','agent_id':aid,'token':'123456:abcdefghijklmnopqrstuv'},status=201)
                    assert 'token' not in telegram and 'credentials' not in telegram
                    await call('POST',f"/api/v1/channels/{telegram['id']}/register-webhook")
                    await call('PUT',f"/api/v1/channels/{telegram['id']}",{'agent_id':aid,'automation':'draft','response_mode':'fixed','fixed_reply':'Thank you. The owner will review your enquiry.','daily_limit':10})
                    async with session() as db:
                        stored=await db.get(AgentChannel,telegram['id']);secret=stored.webhook_secret
                        assert 'abcdefghijklmnopqrstuv' not in stored.credentials
                    event={'update_id':1,'message':{'date':int(datetime.now(timezone.utc).timestamp()),'from':{'id':42,'is_bot':False},'chat':{'id':42,'type':'private'},'text':'Hello'}}
                    denied=await client.post('/channels/webhook/'+telegram['id'],json=event);assert denied.status_code==403
                    wh={'X-Telegram-Bot-Api-Secret-Token':secret}
                    response=await client.post('/channels/webhook/'+telegram['id'],json=event,headers=wh);assert response.json()['received']==1
                    response=await client.post('/channels/webhook/'+telegram['id'],json=event,headers=wh);assert response.json()['received']==0
                    await channel_service.process_channel_queue(session_factory=session)
                    listing=await call('GET','/api/v1/channels/');out=listing['outbox'][0]
                    assert out['status']=='pending' and sent_calls==[]
                    await call('POST',f"/api/v1/channels/outbox/{out['id']}/review",{'action':'send'},actor=1,status=404)
                    delivered=await call('POST',f"/api/v1/channels/outbox/{out['id']}/review",{'action':'send'})
                    assert delivered['status']=='sent' and len(sent_calls)==1
                    await call('POST',f"/api/v1/channels/outbox/{out['id']}/review",{'action':'send'},status=409)
                    assert len(sent_calls)==1
                    wa_secret='meta-application-secret-for-test'
                    whatsapp=await call('POST','/api/v1/channels/',{'platform':'whatsapp','agent_id':aid,'token':'valid-test-meta-access-token','phone_number_id':'987654321','app_secret':wa_secret},status=201)
                    challenge=await client.get('/channels/webhook/'+whatsapp['id'],params={'hub.mode':'subscribe','hub.verify_token':whatsapp['verify_token'],'hub.challenge':'12345'})
                    assert challenge.status_code==200 and challenge.text=='12345'
                    body={'entry':[{'changes':[{'value':{'metadata':{'phone_number_id':'987654321'},'messages':[{'id':'wamid-in-1','from':'60123456789','timestamp':str(int(datetime.now(timezone.utc).timestamp())),'type':'text','text':{'body':'Hello WhatsApp'}}]}}]}]}
                    raw=json.dumps(body).encode();signature='sha256='+hmac.new(wa_secret.encode(),raw,hashlib.sha256).hexdigest()
                    assert (await client.post('/channels/webhook/'+whatsapp['id'],content=raw,headers={'Content-Type':'application/json','X-Hub-Signature-256':signature})).status_code==200
                    assert (await client.post('/channels/webhook/'+whatsapp['id'],content=raw,headers={'X-Hub-Signature-256':'bad'})).status_code==403
                    draft=await call('POST',f"/api/v1/channels/{whatsapp['id']}/outbox",{'peer':'60123456789','content':'Reviewed response','consent':True},status=201)
                    result=await call('POST',f"/api/v1/channels/outbox/{draft['id']}/review",{'action':'send'});assert result['status']=='sent'
                    async with session() as db:
                        incoming=await db.scalar(select(ChannelMessage).where(ChannelMessage.channel_id==whatsapp['id']));incoming.received_at=datetime.utcnow()-timedelta(hours=25);await db.commit()
                    closed=await call('POST',f"/api/v1/channels/{whatsapp['id']}/outbox",{'peer':'60123456789','content':'Outside window','consent':True},status=201)
                    await call('POST',f"/api/v1/channels/outbox/{closed['id']}/review",{'action':'send'},status=409)
                    template=await call('POST',f"/api/v1/channels/{whatsapp['id']}/outbox",{'peer':'60123456789','template_name':'order_update','template_parameters':['INV-1'],'consent':True},status=201)
                    assert (await call('POST',f"/api/v1/channels/outbox/{template['id']}/review",{'action':'send'}))['status']=='sent'
                    assert sent_calls[-1]['template']['name']=='order_update'
                    await call('PUT',f"/api/v1/channels/{telegram['id']}",{'agent_id':aid,'automation':'auto_reply','response_mode':'fixed','fixed_reply':'Automatic owner-written reply','daily_limit':10})
                    event['update_id']=2
                    await client.post('/channels/webhook/'+telegram['id'],json=event,headers=wh)
                    await channel_service.process_channel_queue(session_factory=session)
                    assert sent_calls[-1]['text']=='Automatic owner-written reply'
                    await call('PUT',f"/api/v1/channels/{telegram['id']}",{'agent_id':aid,'paused':True})
                    registered=await call('POST',f"/api/v1/channels/{telegram['id']}/register-webhook")
                    assert registered['status']=='paused', 'Webhook registration must not silently resume paused sends'
                    paused_draft=await call('POST',f"/api/v1/channels/{telegram['id']}/outbox",{'peer':'42','content':'Paused reply','consent':True},status=201)
                    await call('POST',f"/api/v1/channels/outbox/{paused_draft['id']}/review",{'action':'send'},status=409)
                    await call('PUT',f"/api/v1/channels/{telegram['id']}",{'agent_id':aid,'daily_limit':1})
                    await call('POST',f"/api/v1/channels/outbox/{paused_draft['id']}/review",{'action':'send'},status=429)
                    await call('PUT',f"/api/v1/channels/{telegram['id']}",{'agent_id':aid,'daily_limit':10})
                async def uncertain(*args,**kwargs):raise channel_service.DeliveryUncertain('No provider confirmation')
                draft=await call('POST',f"/api/v1/channels/{telegram['id']}/outbox",{'peer':'42','content':'Uncertain send','consent':True},status=201)
                with patch.object(channel_service,'request_provider',uncertain):
                    result=await call('POST',f"/api/v1/channels/outbox/{draft['id']}/review",{'action':'send'});assert result['status']=='unknown'
                await call('POST',f"/api/v1/channels/outbox/{draft['id']}/review",{'action':'send'},status=409)
                assert not (await call('GET','/api/v1/channels/',actor=1))['channels']
                async def rejected(*args,**kwargs):raise HTTPException(502,'Provider rejected verification')
                with patch.object(channel_service,'request_provider',rejected):
                    await call('POST','/api/v1/channels/',{'platform':'telegram','agent_id':aid,'token':'999999:abcdefghijklmnopqrstuv'},status=502)
                assert len((await call('GET','/api/v1/channels/'))['channels'])==2
            print('PASS: quote totals/lifecycle/conversion concurrency, invoice payments and ledger invariants, escaped print; guided agent creation/approval/permissions/scheduling; signed webhook dedup, encrypted channels, approval send, auto-reply, WhatsApp window/templates and unknown-delivery protection. Provider responses are contract fixtures, not live delivery proof.')
        finally:
            settings.channel_encryption_key=original_key;settings.public_webhook_base_url=original_url
            await engine.dispose()


if __name__=='__main__':asyncio.run(check())
