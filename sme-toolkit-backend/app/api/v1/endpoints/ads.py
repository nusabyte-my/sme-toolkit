"""Authenticated ad authoring, bounded media storage, real Gemini image/Veo APIs."""
import base64
import binascii
import json
import re
from datetime import datetime
from typing import Literal
from urllib.parse import urlsplit, urljoin
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.auth import get_current_user
from app.config import settings
from app.database import get_db, AdProfile, AdDraft, AdAsset, AdVideoJob
from app.services.owner_service import business, iso
from app.api.v1.endpoints.owner import capabilities, execute_run, RunInput
from app.providers.rate_limiter import get_rate_limiter
from app.schemas.creative_editor import EditorFields
import asyncio
import shutil
import tempfile
from pathlib import Path

router = APIRouter()
GOOGLE = 'https://generativelanguage.googleapis.com/v1beta'
MAX_MEDIA = 30 * 1024 * 1024


class ProfileInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=120)
    product: str = Field(min_length=1, max_length=2000)
    offer: str = Field(default='', max_length=2000)
    audience: str = Field(min_length=1, max_length=2000)
    voice: str = Field(default='', max_length=1000)
    channel: Literal['Meta', 'Google', 'TikTok', 'LinkedIn', 'Other'] = 'Meta'
    cta: str = Field(default='', max_length=100)
    landing_url: str = Field(default='', max_length=500)
    language: str = Field(default='English', max_length=80)
    prohibited_claims: str = Field(default='', max_length=2000)
    brand_color: str = Field(default='#7C3AED', pattern=r'^#[0-9a-fA-F]{6}$')

    @field_validator('landing_url')
    @classmethod
    def validate_url(cls, value):
        if value:
            url = urlsplit(value)
            if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password:
                raise ValueError('Use an http(s) URL without credentials')
        return value


class DraftInput(EditorFields):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    profile_id: str = Field(max_length=50)
    title: str = Field(min_length=1, max_length=160)
    headline: str = Field(default='', max_length=200)
    body: str = Field(default='', max_length=10000)
    cta: str = Field(default='', max_length=100)
    image_prompt: str = Field(default='', max_length=4000)
    video_prompt: str = Field(default='', max_length=4000)
    script: str = Field(default='', max_length=4000)
    aspect_ratio: Literal['1:1', '4:5', '9:16', '16:9'] = '1:1'
    duration: float = Field(default=6, ge=.5, le=120)
    asset_id: str | None = Field(default=None, max_length=50)
    video_asset_id: str | None = Field(default=None, max_length=50)


class ApproveInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['approved', 'draft']


class AssetInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(min_length=1, max_length=160)
    mime: Literal['image/png', 'image/jpeg', 'image/webp', 'video/webm', 'video/mp4', 'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/webm']
    data: str = Field(min_length=1, max_length=42_000_000)


class GenerateInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    profile_id: str = Field(max_length=50)
    prompt: str = Field(min_length=3, max_length=4000)
    aspect_ratio: Literal['1:1', '4:5', '9:16', '16:9'] = '1:1'
    asset_id: str | None = Field(default=None, max_length=50)


class VideoInput(GenerateInput):
    request_id: UUID
    aspect_ratio: Literal['9:16', '16:9'] = '9:16'
    duration: Literal[4, 6, 8] = 6


async def owned(db, model, item_id, profile):
    row = await db.scalar(select(model).where(model.id == item_id, model.business_profile_id == profile.id))
    if not row:
        raise HTTPException(404, 'Record not found')
    return row


async def validate_editor_assets(data, db, profile):
    if data.audio_asset_id:
        audio=await owned(db,AdAsset,data.audio_asset_id,profile)
        if not audio.mime.startswith('audio/'):raise HTTPException(422,'Soundtrack requires an audio asset')
    for scene in data.scenes:
        if scene.asset_id:
            asset=await owned(db,AdAsset,scene.asset_id,profile)
            if not asset.mime.startswith(('image/','video/')):raise HTTPException(422,'Scene requires image or video media')


