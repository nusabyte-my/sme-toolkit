"""Run: python scripts/check_pilot_requests.py. Temporary SQLite; no external messages."""
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys
import tempfile
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.auth import create_access_token
from app.config import settings
from app.database import Base, PilotRequest, PilotIntakeLimit, get_db
from app.api.v1.endpoints.pilot_requests import router


async def check():
    with tempfile.TemporaryDirectory(prefix='sme-pilot-') as folder:
        engine = create_async_engine('sqlite+aiosqlite:///' + (Path(folder) / 'pilot.db').as_posix(), poolclass=NullPool)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async def database():
            async with sessions() as db:
                yield db
        app = FastAPI()
        app.include_router(router, prefix='/api/v1/pilot-requests')
        app.dependency_overrides[get_db] = database
        headers = {actor: {'Authorization': 'Bearer ' + create_access_token({'sub': actor})} for actor in ('admin', 'n8n', 'demo-pilot')}
        original_debug = settings.debug
        settings.debug = False
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url='http://check') as client:
                path = '/api/v1/pilot-requests'
                data = {'submission_id': str(uuid4()), 'name': 'Pilot Reviewer', 'company': 'Test Business', 'email': 'Pilot@Example.test', 'workflow': 'billing', 'goal': 'Reduce manual quotation re-entry for our team.', 'consent': True, 'website_url': ''}
                for patch in ({'consent': False}, {'consent': 'true'}, {'email': 'bad\nemail'}, {'workflow': 'shell'}, {'goal': 'short'}, {'company': ' '}, {'extra': 'ignored?'}):
                    denied = await client.post(path, json={**data, **patch})
                    assert denied.status_code == 422, denied.text
                    assert all('input' not in error for error in denied.json()['detail']) and 'Pilot@Example.test' not in denied.text
                assert (await client.post(path, json={**data, 'website_url': 'https://spam.test'})).status_code == 400
                assert (await client.post(path, content='x' * 12001, headers={'Content-Type': 'application/json'})).status_code == 413
                assert (await client.post(path, content='{}')).status_code == 415
                created = await client.post(path, json=data)
                assert created.status_code == 201, created.text
                assert created.json() == {'reference': data['submission_id'], 'status': 'received'}
                retry = await client.post(path, json=data)
                assert retry.status_code == 200 and retry.json() == created.json()
                assert (await client.post(path, json={**data, 'goal': 'Changed request using same reference.'})).status_code == 409
                assert (await client.get(path)).status_code in (401, 403)
                for actor in ('n8n', 'demo-pilot'):
                    assert (await client.get(path, headers=headers[actor])).status_code == 403
                    assert (await client.patch(path + '/' + data['submission_id'], json={'status': 'closed'}, headers=headers[actor])).status_code == 403
                    assert (await client.delete(path + '/' + data['submission_id'], headers=headers[actor])).status_code == 403
                inbox = await client.get(path, headers=headers['admin'])
                row = inbox.json()['items'][0]
                assert row['email'] == 'pilot@example.test' and row['goal'] == data['goal'] and row['status'] == 'new'
                assert inbox.headers['cache-control'] == 'no-store' and row['contact_consent_at']
                changed = await client.patch(path + '/' + row['id'], json={'status': 'contacted'}, headers=headers['admin'])
                assert changed.json()['status'] == 'contacted'
                assert (await client.get(path, headers=headers['admin'])).json()['items'] == []
                assert (await client.get(path + '?state=contacted', headers=headers['admin'])).json()['items'][0]['id'] == row['id']
                # Two distinct requests race for the final email/day slot; no overshoot.
                assert (await client.post(path, json={**data, 'submission_id': str(uuid4())})).status_code == 201
                competitors = [{**data, 'submission_id': str(uuid4())} for _ in range(2)]
                raced = await asyncio.gather(*(client.post(path, json=payload) for payload in competitors))
                assert sorted(result.status_code for result in raced) == [201, 429], [result.text for result in raced]
                rejected = next(result for result in raced if result.status_code == 429)
                assert int(rejected.headers['retry-after']) > 0
                async with sessions() as db:
                    assert await db.scalar(select(func.count()).select_from(PilotRequest)) == 3
                    quota_keys = list(await db.scalars(select(PilotIntakeLimit.key)))
                    assert all('example.test' not in key and '127.0.0.1' not in key for key in quota_keys)
                    for quota in await db.scalars(select(PilotIntakeLimit)):
                        quota.expires_at = datetime.utcnow() - timedelta(seconds=1)
                    await db.commit()
                assert (await client.post(path, json={**data, 'submission_id': str(uuid4())})).status_code == 201
                page = await client.get(path + '?state=all&limit=2', headers=headers['admin'])
                assert page.json()['has_more'] and len(page.json()['items']) == 2
                next_page = await client.get(path + '?state=all&limit=2&offset=2', headers=headers['admin'])
                assert not next_page.json()['has_more']
                assert {r['id'] for r in page.json()['items']}.isdisjoint(r['id'] for r in next_page.json()['items'])
                assert (await client.delete(path + '/' + row['id'], headers=headers['admin'])).status_code == 204
                async with sessions() as db:
                    assert await db.get(PilotRequest, row['id']) is None
            print('PASS: production-mode pilot persistence, validation/consent/body bounds, same-request retry, admin-only list/update/delete, race-safe rate cap, expiry recovery and pagination. No email or booking provider invoked.')
        finally:
            settings.debug = original_debug
            await engine.dispose()


if __name__ == '__main__':
    asyncio.run(check())
