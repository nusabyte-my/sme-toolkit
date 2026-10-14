"""Advisor contracts loaded from versioned SKILL.md files; deterministic evidence checks."""
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo
import json
import re

from sqlalchemy import select, func
from app.database import Lead, SalesTransaction, OwnerCampaign, OwnerTask, WorkspaceDocument, AdDraft, BookAccount, BookEntry, BookLine, BookReconciliation, Employee, EmployeeTask, LeaveRequest
from app.services.owner_service import context_data, sales_summary, ledger_brief, iso

SKILL_ROOT = Path(__file__).resolve().parents[2] / 'skills' / 'advisors'


@lru_cache(maxsize=1)
def advisor_catalog():
    catalog = {}
    for path in sorted(SKILL_ROOT.glob('*/SKILL.md')):
        text = path.read_text(encoding='utf-8')
        _, frontmatter, instructions = text.split('---', 2)
        metadata = json.loads(frontmatter)
        catalog[metadata['kind']] = {**metadata, 'instructions': instructions.strip(), 'skill_markdown': text}
    if not catalog:
        raise RuntimeError('Advisor skill files are missing from the deployment.')
    return catalog


def public_advisors():
    return [{key: value for key, value in skill.items() if key != 'instructions'} for skill in advisor_catalog().values()]


def valid_url(value):
    try:
        parsed = urlsplit(value or '')
        return parsed.scheme in ('https', 'http') and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


