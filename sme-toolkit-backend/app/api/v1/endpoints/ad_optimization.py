"""Daily ad-performance ledger. Decisions are review suggestions, not platform mutations."""
import csv
import io
from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.auth import get_current_user
from app.database import get_db, AdPerformance
from app.services.owner_service import business, context_data

router=APIRouter()

class PerformanceInput(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    day:date
    platform:Literal['Meta','Google','TikTok','LinkedIn','Other']
    campaign:str=Field(min_length=1,max_length=160)
    creative:str=Field(min_length=1,max_length=160)
    currency:str=Field(pattern=r'^[A-Z]{3}$')
    attribution:str=Field(min_length=1,max_length=100)
    impressions:int=Field(ge=0,le=2_000_000_000)
    clicks:int=Field(ge=0,le=2_000_000_000)
    conversions:int=Field(ge=0,le=2_000_000_000)
    spend:Decimal=Field(ge=0,le=999999999,max_digits=11,decimal_places=2,allow_inf_nan=False)
    revenue:Decimal=Field(ge=0,le=999999999,max_digits=11,decimal_places=2,allow_inf_nan=False)
    @model_validator(mode='after')
    def valid_metrics(self):
        if self.day>date.today():raise ValueError('Performance date cannot be in the future')
        if self.clicks>self.impressions:raise ValueError('Clicks cannot exceed impressions')
        return self

class ImportInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    csv_text:str=Field(min_length=1,max_length=1_000_000)

class TargetsInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    target_cpa:float|None=Field(default=None,gt=0,le=1_000_000,allow_inf_nan=False)
    target_roas:float|None=Field(default=None,gt=0,le=1000,allow_inf_nan=False)
    min_impressions:int=Field(default=1000,ge=100,le=1_000_000)
    min_conversions:int=Field(default=10,ge=1,le=1000)
    conversion_lag_days:int=Field(default=3,ge=0,le=30)

def metrics(values):
    spend=values['spend_cents']/100;revenue=values['revenue_cents']/100
    return dict(spend=spend,revenue=revenue,impressions=values['impressions'],clicks=values['clicks'],conversions=values['conversions'],
                ctr=round(values['clicks']/values['impressions']*100,2) if values['impressions'] else None,
                cpc=round(spend/values['clicks'],2) if values['clicks'] else None,
                cpa=round(spend/values['conversions'],2) if values['conversions'] else None,
                cvr=round(values['conversions']/values['clicks']*100,2) if values['clicks'] else None,
                roas=round(revenue/spend,2) if spend else None)

def assess(current,previous,targets):
    notes=[];state='observe'
    if current['impressions']<targets['min_impressions']:
        return 'insufficient_data',['Below your minimum impression threshold. Collect more delivery before judging creative.']
    if targets['target_cpa'] is None and targets['target_roas'] is None:
        notes.append('Set a business-specific CPA or ROAS target before making budget decisions.')
    if current['conversions']<targets['min_conversions']:
        notes.append('Below your minimum conversion count. Results are directional, not a proven winner.')
    if targets['target_cpa'] and current['spend']>=3*targets['target_cpa'] and current['conversions']==0:
        state='review';notes.append('Spend exceeds 3× target CPA with no attributed conversions. Verify tracking and the landing-page funnel before considering a pause.')
    if current['cpa'] is not None and targets['target_cpa'] and current['cpa']>targets['target_cpa']:
        state='review';notes.append('CPA is above your target. Review offer, landing-page alignment and lead quality.')
    if current['roas'] is not None and targets['target_roas'] and current['roas']<targets['target_roas']:
        state='review';notes.append('Attributed ROAS is below target. Reconcile revenue and attribution before changing spend.')
    if previous['ctr'] and current['ctr'] is not None and current['ctr']<previous['ctr']*.8:
        notes.append('CTR declined over 20% versus the matched previous window. Test a fresh hook; this alone does not prove fatigue.')
    if current['conversions']>=targets['min_conversions'] and (targets['target_cpa'] or targets['target_roas']) and state!='review':
        state='candidate';notes.append('Targets met with your minimum sample. Candidate for a controlled experiment, not automatic scaling or statistical significance.')
    if not notes:notes.append('No target breach detected. Continue monitoring while changing one variable at a time.')
    return state,notes

@router.get('/')
async def report(days:int=Query(14,ge=7,le=90),actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);context=context_data(profile)
    targets=TargetsInput(**(profile.meta_json or {}).get('ad_targets',{})).model_dump()
    end=datetime.now(ZoneInfo(context['timezone'])).date()-timedelta(days=targets['conversion_lag_days']);start=end-timedelta(days=days-1);previous=start-timedelta(days=days)
    rows=(await db.scalars(select(AdPerformance).where(AdPerformance.business_profile_id==profile.id,AdPerformance.day>=str(previous),AdPerformance.day<=str(end)))).all()
    groups=defaultdict(lambda:{'current':dict(impressions=0,clicks=0,conversions=0,spend_cents=0,revenue_cents=0),'previous':dict(impressions=0,clicks=0,conversions=0,spend_cents=0,revenue_cents=0),'days':set()})
    for row in rows:
        key=(row.platform,row.campaign,row.creative,row.currency,row.attribution)
        group=groups[key];period='current' if row.day>=str(start) else 'previous'
        for key2 in group[period]:group[period][key2]+=getattr(row,key2)
        if period=='current':group['days'].add(row.day)
    output=[]
    for (platform,campaign,creative,currency,attribution),group in groups.items():
        if not group['days']:continue
        current=metrics(group['current']);prior=metrics(group['previous'])
        applicable={**targets,'target_cpa':targets['target_cpa'] if currency==context['currency'] else None}
        state,notes=assess(current,prior,applicable)
        if currency!=context['currency']:notes.append('Different reporting currency; monetary CPA target is not applied. No FX conversion performed.')
        output.append(dict(platform=platform,campaign=campaign,creative=creative,currency=currency,attribution=attribution,current=current,previous=prior,state=state,notes=notes,observed_days=len(group['days'])))
    output.sort(key=lambda g:g['current']['spend'],reverse=True)
    return dict(items=output,targets=targets,start=str(start),end=str(end),previous_start=str(previous),currency=context['currency'],days=days,
                caveat='Source: manually supplied daily reports. Attribution windows and currencies remain separate. Recent days excluded for conversion lag. Recommendations never change live campaigns.')

@router.put('/targets')
async def save_targets(data:TargetsInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);profile.meta_json={**(profile.meta_json or {}),'ad_targets':data.model_dump()}
    await db.commit();return data.model_dump()

async def store_rows(rows,db,profile):
    inserted=0;updated=0
    for data in rows:
        values=data.model_dump();values['day']=str(data.day);values['spend_cents']=int(data.spend*100);values['revenue_cents']=int(data.revenue*100);values.pop('spend');values.pop('revenue')
        filters=[AdPerformance.business_profile_id==profile.id]+[getattr(AdPerformance,k)==values[k] for k in ('day','platform','campaign','creative','currency','attribution')]
        row=await db.scalar(select(AdPerformance).where(*filters))
        if row:
            for key,value in values.items():setattr(row,key,value)
            updated+=1
        else:db.add(AdPerformance(business_profile_id=profile.id,**values));inserted+=1
    try:await db.commit()
    except IntegrityError:
        await db.rollback();raise HTTPException(409,'A concurrent import changed these rows. Retry the import; daily keys prevent double counting.')
    return dict(inserted=inserted,updated=updated)

@router.post('/records')
async def save_record(data:PerformanceInput,actor=Depends(get_current_user),db=Depends(get_db)):
    return await store_rows([data],db,await business(db,actor))

@router.post('/import')
async def import_csv(data:ImportInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    try:
        reader=csv.DictReader(io.StringIO(data.csv_text.lstrip('\ufeff')))
        rows=[];seen=set()
        for number,row in enumerate(reader,2):
            if number>1001:raise ValueError('Maximum 1,000 daily records per import')
            item=PerformanceInput.model_validate(row)
            key=(item.day,item.platform,item.campaign,item.creative,item.currency,item.attribution)
            if key in seen:raise ValueError(f'Duplicate daily record at line {number}')
            seen.add(key);rows.append(item)
        if not rows:raise ValueError('CSV has no data rows')
    except ValueError as exc:raise HTTPException(422,str(exc)[:1500])
    return await store_rows(rows,db,profile)
