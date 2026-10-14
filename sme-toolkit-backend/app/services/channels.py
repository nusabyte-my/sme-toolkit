"""Verified Telegram/Meta connectors. Encrypted credentials; deduplicated inbound; approval outbox."""
import asyncio
import hashlib
import hmac
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit
import httpx
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
from sqlalchemy import select, update, func
from app.config import settings
from app.database import AgentChannel, ChannelMessage, ChannelOutbox, BusinessAgent, BusinessProfile, async_session_maker
from app.services.agent_runtime import channel_reply


class DeliveryUncertain(Exception):
    pass


def cipher():
    if not settings.channel_encryption_key:raise HTTPException(503,'Set CHANNEL_ENCRYPTION_KEY on the server before connecting a channel. Existing business records are unchanged.')
    try:return Fernet(settings.channel_encryption_key.encode())
    except (ValueError,TypeError):raise HTTPException(503,'CHANNEL_ENCRYPTION_KEY is invalid. Use a Fernet key and keep it backed up; changing it makes stored channel credentials unreadable.')


def encrypt(values):return cipher().encrypt(json.dumps(values).encode()).decode()


def decrypt(value):
    try:return json.loads(cipher().decrypt(value.encode()))
    except (InvalidToken,ValueError):raise HTTPException(503,'Stored channel credentials cannot be decrypted. Restore the encryption key or reconnect this channel.')


def callback_url(channel):
    base=settings.public_webhook_base_url.rstrip('/')
    parsed=urlsplit(base)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise HTTPException(503,'Set PUBLIC_WEBHOOK_BASE_URL to the public HTTPS origin of this API before registering webhooks.')
    if parsed.hostname.lower() in ('localhost','127.0.0.1','::1'):
        raise HTTPException(503,'Providers cannot reach a localhost callback. Configure a public HTTPS API origin.')
    return f'{base}/channels/webhook/{channel.id}'


def channel_data(row):
    try:url=callback_url(row)
    except HTTPException:url=None
    return {k:getattr(row,k) for k in ('id','agent_id','platform','external_id','name','status','automation','response_mode','fixed_reply','daily_limit')} | {
        'callback_url':url,'verify_token':row.verify_token if row.platform=='whatsapp' else None,
        'credentials_stored':bool(row.credentials),'created_at':row.created_at.isoformat()+'Z'}


async def request_provider(method,url,headers=None,payload=None,delivery=False):
    try:
        async with httpx.AsyncClient(timeout=25,follow_redirects=False) as client:
            response=await client.request(method,url,headers=headers,json=payload)
        data=response.json()
        if not isinstance(data,dict):raise ValueError('Invalid provider response')
    except (httpx.HTTPError,ValueError):
        if delivery:raise DeliveryUncertain('Provider confirmation was not received. Delivery is unknown; check the provider before sending again.')
        raise HTTPException(502,'The messaging provider could not be verified. Check credentials and connectivity; no connection was fabricated.')
    if response.status_code>=500 and delivery:raise DeliveryUncertain('Provider returned a server error. Delivery is unknown; check the provider before sending again.')
    if not response.is_success or data.get('ok') is False or data.get('error'):
        raise HTTPException(502,'Provider rejected the request. Check token permissions, account configuration and message policy. No success was recorded.')
    return data


def graph_url(phone_id,suffix=''):
    if not re.fullmatch(r'v\d+\.\d+',settings.whatsapp_api_version):raise HTTPException(503,'Invalid configured WhatsApp API version.')
    if not re.fullmatch(r'\d{5,30}',phone_id):raise HTTPException(422,'Use the Meta phone-number ID, not the displayed phone number.')
    return f'https://graph.facebook.com/{settings.whatsapp_api_version}/{phone_id}{suffix}'


async def verify_telegram(token):
    if not re.fullmatch(r'\d{5,20}:[A-Za-z0-9_-]{20,200}',token):raise HTTPException(422,'Enter a BotFather token in the correct format.')
    result=await request_provider('GET',f'https://api.telegram.org/bot{token}/getMe')
    bot=result.get('result',{})
    if not result.get('ok') or not bot.get('is_bot') or not bot.get('id'):raise HTTPException(502,'Telegram did not return a verified bot identity.')
    return str(bot['id']),bot.get('username') or bot.get('first_name') or str(bot['id'])


async def verify_whatsapp(token,phone_id):
    data=await request_provider('GET',graph_url(phone_id)+'?fields=id,display_phone_number,verified_name',headers={'Authorization':'Bearer '+token})
    if str(data.get('id'))!=phone_id:raise HTTPException(502,'Meta did not verify that phone-number ID.')
    return phone_id,str(data.get('verified_name') or data.get('display_phone_number') or phone_id)


