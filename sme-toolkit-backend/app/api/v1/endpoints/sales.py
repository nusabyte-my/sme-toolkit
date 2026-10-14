from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_, delete
from sqlalchemy.exc import IntegrityError
from app.auth import get_current_user
from app.database import get_db, SalesTransaction, MarketplaceCredential
from app.schemas.sales import SalesTransactionCreate, SalesTransactionUpdate
from app.services.owner_service import business, context_data, period_start, sales_summary, iso
import csv
import io
from pydantic import BaseModel, Field, ConfigDict

router = APIRouter()

class SalesImport(BaseModel):
    model_config = ConfigDict(extra='forbid')
    csv_text: str = Field(min_length=1,max_length=1_000_000)


@router.post('/import')
async def import_sales(data: SalesImport, actor=Depends(get_current_user), db=Depends(get_db)):
    profile=await business(db,actor)
    rows=[];seen=set()
    try:
        for number,row in enumerate(csv.DictReader(io.StringIO(data.csv_text.lstrip('\ufeff'))),2):
            if number>1001: raise ValueError('Maximum 1,000 rows per import')
            item=SalesTransactionCreate.model_validate(row)
            if not item.external_id: raise ValueError(f'Line {number}: external_id is required for idempotent import')
            key=(item.platform,item.external_id)
            if key in seen: raise ValueError(f'Line {number}: duplicate channel/order reference')
            seen.add(key);rows.append(item)
        if not rows: raise ValueError('CSV contains no sales')
    except ValueError as exc: raise HTTPException(422,str(exc)[:1500])
    inserted=0;skipped=0
    for item in rows:
        existing=await db.scalar(select(SalesTransaction).where(SalesTransaction.business_profile_id==profile.id,SalesTransaction.platform==item.platform,SalesTransaction.external_id==item.external_id))
        if existing:
            if float(item.amount)!=existing.amount or item.currency!=existing.currency or item.status!=existing.status or item.transaction_date!=existing.transaction_date:
                await db.rollback();raise HTTPException(409,f'Order {item.external_id} already exists with different values. Update it explicitly; import is not an overwrite.')
            skipped+=1
        else: db.add(SalesTransaction(business_profile_id=profile.id,**item.model_dump()));inserted+=1
    try: await db.commit()
    except IntegrityError:
        await db.rollback();raise HTTPException(409,'Concurrent import detected. Retry; duplicate references cannot be inserted.')
    return dict(inserted=inserted,skipped=skipped)


def sale_data(row):
    return {key: getattr(row, key) for key in ('id', 'platform', 'external_id', 'amount', 'currency', 'status')} | {
        'transaction_date': iso(row.transaction_date), 'created_at': iso(row.created_at)}


@router.post('/', status_code=201)
async def create_transaction(data: SalesTransactionCreate, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    if data.external_id:
        duplicate = await db.scalar(select(SalesTransaction.id).where(SalesTransaction.business_profile_id == profile.id, SalesTransaction.platform == data.platform, SalesTransaction.external_id == data.external_id))
        if duplicate:
            raise HTTPException(409, 'This channel and order reference already exist. Update the recorded order instead.')
    row = SalesTransaction(business_profile_id=profile.id, **data.model_dump())
    db.add(row)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, 'This channel and order reference already exist.')
    await db.refresh(row)
    return sale_data(row)


@router.get('/')
async def list_transactions(page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=100),
                            days: int = Query(30, ge=1, le=365), platform: str | None = Query(None, max_length=60),
                            search: str = Query('', max_length=120), status: str | None = Query(None, max_length=20),
                            actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    start, _, end, _, _ = period_start(context_data(profile), days)
    filters = [SalesTransaction.business_profile_id == profile.id, SalesTransaction.transaction_date >= start, SalesTransaction.transaction_date <= end]
    if platform:
        filters.append(SalesTransaction.platform == platform)
    if status:
        filters.append(SalesTransaction.status == status)
    if search.strip():
        filters.append(or_(SalesTransaction.external_id.icontains(search.strip(), autoescape=True), SalesTransaction.platform.icontains(search.strip(), autoescape=True)))
    total = await db.scalar(select(func.count()).select_from(SalesTransaction).where(*filters))
    rows = await db.scalars(select(SalesTransaction).where(*filters).order_by(SalesTransaction.transaction_date.desc(), SalesTransaction.id).offset((page - 1) * size).limit(size))
    return dict(items=[sale_data(r) for r in rows], total=total, page=page, size=size)


@router.get('/summary')
async def summary(days: int = Query(30, ge=1, le=365), actor=Depends(get_current_user), db=Depends(get_db)):
    return await sales_summary(db, await business(db, actor, False), days)


@router.get('/connections')
async def connections(actor=Depends(get_current_user)):
    # ponytail: no verified connector exists yet; enable only after OAuth + signed webhooks are implemented.
    return []


@router.get('/track')
@router.get('/auth/{platform}/url')
@router.get('/auth/{platform}/callback')
async def unavailable_integration(actor=Depends(get_current_user)):
    raise HTTPException(503, 'Live marketplace sync is not configured. Record verified orders manually; no external orders were created or fetched.')


@router.delete('/connections/{platform}', status_code=204)
async def disconnect(platform: str, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    await db.execute(delete(MarketplaceCredential).where(MarketplaceCredential.business_profile_id == profile.id, MarketplaceCredential.platform == platform))
    await db.commit()


@router.patch('/{transaction_id}')
async def update_transaction(transaction_id: str, data: SalesTransactionUpdate, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await db.scalar(select(SalesTransaction).where(SalesTransaction.id == transaction_id, SalesTransaction.business_profile_id == profile.id))
    if not row:
        raise HTTPException(404, 'Sale not found')
    row.status = data.status
    await db.commit()
    await db.refresh(row)
    return sale_data(row)