async def advisor_evidence(db, profile, kind, now=None):
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)
    if now.tzinfo is not None:
        now = now.astimezone(timezone.utc).replace(tzinfo=None)
    context = context_data(profile)
    local_day = now.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(context['timezone'])).date()
    evidence = {'as_of': iso(now), 'business_timezone': context['timezone']}
    issues = []
    observations = []
    limits = []

    if kind in ('business_review', 'sales', 'operations', 'finance_readiness'):
        summary = await sales_summary(db, profile, now=now.replace(tzinfo=timezone.utc))
        evidence['sales'] = summary
        observations = [f"Completed revenue: {summary['currency']} {summary['revenue']:,.2f} across {summary['days']} calendar days.",
                        f"Recorded orders: {summary['orders']}; pending: {summary['pending_orders']}; refunded: {summary['refunded_orders']}."]
        if kind == 'finance_readiness':
            posted = await db.scalar(select(func.count()).select_from(BookEntry).where(BookEntry.business_profile_id == profile.id))
            evidence['bookkeeping_entries'] = posted
            observations.append(f'{posted} posted bookkeeping journals are available separately from the sales ledger.')
            limits.append('Sales alone cannot establish profit, tax or cash runway. Bookkeeping reports use posted journals only; bank feeds, tax rules and completeness are not independently verified.')
            if not posted:
                issues.append({'source_key': 'finance-inputs', 'title': 'Prepare opening balances and verified bookkeeping inputs',
                               'notes': 'Open Bookkeeping, record verified opening balances and income/expense journals, then reconcile the supplied bank closing balance. Do not infer financial health from sales alone.'})
        else:
            limits.append('Revenue is not profit or verified cash receipts; different currencies are not combined.')

    elif kind == 'bookkeeping_review':
        accounts = list(await db.scalars(select(BookAccount).where(BookAccount.business_profile_id == profile.id, BookAccount.is_cash.is_(True))))
        observations = [f'{len(accounts)} cash/bank accounts available for reconciliation review.']
        for account in accounts:
            latest = await db.scalar(select(func.max(BookEntry.day)).join(BookLine, BookLine.entry_id == BookEntry.id).where(BookEntry.business_profile_id == profile.id, BookLine.account_id == account.id))
            reconciled = await db.scalar(select(func.max(BookReconciliation.day)).where(BookReconciliation.business_profile_id == profile.id, BookReconciliation.account_id == account.id))
            if latest and (not reconciled or latest > reconciled):
                issues.append({'source_key': f'bank:{account.id}:{latest}:{reconciled}', 'title': f'Reconcile {account.name}'[:180],
                               'notes': f'Account {account.code} ({account.currency}) has postings through {latest}; last reconciled date: {reconciled or "none"}. Compare the supplied statement closing balance in Bookkeeping. No entry is posted automatically.'})
        if not accounts:
            issues.append({'source_key': 'bookkeeping-setup', 'title': 'Open the bookkeeping chart of accounts', 'notes': 'Set up accounts and record verified opening balances. Sales ledger revenue is not an accounting balance.'})
        limits.append('This is a reconciliation readiness check, not a bank feed, tax review or independent financial audit.')

    elif kind == 'people_review':
        pending = list(await db.scalars(select(LeaveRequest).where(LeaveRequest.business_profile_id == profile.id, LeaveRequest.status == 'pending')))
        overdue = list(await db.scalars(select(EmployeeTask).where(EmployeeTask.business_profile_id == profile.id, EmployeeTask.completed.is_(False), EmployeeTask.due_date < str(local_day))))
        observations = [f'{len(pending)} leave requests await review; {len(overdue)} employee tasks are overdue.']
        for request in pending:
            issues.append({'source_key': f'leave:{request.id}', 'title': 'Review a pending leave request', 'notes': f'Request {request.id}: {request.start_date} to {request.end_date}, {request.days} working days. Open People & HR to inspect employee availability. No private leave note is copied into this task; approval remains manual.'})
        for task in overdue:
            issues.append({'source_key': f'hr-task:{task.id}:{task.due_date}', 'title': 'Review an overdue employee task', 'notes': f'HR task {task.id} was due {task.due_date}. Open People & HR to review the assignment. No employee contact or sensitive notes are copied.'})
        limits.append('Owner-managed records only. No employee rating, payroll, statutory leave or automatic approval is inferred.')

    elif kind == 'lead_followup':
        rows = (await db.scalars(select(Lead).where(Lead.business_profile_id == profile.id, Lead.status.notin_(['won', 'lost'])).order_by(Lead.next_follow_up_at.asc(), Lead.id))).all()
        overdue = [row for row in rows if row.next_follow_up_at and row.next_follow_up_at <= now]
        evidence.update(open_leads=len(rows), overdue_count=len(overdue), unscheduled_count=sum(row.next_follow_up_at is None for row in rows))
        observations = [f'{len(rows)} open leads; {len(overdue)} due or overdue follow-ups.', f"{evidence['unscheduled_count']} open leads have no follow-up time."]
        for row in overdue:
            issues.append({'source_key': f'lead:{row.id}:{iso(row.next_follow_up_at)}', 'title': f'Follow up: {row.name}'[:180],
                           'notes': f'Lead ID: {row.id}. Stage: {row.status}. Follow-up due {iso(row.next_follow_up_at)}. Review the CRM record and choose the next contact action; no message has been sent.'})
        limits.append('No lead values or conversion probabilities are inferred. Won/lost leads are excluded; unscheduled is not overdue.')

    elif kind == 'fulfilment':
        rows = (await db.scalars(select(SalesTransaction).where(SalesTransaction.business_profile_id == profile.id, SalesTransaction.status == 'pending').order_by(SalesTransaction.transaction_date, SalesTransaction.id))).all()
        evidence['pending_count'] = len(rows)
        observations = [f'{len(rows)} ledger orders are pending.']
        for row in rows:
            reference = row.external_id or row.id
            issues.append({'source_key': f'order:{row.id}', 'title': f'Verify pending order {reference}'[:180],
                           'notes': f'Order ID: {row.id}; channel: {row.platform}; recorded: {iso(row.transaction_date)}; amount: {row.currency} {row.amount:.2f}. Verify payment and fulfilment before updating its ledger status.'})
        limits.append('Pending ledger status does not prove a courier delay, unpaid invoice or stock shortage. No order is changed.')

    elif kind == 'campaign_planner':
        rows = (await db.scalars(select(OwnerCampaign).where(OwnerCampaign.business_profile_id == profile.id, OwnerCampaign.status == 'draft').order_by(OwnerCampaign.scheduled_at, OwnerCampaign.id))).all()
        due = [row for row in rows if row.scheduled_at and row.scheduled_at <= now + timedelta(hours=48)]
        evidence.update(draft_count=len(rows), due_within_48_hours=len(due))
        observations = [f'{len(rows)} campaign drafts; {len(due)} planned within 48 hours or already past plan time.']
        for row in due:
            issues.append({'source_key': f'campaign:{row.id}:{iso(row.updated_at)}', 'title': f'Review campaign: {row.title}'[:180],
                           'notes': f'Campaign ID: {row.id}; channel: {row.platform}; planned {iso(row.scheduled_at)}. Review copy, claims and placement. Planned or approved content is not published by this portal.'})
        limits.append('Planning dates are internal reminders, not live platform schedules. Approved and archived campaigns are excluded.')

    elif kind == 'ad_efficiency':
        from app.api.v1.endpoints.ad_optimization import report
        report_data = await report(days=14, actor=profile.user_id, db=db)
        evidence['performance'] = report_data
        flagged = [item for item in report_data['items'] if item['state'] == 'review']
        observations = [f"{len(report_data['items'])} mature creative/attribution groups; {len(flagged)} require review.", f"Evidence window: {report_data['start']} to {report_data['end']} (conversion lag excluded)."]
        for item in flagged:
            identity = json.dumps([item[key] for key in ('platform', 'campaign', 'creative', 'currency', 'attribution')], ensure_ascii=False)
            issues.append({'source_key': 'ad:' + identity, 'title': f"Review ad efficiency: {item['creative']}"[:180],
                           'notes': f"{item['platform']} / {item['campaign']} / {item['creative']} / {item['currency']} / {item['attribution']}. " + ' '.join(item['notes'])})
        limits.append('Attributed reports are owner-supplied, not independently verified or randomized. No budget, bid or live campaign change is performed.')

    elif kind == 'creative_qa':
        rows = (await db.scalars(select(AdDraft).where(AdDraft.business_profile_id == profile.id, AdDraft.status == 'draft').order_by(AdDraft.updated_at.desc()))).all()
        evidence['draft_count'] = len(rows)
        observations = [f'{len(rows)} unapproved ad creatives inspected.']
        for row in rows:
            data = row.data or {}
            reasons = []
            if not data.get('headline', '').strip(): reasons.append('Missing headline')
            if not data.get('cta', '').strip(): reasons.append('Missing call to action')
            if (row.profile_snapshot or {}).get('channel') == 'Google' and len(data.get('headline', '')) > 30: reasons.append('Google search headline exceeds 30 characters')
            if re.search(r'\b(guaranteed|miracle|best)\b|\d+\s*%', data.get('headline', '') + ' ' + data.get('body', ''), re.I): reasons.append('Claim requires owner evidence review')
            if reasons:
                issues.append({'source_key': f'creative:{row.id}:{iso(row.updated_at)}', 'title': f"Review creative: {data.get('title', row.id)}"[:180], 'notes': f'Creative ID: {row.id}. ' + '; '.join(reasons) + '. Text checks do not assess image/video quality or approve this creative.'})
        observations.append(f'{len(issues)} creatives have text/readiness flags.')
        limits.append('Local rules are not legal certification, performance prediction or visual inspection.')

    elif kind in ('seo_readiness', 'research_quality'):
        doc_kind = 'seo' if kind == 'seo_readiness' else 'research'
        rows = (await db.scalars(select(WorkspaceDocument).where(WorkspaceDocument.business_profile_id == profile.id, WorkspaceDocument.kind == doc_kind).order_by(WorkspaceDocument.updated_at.desc()))).all()
        evidence['document_count'] = len(rows)
        observations = [f'{len(rows)} saved {doc_kind} documents inspected.']
        for row in rows:
            fields = row.fields or {}
            if doc_kind == 'seo':
                reasons = [label for key, label in [('page_title', 'Missing title'), ('description', 'Missing description')] if not fields.get(key, '').strip()]
                if not valid_url(fields.get('url')): reasons.append('Missing or invalid canonical URL')
                if len(fields.get('page_title', '')) > 60: reasons.append('Title exceeds the indicative 60-character display guideline')
            else:
                reasons = [label for key, label in [('source_title', 'Missing publisher/source title'), ('published_date', 'Missing publication date'), ('evidence', 'Missing observed evidence')] if not fields.get(key, '').strip()]
                if not valid_url(fields.get('source_url')): reasons.append('Missing or invalid source URL')
            if reasons:
                issues.append({'source_key': f'document:{row.id}:{iso(row.updated_at)}', 'title': f'Review {doc_kind}: {row.title}'[:180], 'notes': f'Document ID: {row.id}. ' + '; '.join(reasons) + '.'})
        if not rows:
            issues.append({'source_key': f'no-{doc_kind}-documents', 'title': f'Create the first {doc_kind} evidence record', 'notes': 'No saved source documents are available. Capture real inputs before requesting conclusions.'})
        limits.append('This checks saved inputs only. No live crawl, source verification, search ranking or market-size estimate is claimed.')

    elif kind == 'execution_coach':
        rows = (await db.scalars(select(OwnerTask).where(OwnerTask.business_profile_id == profile.id, OwnerTask.status != 'done').order_by(OwnerTask.created_at))).all()
        due = [row for row in rows if row.due_date and row.due_date < str(local_day)]
        unassigned = [row for row in rows if not row.owner.strip()]
        evidence.update(open_actions=len(rows), overdue_count=len(due), unassigned_count=len(unassigned))
        observations = [f'{len(rows)} open actions; {len(due)} overdue; {len(unassigned)} unassigned.']
        # One aggregate review avoids recursive tasks about automation-created tasks.
        if due or unassigned:
            issues.append({'source_key': 'execution-review', 'title': 'Review overdue and unassigned owner actions', 'notes': f'{len(due)} overdue and {len(unassigned)} unassigned open actions as of {local_day}. Reassign or update realistic deadlines; completed work is excluded.'})
        limits.append('An internal due date is not a customer SLA. No action status is changed automatically.')

    else:
        evidence['sales'] = await sales_summary(db, profile, now=now.replace(tzinfo=timezone.utc))
        doc_kind = 'strategy' if kind == 'strategy' else 'ideation' if kind == 'ideation' else None
        if doc_kind:
            rows = (await db.scalars(select(WorkspaceDocument).where(WorkspaceDocument.business_profile_id == profile.id, WorkspaceDocument.kind == doc_kind).order_by(WorkspaceDocument.updated_at.desc()).limit(5))).all()
            evidence['documents'] = [{'id': row.id, 'title': row.title, 'fields': row.fields} for row in rows]

    evidence['observations'] = observations
    evidence['issues'] = issues
    evidence['issue_count'] = len(issues)
    evidence['limits'] = limits
    return evidence


def rules_output(kind, objective, context, evidence):
    skill = advisor_catalog()[kind]
    if kind in ('business_review', 'sales', 'operations'):
        content = ledger_brief(kind, objective, context, evidence['sales'])
    else:
        lines = [f"{context['company_name']} — {skill['title']}", f'Objective: {objective}',
                 f"Evidence as of {evidence['as_of']} ({context['timezone']})", '', 'Observed evidence:']
        lines.extend('- ' + text for text in evidence['observations'])
        lines += ['', 'Owner review queue:']
        lines.extend(f"- {issue['title']}: {issue['notes']}" for issue in evidence['issues'][:20])
        if not evidence['issues']: lines.append('- No review flags in the available records. This does not establish completeness of external systems.')
        if evidence['issue_count'] > 20: lines.append(f"- {evidence['issue_count'] - 20} additional flags; inspect the source workspace.")
        lines += ['', 'Limits:'] + ['- ' + text for text in evidence['limits']]
        content = '\n'.join(lines)
    return content + f"\n\nSkill: {skill['name']} v{skill['version']}. Execution: deterministic evidence checks. No external action taken."