def record(row):
    result = {'id': row.id, **row.data, 'created_at': iso(row.created_at), 'updated_at': iso(row.updated_at)}
    if isinstance(row, AdDraft):
        result.update(profile_id=row.profile_id, profile_snapshot=row.profile_snapshot, status=row.status)
    return result


def asset_info(row):
    return {'id': row.id, 'name': row.name, 'mime': row.mime, 'created_at': iso(row.created_at)}


def job_info(row):
    return {'id': row.id, 'status': row.status, 'error': row.error, 'asset_id': row.asset_id,
            'prompt': row.prompt, 'created_at': iso(row.created_at)}


def validate_media(raw, mime):
    if not raw or len(raw) > MAX_MEDIA:
        raise HTTPException(413, 'Media must be between 1 byte and 30 MB.')
    signatures = {
        'image/png': raw.startswith(b'\x89PNG\r\n\x1a\n'),
        'image/jpeg': raw.startswith(b'\xff\xd8\xff'),
        'image/webp': raw.startswith(b'RIFF') and raw[8:12] == b'WEBP',
        'video/webm': raw.startswith(b'\x1aE\xdf\xa3'),
        'video/mp4': raw[4:8] == b'ftyp',
        'audio/mpeg': raw.startswith(b'ID3') or (len(raw)>1 and raw[0]==255 and raw[1]&224==224),
        'audio/wav': raw.startswith(b'RIFF') and raw[8:12]==b'WAVE',
        'audio/ogg': raw.startswith(b'OggS'),
        'audio/webm': raw.startswith(b'\x1aE\xdf\xa3'),
    }
    if not signatures.get(mime):
        raise HTTPException(415, 'File contents do not match a supported image or video type.')
    if mime.startswith('image/') and len(raw) > 10 * 1024 * 1024:
        raise HTTPException(413, 'Images must be smaller than 10 MB.')


async def google_request(method, path, body=None):
    if not settings.gemini_api_key:
        raise HTTPException(503, 'Set GEMINI_API_KEY on the server to generate AI images or video. Manual media editing remains available.')
    try:
        async with httpx.AsyncClient(timeout=100) as client:
            response = await client.request(method, f'{GOOGLE}/{path}', headers={'x-goog-api-key': settings.gemini_api_key}, json=body)
        if not response.is_success:
            payload = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            reasons = [entry.get('reason') for entry in payload.get('error', {}).get('details', []) if isinstance(entry, dict)]
            if 'API_KEY_INVALID' in reasons:
                raise HTTPException(502, 'The configured Gemini API key is invalid. Update GEMINI_API_KEY on the server. Your draft is unchanged.')
            raise HTTPException(502, f'Google generation request failed (HTTP {response.status_code}). Check model access, quota and billing. Your existing draft is unchanged.')
        return response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, 'Generation service could not be reached or returned invalid data. Existing drafts are unchanged.')


