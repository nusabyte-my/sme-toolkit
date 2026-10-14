"""Run: python scripts/check_enterprise.py. Temporary SQLite only; no workspace data."""
import asyncio
from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.auth import create_access_token
from app.database import Base, get_db, BookEntry, BookLine, Employee
from app.api.v1.endpoints import owner, bookkeeping, hr, workflows


async def check():
    with tempfile.TemporaryDirectory(prefix='sme-enterprise-') as folder:
        engine=create_async_engine('sqlite+aiosqlite:///'+(Path(folder)/'check.db').as_posix(),poolclass=NullPool)
        session=async_sessionmaker(engine,expire_on_commit=False)
        try:
            async with engine.begin() as connection: await connection.run_sync(Base.metadata.create_all)
            async def database():
                async with session() as db: yield db
            app=FastAPI()
            for router,prefix in [(owner.router,'owner'),(bookkeeping.router,'bookkeeping'),(hr.router,'hr'),(workflows.router,'workflows')]:
                app.include_router(router,prefix='/api/v1/'+prefix)
            app.dependency_overrides[get_db]=database
            headers=[{'Authorization':'Bearer '+create_access_token({'sub':actor})} for actor in ['enterprise-a','enterprise-b']]
            async with AsyncClient(transport=ASGITransport(app=app),base_url='http://check') as client:
                async def call(method,path,payload=None,actor=0,status=200):
                    response=await client.request(method,'/api/v1/'+path,json=payload,headers=headers[actor])
                    assert response.status_code==status,(path,response.status_code,response.text)
                    return response.json() if response.content else None
                for actor in range(2):
                    await call('PUT','owner/context',{'company_name':f'Business {actor}','currency':'MYR','timezone':'Asia/Kuala_Lumpur'},actor=actor)
                    await call('POST','bookkeeping/setup',actor=actor)
                books=await call('GET','bookkeeping/')
                accounts={a['code']:a['id'] for a in books['accounts']}
                other_accounts={a['code']:a['id'] for a in (await call('GET','bookkeeping/',actor=1))['accounts']}
                when=date.today()-timedelta(days=1)
                def journal(ref,debit,credit,amount='100.25',day=when):
                    return {'day':str(day),'reference':ref,'memo':'Verified input','lines':[{'account_id':debit,'debit':amount},{'account_id':credit,'credit':amount}]}
                await call('POST','bookkeeping/entries',journal('CAP',accounts['1000'],accounts['3000'],'1000.00'),status=201)
                income=await call('POST','bookkeeping/entries',journal('SALE',accounts['1000'],accounts['4000']),status=201)
                await call('POST','bookkeeping/entries',journal('COST',accounts['6000'],accounts['1000'],'40.10'),status=201)
                bad=journal('UNBALANCED',accounts['1000'],accounts['4000']);bad['lines'][1]['credit']='99.00'
                await call('POST','bookkeeping/entries',bad,status=422)
                await call('POST','bookkeeping/entries',journal('FOREIGN',other_accounts['1000'],accounts['4000']),status=404)
                await call('POST','bookkeeping/entries',journal('PRECISION',accounts['1000'],accounts['4000'],'1.001'),status=422)
                await call('POST','bookkeeping/entries',journal('SALE',accounts['1000'],accounts['4000']),status=409)
                report=await call('GET',f'bookkeeping/?start={when}&end={date.today()}')
                assert report['reports'][0]['income_cents']==10025
                assert report['reports'][0]['expense_cents']==4010
                assert report['reports'][0]['net_cents']==6015
                assert report['reports'][0]['debits_cents']==report['reports'][0]['credits_cents']
                assert not (await call('GET','bookkeeping/',actor=1))['entries']
                await call('POST',f"bookkeeping/entries/{income['id']}/reverse",{'day':str(when),'reference':'REV-FOREIGN','reason':'Cannot access another business'},actor=1,status=404)
                await call('POST',f"bookkeeping/entries/{income['id']}/reverse",{'day':str(when),'reference':'REV-SALE','reason':'Correct mistaken receipt'},status=201)
                await call('POST',f"bookkeeping/entries/{income['id']}/reverse",{'day':str(when),'reference':'REV-AGAIN','reason':'Duplicate reversal'},status=409)
                corrected=await call('GET',f'bookkeeping/?start={when}&end={date.today()}')
                assert corrected['reports'][0]['income_cents']==0 and corrected['reports'][0]['net_cents']==-4010
                reconciliation={'account_id':accounts['1000'],'day':str(when),'statement_balance':'959.90','reference':'BANK-1'}
                await call('POST','bookkeeping/reconciliations',{**reconciliation,'statement_balance':'1000.00'},status=409)
                await call('POST','bookkeeping/reconciliations',reconciliation,status=201)
                await call('POST','bookkeeping/entries',journal('LOCKED',accounts['1000'],accounts['4000']),status=409)
                await call('POST','bookkeeping/entries',journal('AFTER-LOCK',accounts['1000'],accounts['4000'],'10.00',date.today()),status=201)
                concurrent=journal('CONCURRENT',accounts['1010'],accounts['3000'],'12.00',date.today())
                responses=await asyncio.gather(*[client.post('/api/v1/bookkeeping/entries',json=concurrent,headers=headers[0]) for _ in range(2)])
                assert sorted(r.status_code for r in responses)==[201,409]
                exported=await client.get(f'/api/v1/bookkeeping/export?start={when}&end={date.today()}',headers=headers[0])
                assert exported.status_code==200 and 'REV-SALE' in exported.text and '959.90' not in exported.text
                await call('POST','bookkeeping/entries',journal('=FORMULA',accounts['1010'],accounts['3000'],'1.00',date.today()),status=201)
                exported=await client.get(f'/api/v1/bookkeeping/export?start={when}&end={date.today()}',headers=headers[0])
                assert "'=FORMULA" in exported.text
                async with session() as db:
                    sums=(await db.execute(select(BookLine.entry_id,func.sum(BookLine.debit_cents),func.sum(BookLine.credit_cents)).group_by(BookLine.entry_id))).all()
                    assert all(debits==credits for _,debits,credits in sums)
                    assert await db.scalar(select(BookEntry.id).where(BookEntry.reference=='UNBALANCED')) is None
                employee={'code':'EMP-1','name':'Aina','email':'aina@example.test','department':'Sales','job_title':'Lead','start_date':'2020-01-01','status':'active','annual_leave_days':5}
                person=await call('POST','hr/employees',employee,status=201)
                other=await call('POST','hr/employees',{**employee,'name':'Other owner'},actor=1,status=201)
                await call('POST','hr/employees',{**employee,'code':'EMP-FOREIGN','manager_id':other['id']},status=404)
                monday=date.today()+timedelta(days=(7-date.today().weekday())%7 or 7)
                if monday.year!=date.today().year: monday=date(date.today().year,1,1);monday+=timedelta(days=(7-monday.weekday())%7)
                request={'employee_id':person['id'],'start_date':str(monday),'end_date':str(monday+timedelta(days=1)),'kind':'annual','note':'Private note must not appear in automation task'}
                leave=await call('POST','hr/leave',request,status=201)
                await call('POST','hr/leave',request,status=409)
                await call('POST','hr/leave',{**request,'employee_id':other['id']},status=404)
                await call('POST','hr/leave',{**request,'start_date':str(monday+timedelta(days=7)),'end_date':str(monday+timedelta(days=11))},status=409)
                await call('POST','hr/leave',{**request,'start_date':str(monday+timedelta(days=5)),'end_date':str(monday+timedelta(days=6))},status=422)
                await call('PATCH',f"hr/leave/{leave['id']}",{'status':'approved'},actor=1,status=404)
                latest=(await call('GET',f'hr/?year={monday.year}'))['employees'][0]
                assert latest['pending_days']==2 and latest['available_days']==3
                await call('PUT',f"hr/employees/{person['id']}",{**employee,'version':latest['version'],'start_date':str(monday+timedelta(days=1))},status=409)
                await call('PUT',f"hr/employees/{person['id']}",{**employee,'version':person['version'],'name':'Stale name'},status=409)
                await call('PATCH',f"hr/leave/{leave['id']}",{'status':'approved'})
                latest=(await call('GET',f'hr/?year={monday.year}'))['employees'][0]
                assert latest['used_days']==2 and latest['pending_days']==0 and latest['available_days']==3
                await call('PATCH',f"hr/leave/{leave['id']}",{'status':'cancelled'})
                latest=(await call('GET',f'hr/?year={monday.year}'))['employees'][0]
                assert latest['available_days']==5
                await call('PATCH',f"hr/leave/{leave['id']}",{'status':'approved'},status=409)
                subordinate=await call('POST','hr/employees',{**employee,'code':'EMP-2','name':'Daniel','manager_id':person['id']},status=201)
                await call('PUT',f"hr/employees/{person['id']}",{**employee,'version':latest['version'],'manager_id':subordinate['id']},status=422)
                await call('PUT',f"hr/employees/{person['id']}",{**employee,'version':latest['version'],'status':'inactive'},status=409)
                hr_task=await call('POST','hr/tasks',{'employee_id':subordinate['id'],'title':'Onboarding access','due_date':str(when)},status=201)
                await call('PATCH',f"hr/tasks/{hr_task['id']}",{'completed':True},actor=1,status=404)
                await call('PATCH',f"hr/tasks/{hr_task['id']}",{'completed':True})
                await call('PATCH',f"hr/tasks/{hr_task['id']}",{'completed':False})
                newleave=await call('POST','hr/leave',request,status=201)
                preview=await call('GET','workflows/preview/people_review')
                assert len(preview['proposed_actions'])==2
                assert request['note'] not in str(preview)
                rule=await call('POST','workflows/rules',{'template_key':'people_review','enabled':True,'interval_hours':24},status=201)
                result=await call('POST',f"workflows/rules/{rule['id']}/check")
                assert len(result['run']['task_ids'])==2
                assert (await call('POST',f"workflows/rules/{rule['id']}/check"))['status']=='already_checked'
                assert (await call('GET','workflows/preview/bookkeeping_review'))['evidence']['issue_count']==2
                assert not (await call('GET','hr/',actor=1))['leave']
                assert (await call('GET','owner/overview'))['operations']['pending_leave']==1
                # Two overlapping requests reserve the allowance once, even from separate sessions.
                race_request={**request,'employee_id':subordinate['id']}
                responses=await asyncio.gather(*[client.post('/api/v1/hr/leave',json=race_request,headers=headers[0]) for _ in range(2)])
                assert sorted(r.status_code for r in responses)==[201,409]
            print('PASS: balanced cents, immutable reversal, period locks, duplicate/concurrent posts, CSV safety; HR isolation, leave reservation/decisions/concurrency, manager cycles, task recovery, private automation handoff')
        finally:
            await engine.dispose()


if __name__=='__main__':
    asyncio.run(check())
