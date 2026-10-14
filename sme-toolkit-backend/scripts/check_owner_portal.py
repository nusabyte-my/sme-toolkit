"""Run: python scripts/check_owner_portal.py. Uses only temporary SQLite, never the workspace DB."""
import asyncio
import base64
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi import FastAPI, Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.auth import create_access_token, get_current_user, get_admin_user
from app.database import Base, BusinessProfile, SalesTransaction, AdVideoJob, AutomationRule, AutomationRun, OwnerTask, Lead, get_db
from app.api.v1.endpoints import owner, sales, ads, workspace, ad_optimization, workflows
from app.services.owner_service import sales_summary, period_start, context_data
from app.agents.workflow_engine import run_rule, check_due_rules, schedule_slot
from app.services.advisors import advisor_catalog
from app.api.v1.auth_routes import auth_router
from app.config import settings


async def check():
    with tempfile.TemporaryDirectory(prefix='sme-owner-check-') as directory:
        engine = create_async_engine('sqlite+aiosqlite:///' + (Path(directory) / 'isolated.db').as_posix(), poolclass=NullPool)
        session = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async def database():
            async with session() as db:
                yield db
        app = FastAPI()
        app.include_router(owner.router, prefix='/owner')
        app.include_router(sales.router, prefix='/sales')
        app.include_router(ads.router, prefix='/ads')
        app.include_router(workspace.router,prefix='/workspace')
        app.include_router(ad_optimization.router,prefix='/optimization')
        app.include_router(workflows.router,prefix='/workflows')
        app.include_router(auth_router,prefix='/auth')
        for router,prefix in [(owner.router,'owner'),(sales.router,'sales'),(ads.router,'ads'),(workspace.router,'workspace'),(ad_optimization.router,'ad-optimization'),(workflows.router,'workflows')]:
            app.include_router(router,prefix='/api/v1/'+prefix)
        @app.post('/api/v1/copywriter/generate')
        async def restricted_legacy(actor=Depends(get_current_user)):
            raise AssertionError('Demo must not reach a legacy generator')
        @app.get('/admin-check')
        async def admin_check(actor=Depends(get_admin_user)):
            return {'actor':actor}
        app.dependency_overrides[get_db] = database
        headers = [{'Authorization':'Bearer ' + create_access_token({'sub':actor})} for actor in ('owner-check-a','owner-check-b')]
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://check') as client:
            async def call(method, path, payload=None, actor=0, expected=200):
                response = await client.request(method, path, json=payload, headers=headers[actor])
                assert response.status_code == expected, (path, response.status_code, response.text)
                return response.json() if response.content else None
            assert (await client.get('/owner/overview')).status_code in (401,403)
            assert await call('GET','/owner/context') is None
            context = dict(company_name='Owner check', industry='Services', products_services='Repairs', target_market='Local shops', goals='Reduce pending orders', timezone='Asia/Kuala_Lumpur', currency='MYR')
            a = await call('PUT','/owner/context',context)
            b = await call('PUT','/owner/context',{**context,'company_name':'Other owner'},actor=1)
            assert a['id'] != b['id']
            now = datetime.now(timezone.utc) - timedelta(minutes=1)
            sale = dict(platform='manual', amount=100.25, currency='MYR', status='completed', transaction_date=now.isoformat(), external_id='ORDER-1')
            saved = await call('POST','/sales/',sale,expected=201)
            await call('POST','/sales/',sale,expected=409)
            for status, amount, currency, ref in [('pending',80,'MYR','P'),('refunded',25,'MYR','R'),('completed',500,'USD','FX')]:
                await call('POST','/sales/',{**sale,'external_id':ref,'status':status,'amount':amount,'currency':currency},expected=201)
            await call('POST','/sales/',{**sale,'external_id':'BAD','amount':-1},expected=422)
            await call('POST','/sales/',{**sale,'external_id':'FUTURE','transaction_date':(now+timedelta(days=2)).isoformat()},expected=422)
            summary = await call('GET','/sales/summary')
            assert (summary['revenue'],summary['orders'],summary['pending_orders'],summary['refunded_orders'],summary['excluded_currency_orders']) == (100.25,4,1,1,1)
            assert summary['change_percent'] is None
            assert (await call('GET','/sales/?search=ORDER&size=1'))['total']==1
            assert (await call('GET','/sales/summary',actor=1))['revenue']==0
            await call('PATCH',f"/sales/{saved['id']}",{'status':'refunded'},actor=1,expected=404)
            await call('GET','/sales/track',expected=503)
            assert (await call('GET','/sales/summary'))['orders']==4
            run = await call('POST','/owner/runs',{'kind':'sales','objective':'Review my recorded sales'},expected=201)
            assert run['provider']=='rules' and '100.25' in run['output']
            await call('PATCH',f"/owner/runs/{run['id']}",{'status':'approved'},actor=1,expected=404)
            approved = await call('PATCH',f"/owner/runs/{run['id']}",{'status':'approved'})
            assert approved['output']==run['output']
            await call('PATCH',f"/owner/runs/{run['id']}",{'status':'dismissed'},expected=409)
            await call('PUT','/owner/context',{**context,'company_name':'Updated owner'})
            assert (await call('GET','/owner/runs'))[0]['context_snapshot']['company_name']=='Owner check'
            campaign = await call('POST','/owner/campaigns',{'title':'Repair offer','platform':'email','caption':'Book a repair consultation.'},expected=201)
            await call('PATCH',f"/owner/campaigns/{campaign['id']}",{'status':'approved'})
            edited = await call('PATCH',f"/owner/campaigns/{campaign['id']}",{'caption':'Arrange a repair consultation.'})
            assert edited['status']=='draft'
            await call('PATCH',f"/owner/campaigns/{campaign['id']}",{'status':'approved'},actor=1,expected=404)
            profile = await call('POST','/ads/profiles',{'name':'Repair ads','product':'Appliance repairs','audience':'Local shops'},expected=201)
            draft_data = dict(profile_id=profile['id'],title='Repair creative',headline='Repair instead of replace',body='Book a consultation',cta='Book a repair')
            draft = await call('POST','/ads/drafts',draft_data,expected=201)
            await call('PATCH',f"/ads/drafts/{draft['id']}",{'status':'approved'})
            edited = await call('PUT',f"/ads/drafts/{draft['id']}",{**draft_data,'headline':'Appliance repair advice'})
            assert edited['status']=='draft'
            await call('PUT',f"/ads/drafts/{draft['id']}",draft_data,actor=1,expected=404)
            pixel = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aZfoAAAAASUVORK5CYII=')
            asset = await call('POST','/ads/assets',{'name':'pixel.png','mime':'image/png','data':base64.b64encode(pixel).decode()},expected=201)
            response=await client.get(f"/ads/assets/{asset['id']}",headers=headers[0])
            assert response.content==pixel and response.headers['content-type']=='image/png'
            await call('GET',f"/ads/assets/{asset['id']}",actor=1,expected=404)
            await call('POST','/ads/assets',{'name':'bad.png','mime':'image/png','data':base64.b64encode(b'not an image').decode()},expected=415)
            await call('POST','/ads/drafts',{**draft_data,'profile_id':(await call('POST','/ads/profiles',{'name':'B','product':'B','audience':'B'},actor=1,expected=201))['id']},expected=404)
            library = await call('GET','/ads/')
            assert library['drafts'][0]['headline']=='Appliance repair advice'
            assert not (await call('GET','/ads/',actor=1))['drafts']
            await call('PUT',f"/ads/drafts/{draft['id']}",{**draft_data,'video_asset_id':asset['id']},expected=422)
            async with session() as db:
                db.add(AdVideoJob(id='00000000-0000-4000-8000-000000000001', business_profile_id=a['id'],
                                 prompt='Existing failed generation', status='failed', error='Provider rejected the request'))
                await db.commit()
            repeated = await call('POST','/ads/video',{'request_id':'00000000-0000-4000-8000-000000000001',
                                  'profile_id':profile['id'],'prompt':'Do not resubmit this job','aspect_ratio':'9:16','duration':4},expected=201)
            assert repeated['status']=='failed' and repeated['prompt']=='Existing failed generation'
            await call('POST','/ads/video/00000000-0000-4000-8000-000000000001/check',actor=1,expected=404)
            action=await call('POST','/workspace/tasks',{'title':'Review acquisition spend','owner':'Owner'},expected=201)
            await call('PUT',f"/workspace/tasks/{action['id']}",{'title':'Review acquisition spend','status':'done'},actor=1,expected=404)
            await call('PUT',f"/workspace/tasks/{action['id']}",{'title':'Review acquisition spend','status':'done'})
            assert (await call('GET','/workspace/tasks'))[0]['status']=='done'
            for kind,fields in [('canvas',{'value':'Repair advice'}),('strategy',{'goal':'Reduce pending orders'}),('ideation',{'idea':'Scheduled maintenance'}),('seo',{'page_title':'Repair services'}),('research',{'evidence':'Interviewed five retailers'})]:
                doc=await call('POST','/workspace/documents',{'kind':kind,'title':kind,'fields':fields},expected=201)
                assert (await call('GET',f'/workspace/documents?kind={kind}'))[0]['fields']==fields
                await call('PUT',f"/workspace/documents/{doc['id']}",{'kind':kind,'title':'Other','fields':fields},actor=1,expected=404)
            lead=await call('POST','/workspace/leads',{'name':'Actual prospect','email':'buyer@example.com','status':'qualified'},expected=201)
            assert (await call('GET','/workspace/leads?search=Actual'))['total']==1
            await call('PUT',f"/workspace/leads/{lead['id']}",{'name':'Changed','status':'won'},actor=1,expected=404)
            day=(datetime.now(timezone.utc)-timedelta(days=5)).date().isoformat()
            performance=dict(day=day,platform='Meta',campaign='Prospecting',creative='Hook A',currency='MYR',attribution='7-day click',impressions=2000,clicks=100,conversions=10,spend='100.00',revenue='500.00')
            await call('POST','/optimization/records',performance)
            await call('POST','/optimization/records',performance)
            await call('PUT','/optimization/targets',{'target_cpa':15,'target_roas':3,'min_impressions':1000,'min_conversions':10,'conversion_lag_days':3})
            report=await call('GET','/optimization/')
            assert len(report['items'])==1
            metric=report['items'][0]['current']
            assert (metric['spend'],metric['ctr'],metric['cpc'],metric['cpa'],metric['cvr'],metric['roas'])==(100,5,1,10,10,5)
            assert report['items'][0]['state']=='candidate'
            assert (await call('GET','/optimization/',actor=1))['items']==[]
            await call('POST','/optimization/records',{**performance,'clicks':2001},expected=422)
            creative=await call('PUT',f"/ads/drafts/{draft['id']}",{**draft_data,'layers':[{'id':'layer1','type':'text','text':'Supporting fact'}],'scenes':[{'id':'scene1','caption':'Hook','duration':2}],'image_style':{'brightness':120}})
            assert creative['image_style']['brightness']==120 and creative['scenes'][0]['duration']==2
            await call('PUT',f"/ads/drafts/{draft['id']}",{**draft_data,'scenes':[{'id':'same','duration':2},{'id':'same','duration':2}]},expected=422)
            await call('POST','/workspace/documents',{'kind':'research','title':'Unsafe source','fields':{'source_url':'javascript:alert(1)'}},expected=422)
            imported_csv='platform,external_id,amount,currency,status,transaction_date\nmanual,CSV-1,12.50,MYR,completed,'+now.isoformat()
            assert (await call('POST','/sales/import',{'csv_text':imported_csv}))['inserted']==1
            assert (await call('POST','/sales/import',{'csv_text':imported_csv}))['skipped']==1
            before_count=(await call('GET','/sales/summary'))['orders']
            conflict='platform,external_id,amount,currency,status,transaction_date\nmanual,ROLLBACK,1.00,MYR,completed,'+now.isoformat()+'\nmanual,CSV-1,99.00,MYR,completed,'+now.isoformat()
            await call('POST','/sales/import',{'csv_text':conflict},expected=409)
            assert (await call('GET','/sales/summary'))['orders']==before_count
            await call('POST','/optimization/records',{**performance,'attribution':'1-day click'})
            assert len((await call('GET','/optimization/'))['items'])==2
            empty=ad_optimization.metrics(dict(impressions=0,clicks=0,conversions=0,spend_cents=0,revenue_cents=0))
            assert empty['ctr'] is None and empty['cpa'] is None and empty['roas'] is None
            review=ad_optimization.metrics(dict(impressions=2000,clicks=40,conversions=0,spend_cents=6000,revenue_cents=0))
            assert ad_optimization.assess(review,empty,report['targets'])[0]=='review'
            catalog=await call('GET','/owner/advisors')
            overdue_time=(datetime.now(timezone.utc)-timedelta(days=2)).isoformat()
            await call('POST','/workspace/leads',{'name':'Needs follow-up','status':'qualified','next_follow_up_at':overdue_time},expected=201)
            await call('POST','/workspace/leads',{'name':'Closed prospect','status':'won','next_follow_up_at':overdue_time},expected=201)
            followup=await call('POST','/owner/runs',{'kind':'lead_followup','objective':'Find overdue follow-ups'},expected=201)
            assert followup['skill']['name']=='lead-followup-advisor' and followup['evidence']['overdue_count']==1
            assert 'Needs follow-up' in followup['output'] and 'Closed prospect' not in followup['output']
            for advisor in catalog:
                if advisor['mode']=='rules':
                    result=await call('POST','/owner/runs',{'kind':advisor['kind'],'objective':advisor['default_objective']},expected=201)
                    assert result['status']=='needs_review' and result['provider']=='rules'
            paused=await call('POST','/workflows/rules',{'template_key':'lead_followup','enabled':False,'interval_hours':1},expected=201)
            await call('POST','/workflows/rules',{'template_key':'lead_followup'},expected=409)
            before_tasks=len(await call('GET','/workspace/tasks'))
            preview=await call('GET','/workflows/preview/lead_followup')
            assert len(preview['proposed_actions'])==1 and len(await call('GET','/workspace/tasks'))==before_tasks
            await call('POST',f"/workflows/rules/{paused['id']}/check",expected=409)
            await call('PUT',f"/workflows/rules/{paused['id']}",{'template_key':'lead_followup','enabled':True,'interval_hours':1},actor=1,expected=404)
            await call('PUT',f"/workflows/rules/{paused['id']}",{'template_key':'lead_followup','enabled':True,'interval_hours':1})
            execution=await call('POST',f"/workflows/rules/{paused['id']}/check")
            assert execution['status']=='completed' and len(execution['run']['task_ids'])==1
            repeated=await call('POST',f"/workflows/rules/{paused['id']}/check")
            assert repeated['status']=='already_checked'
            assert len(await call('GET','/workspace/tasks'))==before_tasks+1
            assert not (await call('GET','/workflows/',actor=1))['logs']
            await call('POST',f"/workflows/rules/{paused['id']}/check",actor=1,expected=404)
            async with session() as db:
                result=await run_rule(db,paused['id'],a['id'],now=datetime.now(timezone.utc)+timedelta(hours=2))
                assert result['status']=='no_action' and result['run']['task_ids']==[]
            await call('PUT',f"/workflows/rules/{paused['id']}",{'template_key':'lead_followup','enabled':False,'interval_hours':1})
            async with session() as db:
                assert (await run_rule(db,paused['id'],a['id'],force=True))['status']=='paused'
            scheduled=await call('POST','/workflows/rules',{'template_key':'owner_brief','enabled':True,'interval_hours':24},expected=201)
            tick=await check_due_rules(session_factory=session)
            assert any(result['status']=='completed' for result in tick)
            logs=(await call('GET','/workflows/'))['logs']
            assert any(log['rule_id']==scheduled['id'] and log['advisor_run_id'] for log in logs)
            async def concurrent_check():
                async with session() as db:
                    return await run_rule(db,scheduled['id'],a['id'],force=True,now=datetime.now(timezone.utc)+timedelta(days=2))
            concurrent=await asyncio.gather(concurrent_check(),concurrent_check())
            assert sum(result['status']=='completed' for result in concurrent)==1
            assert schedule_slot(datetime(2026,10,6,23,59),24)[1]==datetime(2026,10,7)
            batch_now=datetime.now(timezone.utc).replace(tzinfo=None,minute=0,second=0,microsecond=0)
            async with session() as db:
                db.add_all([Lead(business_profile_id=b['id'],name=f'Batch prospect {index}',email='',status='qualified',next_follow_up_at=batch_now-timedelta(days=1)) for index in range(105)])
                batch_rule=AutomationRule(business_profile_id=b['id'],template_key='lead_followup',enabled=True,interval_hours=1,next_run_at=batch_now)
                db.add(batch_rule)
                await db.commit()
                batch_rule_id=batch_rule.id
            batch_preview=await call('GET','/workflows/preview/lead_followup',actor=1)
            assert batch_preview['evidence']['issue_count']==105 and len(batch_preview['proposed_actions'])==100
            async with session() as db:
                first_batch=await run_rule(db,batch_rule_id,b['id'],now=batch_now)
                assert len(first_batch['run']['task_ids'])==100
            async with session() as db:
                second_batch=await run_rule(db,batch_rule_id,b['id'],now=batch_now+timedelta(hours=1))
                assert len(second_batch['run']['task_ids'])==5
                assert set(first_batch['run']['task_ids']).isdisjoint(second_batch['run']['task_ids'])
                assert await db.scalar(select(func.count()).select_from(OwnerTask).where(OwnerTask.business_profile_id==b['id']))==105
            async with session() as db:
                third_batch=await run_rule(db,batch_rule_id,b['id'],now=batch_now+timedelta(hours=2))
                assert third_batch['status']=='no_action' and third_batch['run']['task_ids']==[]
                rule=await db.get(AutomationRule,batch_rule_id)
                rule.next_run_at=batch_now+timedelta(hours=2,minutes=5)
                await db.commit()
            async with session() as db:
                resumed=await run_rule(db,batch_rule_id,b['id'],now=batch_now+timedelta(hours=2,minutes=10))
                assert resumed['status']=='already_checked'
            async with session() as db:
                rule=await db.get(AutomationRule,batch_rule_id)
                assert rule.next_run_at==batch_now+timedelta(hours=3)
                assert await db.scalar(select(func.count()).select_from(AutomationRun).where(AutomationRun.rule_id==batch_rule_id))==3
            own_context=await call('GET','/owner/context')
            original_debug=settings.debug
            try:
                settings.debug=True
                for _ in range(2):
                    token=await call('POST','/auth/demo')
                    headers.append({'Authorization':'Bearer '+token['access_token']})
                settings.debug=False
                await call('POST','/auth/demo',expected=403)
            finally:
                settings.debug=original_debug
            demo=await call('GET','/api/v1/owner/overview',actor=2)
            other_demo=await call('GET','/api/v1/owner/overview',actor=3)
            assert demo['context']['is_demo'] and demo['context']['id']!=other_demo['context']['id']
            assert demo['sales']['pending_orders']==3 and not demo['capabilities']['ai_available']
            demo_sales=await call('GET','/api/v1/sales/?status=pending',actor=2)
            order=demo_sales['items'][0]
            await call('PATCH',f"/api/v1/sales/{order['id']}",{'status':'completed'},actor=3,expected=404)
            await call('PATCH',f"/api/v1/sales/{order['id']}",{'status':'completed'},actor=0,expected=404)
            await call('PATCH',f"/api/v1/sales/{order['id']}",{'status':'completed'},actor=2)
            changed=await call('GET','/api/v1/owner/overview',actor=2)
            assert changed['sales']['revenue']==demo['sales']['revenue']+order['amount']
            assert changed['sales']['pending_orders']==2
            assert (await call('GET','/api/v1/owner/overview',actor=3))['sales']==other_demo['sales']
            assert await call('GET','/owner/context')==own_context
            await call('POST','/api/v1/copywriter/generate',{},actor=2,expected=403)
            await call('GET','/admin-check',actor=2,expected=403)
            for path in ('copy','image','video'):
                await call('POST','/api/v1/ads/'+path,{},actor=2,expected=403)
            await call('POST','/api/v1/owner/runs',{'kind':'marketing','objective':'Publish a real campaign'},actor=2,expected=403)
            lead_run=await call('POST','/api/v1/owner/runs',{'kind':'lead_followup','objective':'Find overdue sample enquiries'},actor=2,expected=201)
            assert lead_run['evidence']['overdue_count']==2
            library=await call('GET','/api/v1/ads/',actor=2)
            assert not library['capabilities']['image_available'] and not library['capabilities']['video_available']
            for draft in library['drafts']:
                ads.DraftInput.model_validate({k:v for k,v in draft.items() if k not in ('id','created_at','updated_at','profile_snapshot','status')})
                await call('GET',f"/api/v1/ads/assets/{draft['asset_id']}",actor=3,expected=404)
            for kind in ('canvas','strategy','ideation','seo','research'):
                for document in await call('GET','/api/v1/workspace/documents?kind='+kind,actor=2):
                    workspace.DocumentInput.model_validate({k:document[k] for k in ('kind','title','fields')})
            demo_rules=(await call('GET','/api/v1/workflows/',actor=2))['rules']
            assert all(not rule['enabled'] for rule in demo_rules)
            rule=next(rule for rule in demo_rules if rule['template_key']=='lead_followup')
            await call('PUT',f"/api/v1/workflows/rules/{rule['id']}",{'template_key':'lead_followup','enabled':True,'interval_hours':6},actor=2)
            demo_check=await call('POST',f"/api/v1/workflows/rules/{rule['id']}/check",actor=2)
            assert len(demo_check['run']['task_ids'])==2
            assert (await call('POST',f"/api/v1/workflows/rules/{rule['id']}/check",actor=2))['status']=='already_checked'
            assert not (await call('GET','/api/v1/workflows/',actor=3))['logs']
        async with session() as db:
            profile=await db.scalar(select(BusinessProfile).where(BusinessProfile.id==b['id']))
            profile.meta_json={**profile.meta_json,'owner_context':{**context,'timezone':'America/New_York'}}
            fixed=datetime(2026,3,9,12,tzinfo=timezone.utc)
            start,previous,end,zone,first=period_start(context_data(profile),1,fixed)
            db.add_all([
                SalesTransaction(business_profile_id=profile.id,platform='manual',amount=10,currency='MYR',status='completed',transaction_date=start-timedelta(microseconds=1)),
                SalesTransaction(business_profile_id=profile.id,platform='manual',amount=30,currency='MYR',status='completed',transaction_date=start),
            ])
            await db.commit()
            result=await sales_summary(db,profile,1,fixed)
            assert result['revenue']==30 and result['previous_revenue']==10 and result['change_percent']==200
            assert result['daily']==[{'date':'2026-03-09','revenue':30.0}]
        await engine.dispose()
    print('PASS: owner contracts; automation backlog/resume; demo isolation; paid-action gates; sample record validation and connected revenue/task updates')

if __name__=='__main__':
    asyncio.run(check())