async def register_telegram(channel):
    values=decrypt(channel.credentials)
    result=await request_provider('POST',f"https://api.telegram.org/bot{values['token']}/setWebhook",
              payload={'url':callback_url(channel),'secret_token':channel.webhook_secret,'allowed_updates':['message'],'drop_pending_updates':False})
    if result.get('result') is not True:raise HTTPException(502,'Telegram did not confirm webhook registration.')


def provider_time(value):
    try:
        instant=datetime.fromtimestamp(int(value),timezone.utc).replace(tzinfo=None)
        if instant>datetime.utcnow()+timedelta(minutes=5):return None
        return instant
    except (ValueError,TypeError,OverflowError,OSError):return None


async def ingest(db,channel,payload):
    await db.execute(update(AgentChannel).where(AgentChannel.id==channel.id).values(name=AgentChannel.name))
    await db.refresh(channel)
    messages=[]
    if channel.platform=='telegram':
        event=payload.get('message') or {};chat=event.get('chat') or {};sender=event.get('from') or {}
        when=provider_time(event.get('date'))
        # Ignore groups, bots, edited messages and commands without text. Never use arbitrary update senders as owners.
        if not isinstance(chat.get('id'),int):return 0
        if chat.get('type')=='private' and not sender.get('is_bot') and isinstance(event.get('text'),str) and payload.get('update_id') is not None and when:
            messages.append((str(payload['update_id']),str(chat.get('id')),event['text'][:12000],when))
    else:
        for entry in payload.get('entry',[])[:20]:
            for change in entry.get('changes',[])[:20]:
                value=change.get('value') or {}
                if str((value.get('metadata') or {}).get('phone_number_id'))!=channel.external_id:continue
                for event in value.get('messages',[])[:100]:
                    when=provider_time(event.get('timestamp'))
                    text=(event.get('text') or {}).get('body')
                    if event.get('type')=='text' and event.get('id') and re.fullmatch(r'\d{7,16}',str(event.get('from',''))) and isinstance(text,str) and when:
                        messages.append((str(event['id']),str(event['from']),text[:12000],when))
                for status in value.get('statuses',[])[:100]:
                    row=await db.scalar(select(ChannelOutbox).where(ChannelOutbox.channel_id==channel.id,ChannelOutbox.provider_message_id==str(status.get('id'))))
                    next_status=status.get('status')
                    if row and next_status in ('sent','delivered','read','failed'):
                        ranks={'sent':1,'delivered':2,'read':3}
                        if next_status=='failed' and row.status not in ('delivered','read'):row.status='failed';row.error='WhatsApp reported delivery failure. Review provider status before a new message.'
                        elif ranks.get(next_status,0)>ranks.get(row.status,0):row.status=next_status
    created=0
    for external_id,peer,text,when in messages:
        if not peer or await db.scalar(select(ChannelMessage.id).where(ChannelMessage.channel_id==channel.id,ChannelMessage.external_id==external_id)):continue
        db.add(ChannelMessage(channel_id=channel.id,external_id=external_id,peer=peer,content=text,status='queued' if channel.automation!='manual' else 'received',received_at=when));created+=1
    await db.commit()
    return created


async def send_outbox(db,outbox_id,profile_id):
    outbox=await db.scalar(select(ChannelOutbox).where(ChannelOutbox.id==outbox_id))
    if not outbox:raise HTTPException(404,'Outbox message not found.')
    channel=await db.scalar(select(AgentChannel).where(AgentChannel.id==outbox.channel_id,AgentChannel.business_profile_id==profile_id))
    if not channel:raise HTTPException(404,'Channel not found.')
    await db.execute(update(AgentChannel).where(AgentChannel.id==channel.id).values(name=AgentChannel.name))
    await db.refresh(channel)
    if channel.status not in ('verified','connected'):raise HTTPException(409,'This channel is paused or not verified.')
    values=decrypt(channel.credentials)
    today=datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)
    sent=await db.scalar(select(func.count()).select_from(ChannelOutbox).where(ChannelOutbox.channel_id==channel.id,ChannelOutbox.attempted_at>=today,
               ChannelOutbox.status.in_(['sending','sent','delivered','read','unknown'])))
    if sent>=channel.daily_limit:raise HTTPException(429,'Channel daily send limit reached. Wait until the next UTC day.')
    if outbox.template and not outbox.consent:raise HTTPException(422,'Confirm recipient opt-in before sending a WhatsApp template.')
    if channel.platform=='whatsapp' and not outbox.template:
        last=await db.scalar(select(func.max(ChannelMessage.received_at)).where(ChannelMessage.channel_id==channel.id,ChannelMessage.peer==outbox.peer))
        if not last or last<datetime.utcnow()-timedelta(hours=24):raise HTTPException(409,'The WhatsApp 24-hour customer-service window is closed. Use an approved template with recipient opt-in.')
    claim=await db.execute(update(ChannelOutbox).where(ChannelOutbox.id==outbox.id,ChannelOutbox.status=='pending').values(status='sending',attempted_at=datetime.utcnow()))
    if not claim.rowcount:raise HTTPException(409,'This message was already handled or is sending. Refresh its status; do not submit a duplicate.')
    await db.commit()
    try:
        if channel.platform=='telegram':
            result=await request_provider('POST',f"https://api.telegram.org/bot{values['token']}/sendMessage",payload={'chat_id':outbox.peer,'text':outbox.content,'link_preview_options':{'is_disabled':True}},delivery=True)
            message_id=(result.get('result') or {}).get('message_id')
            if message_id is None:raise DeliveryUncertain('Telegram returned no message identifier. Check provider history before resending.')
        else:
            payload={'messaging_product':'whatsapp','to':outbox.peer}
            if outbox.template:payload.update(type='template',template=outbox.template)
            else:payload.update(type='text',text={'body':outbox.content,'preview_url':False})
            result=await request_provider('POST',graph_url(channel.external_id,'/messages'),headers={'Authorization':'Bearer '+values['token']},payload=payload,delivery=True)
            message_id=(result.get('messages') or [{}])[0].get('id')
            if not message_id:raise DeliveryUncertain('WhatsApp returned no message identifier. Check provider history before resending.')
        await db.refresh(outbox)
        if outbox.status not in ('delivered','read'):outbox.status='sent'
        outbox.provider_message_id=str(message_id);outbox.sent_at=datetime.utcnow();outbox.error=None
    except DeliveryUncertain as exc:
        outbox.status='unknown';outbox.error=str(exc)
    except HTTPException as exc:
        outbox.status='failed';outbox.error=exc.detail
    await db.commit()
    return outbox