@router.get('/')
async def library(actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    profiles = await db.scalars(select(AdProfile).where(AdProfile.business_profile_id == profile.id).order_by(AdProfile.updated_at.desc()))
    drafts = await db.scalars(select(AdDraft).where(AdDraft.business_profile_id == profile.id).order_by(AdDraft.updated_at.desc()).limit(100))
    jobs = await db.scalars(select(AdVideoJob).where(AdVideoJob.business_profile_id == profile.id).order_by(AdVideoJob.created_at.desc()).limit(30))
    # Select metadata only: do not load every media blob for a library view.
    assets = await db.execute(select(AdAsset.id, AdAsset.name, AdAsset.mime, AdAsset.created_at).where(AdAsset.business_profile_id == profile.id).order_by(AdAsset.created_at.desc()).limit(100))
    return {'profiles':[record(p) for p in profiles], 'drafts':[record(d) for d in drafts],
            'assets':[asset_info(a) for a in assets], 'jobs':[job_info(j) for j in jobs],
            'capabilities':{**capabilities(actor), 'image_available':bool(settings.gemini_api_key) and not actor.startswith('demo-'),
                            'video_available':bool(settings.gemini_api_key) and not actor.startswith('demo-'), 'image_model':settings.gemini_image_model,
                            'video_model':settings.gemini_video_model, 'mp4_available':bool(shutil.which(settings.ffmpeg_path))}}


@router.post('/profiles', status_code=201)
async def create_profile(data: ProfileInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = AdProfile(business_profile_id=profile.id, data=data.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return record(row)


@router.put('/profiles/{profile_id}')
async def edit_profile(profile_id: str, data: ProfileInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await owned(db, AdProfile, profile_id, profile)
    row.data = data.model_dump()
    row.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(row)
    return record(row)


@router.post('/drafts', status_code=201)
async def create_draft(data: DraftInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    ad_profile = await owned(db, AdProfile, data.profile_id, profile)
    for asset_id, kind in ((data.asset_id, 'image/'), (data.video_asset_id, 'video/')):
        if asset_id:
            asset = await owned(db, AdAsset, asset_id, profile)
            if not asset.mime.startswith(kind):
                raise HTTPException(422, 'Selected media does not match its image/video field.')
    await validate_editor_assets(data, db, profile)
    row = AdDraft(business_profile_id=profile.id, profile_id=ad_profile.id, profile_snapshot=ad_profile.data,
                  data=data.model_dump(exclude={'profile_id'}))
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return record(row)


@router.put('/drafts/{draft_id}')
async def save_draft(draft_id: str, data: DraftInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await owned(db, AdDraft, draft_id, profile)
    ad_profile = await owned(db, AdProfile, data.profile_id, profile)
    for asset_id, kind in ((data.asset_id, 'image/'), (data.video_asset_id, 'video/')):
        if asset_id:
            asset = await owned(db, AdAsset, asset_id, profile)
            if not asset.mime.startswith(kind):
                raise HTTPException(422, 'Selected media does not match its image/video field.')
    await validate_editor_assets(data, db, profile)
    row.data = data.model_dump(exclude={'profile_id'})
    row.profile_id = ad_profile.id
    row.profile_snapshot = ad_profile.data
    row.status = 'draft'
    row.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(row)
    return record(row)


@router.patch('/drafts/{draft_id}')
async def approve_draft(draft_id: str, data: ApproveInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await owned(db, AdDraft, draft_id, profile)
    row.status = data.status
    await db.commit()
    await db.refresh(row)
    return record(row)


@router.post('/assets', status_code=201)
async def upload_asset(data: AssetInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    try:
        raw = base64.b64decode(data.data, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(422, 'Invalid base64 media data')
    validate_media(raw, data.mime)
    row = AdAsset(business_profile_id=profile.id, name=data.name, mime=data.mime, content=raw)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return asset_info(row)


@router.get('/assets/{asset_id}')
async def download_asset(asset_id: str, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await owned(db, AdAsset, asset_id, profile)
    return Response(row.content, media_type=row.mime, headers={'Cache-Control':'private, no-store', 'X-Content-Type-Options':'nosniff'})


@router.post('/copy')
async def generate_copy(data: GenerateInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    ad_profile = await owned(db, AdProfile, data.profile_id, profile)
    objective = 'Write ad copy grounded ONLY in this advertising profile. Respect prohibited claims.\n' + json.dumps(ad_profile.data, ensure_ascii=False) + '\nRequest: ' + data.prompt
    # The saved run captures the exact ad profile supplied, independently of later edits.
    return await execute_run(RunInput.model_construct(kind='marketing', objective=objective), actor, db)


@router.post('/image', status_code=201)
async def generate_image(data: GenerateInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    ad_profile = await owned(db, AdProfile, data.profile_id, profile)
    limiter = get_rate_limiter()
    if not (await limiter.check_rate_limit(actor, 'free', 'image')).allowed:
        raise HTTPException(429, 'Too many media generation requests. Wait before generating again.')
    await limiter.increment_usage(actor, 'image')
    prompt = 'Create an advertising visual. No invented claims, statistics or testimonials. Keep readable text out; the editor adds overlays. Advertising profile: ' + json.dumps(ad_profile.data, ensure_ascii=False) + '\nCreative direction: ' + data.prompt
    parts = [{'text':prompt}]
    if data.asset_id:
        reference = await owned(db, AdAsset, data.asset_id, profile)
        if not reference.mime.startswith('image/'):
            raise HTTPException(422, 'Use an image as the reference asset.')
        parts.append({'inlineData':{'mimeType':reference.mime,'data':base64.b64encode(reference.content).decode('ascii')}})
    model = settings.gemini_image_model
    if not re.fullmatch(r'[A-Za-z0-9._-]+', model):
        raise HTTPException(503, 'Invalid image model configuration')
    result = await google_request('POST', f'models/{model}:generateContent', {
        'contents':[{'parts':parts}], 'generationConfig':{'responseModalities':['TEXT','IMAGE'], 'imageConfig':{'aspectRatio':data.aspect_ratio}}})
    for candidate in result.get('candidates', []):
        for part in candidate.get('content', {}).get('parts', []):
            inline = part.get('inlineData')
            if inline and inline.get('mimeType', '').startswith('image/'):
                try:
                    raw = base64.b64decode(inline['data'], validate=True)
                except (binascii.Error, KeyError, ValueError):
                    raise HTTPException(502, 'Provider returned an invalid image.')
                validate_media(raw, inline['mimeType'])
                row = AdAsset(business_profile_id=profile.id, name=f"{ad_profile.data['name']} generated image", mime=inline['mimeType'], content=raw)
                db.add(row)
                await db.commit()
                await db.refresh(row)
                return asset_info(row)
    raise HTTPException(502, 'No image was returned. Check the creative request and provider safety restrictions; your existing asset is unchanged.')


@router.post('/video', status_code=201)
async def start_video(data: VideoInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    ad_profile = await owned(db, AdProfile, data.profile_id, profile)
    existing = await db.scalar(select(AdVideoJob).where(AdVideoJob.id == str(data.request_id)))
    if existing:
        if existing.business_profile_id != profile.id:
            raise HTTPException(404, 'Video job not found')
        return job_info(existing)
    if not settings.gemini_api_key:
        raise HTTPException(503, 'Configure GEMINI_API_KEY for AI footage. The silent motion-ad renderer works without an API key.')
    limiter = get_rate_limiter()
    if not (await limiter.check_rate_limit(actor, 'free', 'image')).allowed:
        raise HTTPException(429, 'Too many media generation requests. Wait before generating again.')
    await limiter.increment_usage(actor, 'image')
    prompt = 'Create a commercial video, without invented facts or text overlays. Profile: ' + json.dumps(ad_profile.data, ensure_ascii=False) + '\nDirection: ' + data.prompt
    row = AdVideoJob(id=str(data.request_id), business_profile_id=profile.id, prompt=data.prompt, status='submitting')
    db.add(row)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, 'This generation request was already submitted. Refresh video jobs rather than submitting again.')
    model = settings.gemini_video_model
    if not re.fullmatch(r'[A-Za-z0-9._-]+', model):
        row.status='failed'; row.error='Invalid video model configuration'
    else:
        try:
            result = await google_request('POST', f'models/{model}:predictLongRunning', {
                'instances':[{'prompt':prompt}], 'parameters':{'aspectRatio':data.aspect_ratio,'durationSeconds':str(data.duration),'resolution':'720p'}})
            operation = result.get('name', '')
            if not re.fullmatch(r'[A-Za-z0-9_./-]+', operation) or '..' in operation or '/operations/' not in operation:
                raise HTTPException(502, 'Provider returned an invalid operation identifier.')
            row.operation=operation; row.status='processing'
        except HTTPException as exc:
            row.status='failed'; row.error=str(exc.detail) + ' Check provider history before starting a new request; a timed-out submission may still incur a charge.'
    await db.commit()
    await db.refresh(row)
    return job_info(row)


@router.post('/video/{job_id}/check')
async def check_video(job_id: str, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await owned(db, AdVideoJob, job_id, profile)
    if row.status in ('completed','failed'):
        return job_info(row)
    if not row.operation:
        raise HTTPException(409, 'Submission is not confirmed. Check provider history before retrying to avoid duplicate charges.')
    result = await google_request('GET', row.operation)
    if not result.get('done'):
        return job_info(row)
    samples = result.get('response',{}).get('generateVideoResponse',{}).get('generatedSamples',[])
    if result.get('error') or not samples:
        row.status='failed'; row.error='Video generation failed or was blocked by the provider. Review the prompt and provider quota.'
    else:
        url = samples[0].get('video',{}).get('uri','')
        # Provider URL only; never accept a client URL or forward API keys to arbitrary redirects.
        async with httpx.AsyncClient(timeout=100, follow_redirects=False) as client:
            for _ in range(5):
                parsed=urlsplit(url)
                if parsed.scheme!='https' or parsed.username or parsed.password or parsed.port not in (None,443) or not (parsed.hostname in ('generativelanguage.googleapis.com','storage.googleapis.com') or (parsed.hostname or '').endswith('.googleusercontent.com')):
                    raise HTTPException(502, 'Provider returned an unsupported media download host.')
                headers={'x-goog-api-key':settings.gemini_api_key} if parsed.hostname=='generativelanguage.googleapis.com' else {}
                try:
                    async with client.stream('GET',url,headers=headers) as response:
                        if response.is_redirect:
                            url=urljoin(url,response.headers.get('location','')); continue
                        if not response.is_success:
                            raise HTTPException(502,'Video download failed. Check this job again; no new generation will be charged.')
                        content=bytearray()
                        async for chunk in response.aiter_bytes():
                            content.extend(chunk)
                            if len(content)>MAX_MEDIA:
                                raise HTTPException(413,'Generated video exceeds the 30 MB storage limit.')
                    validate_media(content,'video/mp4')
                    asset=AdAsset(business_profile_id=profile.id,name='Generated video ad',mime='video/mp4',content=bytes(content))
                    db.add(asset); await db.flush(); row.asset_id=asset.id; row.status='completed'; break
                except httpx.HTTPError:
                    raise HTTPException(502,'Video download interrupted. Check the existing job again rather than generating another.')
            else:
                raise HTTPException(502,'Video download exceeded the redirect limit.')
    await db.commit()
    await db.refresh(row)
    return job_info(row)


@router.post('/assets/{asset_id}/mp4', status_code=201)
async def export_mp4(asset_id: str, actor=Depends(get_current_user), db=Depends(get_db)):
    profile=await business(db,actor)
    source=await owned(db,AdAsset,asset_id,profile)
    if source.mime not in ('video/webm','video/mp4'):raise HTTPException(422,'Choose a video asset to convert')
    executable=shutil.which(settings.ffmpeg_path)
    if not executable:raise HTTPException(503,'FFmpeg is not installed on the server. WebM export remains available.')
    with tempfile.TemporaryDirectory(prefix='sme-video-') as directory:
        input_path=Path(directory)/('input.webm' if source.mime=='video/webm' else 'input.mp4')
        output_path=Path(directory)/'output.mp4'
        input_path.write_bytes(source.content)
        process=await asyncio.create_subprocess_exec(executable,'-nostdin','-hide_banner','-loglevel','error','-y','-protocol_whitelist','file,pipe','-i',str(input_path),'-map','0:v:0','-map','0:a?','-t','120','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2','-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart','-fs',str(MAX_MEDIA),str(output_path),stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.PIPE)
        try:
            _,stderr=await asyncio.wait_for(process.communicate(),timeout=120)
        except (asyncio.TimeoutError,asyncio.CancelledError):
            process.kill();await process.communicate()
            raise HTTPException(504,'Video conversion exceeded its time limit. Use WebM or shorten the timeline.')
        if process.returncode or not output_path.is_file():raise HTTPException(422,'Video could not be decoded or converted. Use a supported MP4/WebM source.')
        raw=output_path.read_bytes()
        if len(raw)>=MAX_MEDIA:raise HTTPException(413,'Converted video exceeds 30 MB. Shorten the timeline.')
        validate_media(raw,'video/mp4')
        row=AdAsset(business_profile_id=profile.id,name=source.name.rsplit('.',1)[0]+'.mp4',mime='video/mp4',content=raw)
        db.add(row);await db.commit();await db.refresh(row)
        return asset_info(row)
