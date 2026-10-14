"""Owner-scoped business context and ledger-derived evidence. No synthetic metrics."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone, time
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo
import json

from fastapi import HTTPException
from sqlalchemy import select
from app.database import BusinessProfile, SalesTransaction


def iso(value):
    return value.replace(tzinfo=timezone.utc).isoformat() if value else None


async def business(db, actor, required=True):
    profile = await db.scalar(select(BusinessProfile).where(BusinessProfile.user_id == actor))
    if profile is None and required:
        raise HTTPException(409, 'Save your business context first.')
    return profile


def context_data(profile):
    if not profile:
        return None
    meta = profile.meta_json or {}
    saved = meta.get('owner_context', {})
    def text(key, fallback=''):
        value = saved.get(key, meta.get(key, fallback))
        if isinstance(value, list):
            return '\n'.join(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False) for v in value)
        return value if isinstance(value, str) else ''
    return {
        'id': profile.id, 'company_name': profile.company_name,
        'is_demo': bool(meta.get('demo')),
        'industry': profile.industry or '', 'website': profile.website or '',
        'business_description': text('business_description'),
        'products_services': text('products_services'), 'target_market': text('target_market'),
        'brand_voice': text('brand_voice'), 'goals': text('goals', text('short_term_goals')),
        'currency': text('currency', text('revenue_currency', 'MYR')) or 'MYR',
        'timezone': text('timezone', 'Asia/Kuala_Lumpur') or 'Asia/Kuala_Lumpur',
        'proof_points': text('proof_points'), 'constraints': text('constraints'),
        'logo_data_url': text('logo_data_url'),
        'updated_at': iso(profile.updated_at),
    }


def period_start(context, days, now=None):
    now = now or datetime.now(timezone.utc)
    zone = ZoneInfo(context['timezone'] if context else 'Asia/Kuala_Lumpur')
    today = now.astimezone(zone).date()
    first = today - timedelta(days=days - 1)
    start = datetime.combine(first, time.min, zone).astimezone(timezone.utc).replace(tzinfo=None)
    previous = datetime.combine(first - timedelta(days=days), time.min, zone).astimezone(timezone.utc).replace(tzinfo=None)
    return start, previous, now.replace(tzinfo=None), zone, first


async def sales_summary(db, profile, days=30, now=None):
    context = context_data(profile)
    currency = context['currency'] if context else 'MYR'
    start, previous, end, zone, first = period_start(context, days, now)
    summary = dict(days=days, currency=currency, revenue=0, previous_revenue=0,
                   change_percent=None, orders=0, pending_orders=0, refunded_orders=0,
                   average_order_value=0, excluded_currency_orders=0, by_platform=[],
                   daily=[], latest_at=None)
    daily = {str(first + timedelta(days=i)): Decimal(0) for i in range(days)}
    platforms = defaultdict(lambda: {'revenue': Decimal(0), 'orders': 0})
    revenue = Decimal(0)
    prior_revenue = Decimal(0)
    paid_orders = 0
    latest = None
    if profile:
        rows = (await db.scalars(select(SalesTransaction).where(
            SalesTransaction.business_profile_id == profile.id,
            SalesTransaction.transaction_date >= previous,
            SalesTransaction.transaction_date <= end,
        ))).all()
        for row in rows:
            current = row.transaction_date >= start
            if current:
                summary['orders'] += 1
                summary['pending_orders'] += row.status == 'pending'
                summary['refunded_orders'] += row.status == 'refunded'
                latest = max(latest, row.transaction_date) if latest else row.transaction_date
                platforms[row.platform]['orders'] += 1
            if row.currency != currency:
                summary['excluded_currency_orders'] += int(current)
                continue
            if row.status not in ('completed', 'paid'):
                continue
            amount = Decimal(str(row.amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if current:
                revenue += amount
                paid_orders += 1
                platforms[row.platform]['revenue'] += amount
                day = str(row.transaction_date.replace(tzinfo=timezone.utc).astimezone(zone).date())
                daily[day] += amount
            else:
                prior_revenue += amount
    summary.update(
        revenue=float(revenue), previous_revenue=float(prior_revenue),
        change_percent=float(((revenue - prior_revenue) * 100 / prior_revenue).quantize(Decimal('0.1'))) if prior_revenue else None,
        average_order_value=float((revenue / paid_orders).quantize(Decimal('0.01'))) if paid_orders else 0,
        by_platform=[{'platform': k, 'revenue': float(v['revenue']), 'orders': v['orders']}
                     for k, v in sorted(platforms.items(), key=lambda item: item[1]['revenue'], reverse=True)],
        daily=[{'date': k, 'revenue': float(v)} for k, v in daily.items()], latest_at=iso(latest),
    )
    return summary


def run_data(row):
    snapshot = row.context_snapshot or {}
    return {key: getattr(row, key) for key in ('id', 'kind', 'objective', 'status', 'output', 'error', 'provider', 'context_snapshot')} | {'created_at': iso(row.created_at), 'skill': snapshot.get('_advisor'), 'evidence': snapshot.get('_evidence')}


def campaign_data(row):
    return {key: getattr(row, key) for key in ('id', 'title', 'platform', 'caption', 'status')} | {
        'scheduled_at': iso(row.scheduled_at), 'created_at': iso(row.created_at), 'updated_at': iso(row.updated_at)}


def ledger_brief(kind, objective, context, sales):
    """A reproducible evidence brief, explicitly not an LLM or financial health score."""
    currency = sales['currency']
    lines = [f"{context['company_name']} — {kind.replace('_', ' ').title()}",
             f"Objective: {objective}", '',
             f"Evidence window: {sales['days']} calendar days, {context['timezone']}.",
             f"Recorded completed sales: {currency} {sales['revenue']:,.2f}. Orders recorded: {sales['orders']}.",
             f"Pending orders: {sales['pending_orders']}. Refunded orders: {sales['refunded_orders']}."]
    if sales['change_percent'] is not None:
        lines.append(f"Completed revenue change versus previous period: {sales['change_percent']:+.1f}% (current day is partial).")
    else:
        lines.append('No non-zero prior-period revenue; growth percentage cannot be calculated.')
    if sales['excluded_currency_orders']:
        lines.append(f"{sales['excluded_currency_orders']} orders use another currency; excluded from revenue, not converted.")
    lines += ['', 'Recommended next actions:']
    if not sales['orders']:
        lines.append('- Record actual sales or import a verified marketplace export before judging demand.')
    if sales['pending_orders']:
        lines.append(f"- Review the {sales['pending_orders']} pending orders; confirm payment or resolve fulfilment before marking completed.")
    if sales['refunded_orders']:
        lines.append('- Investigate refunded orders before increasing acquisition spend.')
    if sales['by_platform'] and sales['revenue'] > 0:
        top = sales['by_platform'][0]
        lines.append(f"- Review concentration: {top['platform']} accounts for {top['revenue'] / sales['revenue']:.0%} of recorded completed revenue.")
    missing = [label for key, label in [('products_services','products/services'),('target_market','target customers'),('goals','business goals')] if not context[key].strip()]
    if missing:
        lines.append('- Complete business context: ' + ', '.join(missing) + '.')
    if kind in ('business_review', 'operations'):
        lines.append('- Compare your stated goals with the recorded sales; assign an owner and review date to the next action.')
    if context['goals']:
        lines.extend(['', 'Owner-stated goals:', context['goals']])
    lines += ['', 'Limits: recorded sales are not profit, cash flow, verified bank receipts, or the whole market. This brief does not incorporate the separate bookkeeping journals or attributed ad reports. Inventory and live bank feeds are not connected. This is a ledger-rules brief, not an AI-generated assessment. Nothing has been sent, published or changed externally.']
    return '\n'.join(lines)