async def process_channel_queue(session_factory=async_session_maker):
    async with session_factory() as db:
        # A process death cannot safely retry a send; record uncertainty for owner review.
        await db.execute(update(ChannelOutbox).where(ChannelOutbox.status=='sending',ChannelOutbox.attempted_at<datetime.utcnow()-timedelta(minutes=10)).values(status='unknown',error='Send was interrupted. Check provider history before creating another message.'))
        await db.execute(update(ChannelMessage).where(ChannelMessage.status=='processing',ChannelMessage.processing_at<datetime.utcnow()-timedelta(minutes=10)).values(status='failed',error='Processing interrupted. Review this message manually.'))
        await db.commit()
        ids=list(await db.scalars(select(ChannelMessage.id).where(ChannelMessage.status=='queued').order_by(ChannelMessage.received_at).limit(25)))
    for mid in ids:
        async with session_factory() as db:
            row=await db.get(ChannelMessage,mid);channel=await db.get(AgentChannel,row.channel_id)
            if not channel or channel.status=='paused' or channel.automation=='manual':continue
            agent=await db.get(BusinessAgent,channel.agent_id);profile=await db.get(BusinessProfile,channel.business_profile_id)
            if not agent or not agent.enabled or profile.user_id.startswith('demo-'):
                row.status='failed';row.error='Agent unavailable or demo channel blocked.';await db.commit();continue
            if row.received_at<datetime.utcnow()-timedelta(hours=24):
                row.status='received';row.error='Old inbound message: automatic reply skipped.';await db.commit();continue
            await db.execute(update(AgentChannel).where(AgentChannel.id==channel.id).values(name=AgentChannel.name))
            await db.refresh(channel)
            if channel.status=='paused' or channel.automation=='manual':
                await db.rollback();continue
            count=await db.scalar(select(func.count()).select_from(ChannelMessage).where(ChannelMessage.channel_id==channel.id,ChannelMessage.received_at>=datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0),ChannelMessage.status.in_(['processing','processed','failed'])))
            if count>=channel.daily_limit:continue
            claim=await db.execute(update(ChannelMessage).where(ChannelMessage.id==mid,ChannelMessage.status=='queued').values(status='processing',processing_at=datetime.utcnow()))
            if not claim.rowcount:await db.rollback();continue
            await db.commit()
            try:
                text=channel.fixed_reply if channel.response_mode=='fixed' else await channel_reply(profile,agent,row.content)
                if not text.strip():raise HTTPException(422,'Configure a response before enabling channel automation.')
                await db.refresh(channel);await db.refresh(agent)
                if channel.status=='paused' or channel.automation=='manual' or not agent.enabled:
                    row.status='received';await db.commit();continue
                outbox=ChannelOutbox(channel_id=channel.id,inbound_id=row.id,peer=row.peer,content=text,status='pending',consent=True)
                db.add(outbox);row.status='processed';await db.commit()
                if channel.automation=='auto_reply':await send_outbox(db,outbox.id,profile.id)
            except Exception as exc:
                await db.rollback();row=await db.get(ChannelMessage,mid);row.status='failed';row.error=exc.detail if isinstance(exc,HTTPException) else 'Reply processing failed. Review manually; no successful send is claimed.';await db.commit()
