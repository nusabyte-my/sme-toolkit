"""Persistent evidence automations. Only internal tasks and deterministic advisor briefs."""
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from app.database import (AutomationRule, AutomationRun, AutomationAction, BusinessProfile,
                          OwnerTask, OwnerAgentRun, async_session_maker)
from app.services.advisors import advisor_catalog, advisor_evidence, rules_output
from app.services.owner_service import context_data, iso

logger = logging.getLogger(__name__)
TEMPLATES = {
    'owner_brief': {'name': 'Owner briefing', 'advisor': 'business_review', 'interval_hours': 24, 'output': 'brief',
                    'description': 'Save a fresh evidence brief from the recorded sales ledger; no AI call or external message.'},
    'lead_followup': {'name': 'Overdue lead follow-ups', 'advisor': 'lead_followup', 'interval_hours': 6, 'output': 'tasks',
                      'description': 'Create one review task per overdue open lead and follow-up timestamp.'},
    'pending_orders': {'name': 'Pending-order verification', 'advisor': 'fulfilment', 'interval_hours': 24, 'output': 'tasks',
                       'description': 'Create one verification task per pending order; never change payment or delivery status.'},
    'campaign_review': {'name': 'Campaign review reminders', 'advisor': 'campaign_planner', 'interval_hours': 24, 'output': 'tasks',
                        'description': 'Flag unreviewed campaigns planned within 48 hours or already past their planned time.'},
    'ad_efficiency': {'name': 'Ad efficiency review', 'advisor': 'ad_efficiency', 'interval_hours': 24, 'output': 'tasks',
                      'description': 'Use mature attributed reports and your thresholds; create review tasks, never change spend.'},
    'creative_qa': {'name': 'Creative preflight', 'advisor': 'creative_qa', 'interval_hours': 24, 'output': 'tasks',
                    'description': 'Flag missing copy, Google headline limits and claim-review needs in unapproved creatives.'},
    'execution_review': {'name': 'Execution follow-through', 'advisor': 'execution_coach', 'interval_hours': 24, 'output': 'tasks',
                         'description': 'Create one aggregate review for overdue or unassigned owner actions, not recursive alerts.'},
    'seo_review': {'name': 'SEO metadata readiness', 'advisor': 'seo_readiness', 'interval_hours': 168, 'output': 'tasks',
                   'description': 'Review saved metadata for missing titles, descriptions and canonical URLs; no live crawl.'},
    'research_review': {'name': 'Research evidence hygiene', 'advisor': 'research_quality', 'interval_hours': 168, 'output': 'tasks',
                        'description': 'Find research documents missing sources, dates or evidence without inventing market facts.'},
    'finance_readiness': {'name': 'Finance evidence readiness', 'advisor': 'finance_readiness', 'interval_hours': 168, 'output': 'tasks',
                          'description': 'Remind the owner to collect cost and cash inputs; recorded revenue is not profit.'},
    'bookkeeping_review': {'name': 'Bookkeeping reconciliation review', 'advisor': 'bookkeeping_review', 'interval_hours': 168, 'output': 'tasks',
                           'description': 'Flag cash/bank postings beyond the last reconciliation; never post or move money.'},
    'people_review': {'name': 'People and leave review', 'advisor': 'people_review', 'interval_hours': 24, 'output': 'tasks',
                      'description': 'Flag pending leave and overdue HR tasks without exposing private notes or approving requests.'},
}


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def schedule_slot(now, interval_hours):
    seconds = interval_hours * 3600
    bucket = int(now.replace(tzinfo=timezone.utc).timestamp()) // seconds
    next_run = datetime.fromtimestamp((bucket + 1) * seconds, timezone.utc).replace(tzinfo=None)
    return f'{interval_hours}:{bucket}', next_run


def rule_data(row):
    return {key: getattr(row, key) for key in ('id', 'template_key', 'enabled', 'interval_hours', 'last_status')} | {
        'next_run_at': iso(row.next_run_at), 'last_run_at': iso(row.last_run_at), 'created_at': iso(row.created_at)}


def log_data(row):
    return {key: getattr(row, key) for key in ('id', 'rule_id', 'slot', 'status', 'summary', 'task_ids', 'advisor_run_id')} | {'created_at': iso(row.created_at)}


async def preview_rule(db, profile, template_key, now=None):
    template = TEMPLATES[template_key]
    evidence = await advisor_evidence(db, profile, template['advisor'], now=now)
    return {'template': template, 'evidence': evidence,
            'proposed_actions': evidence['issues'][:100],
            'notice': 'Preview only. No tasks, advisor runs or external actions created.'}


async def run_rule(db, rule_id, profile_id, force=False, now=None):
    """Claim and commit a cadence slot plus all outputs atomically; process death rolls it back."""
    now = now or utc_now()
    if now.tzinfo is not None:
        now = now.astimezone(timezone.utc).replace(tzinfo=None)
    rule = await db.scalar(select(AutomationRule).where(AutomationRule.id == rule_id, AutomationRule.business_profile_id == profile_id))
    if not rule or not rule.enabled:
        return {'status': 'paused', 'summary': 'Rule is paused or missing.'}
    if not force and rule.next_run_at > now:
        return {'status': 'not_due', 'summary': 'The next scheduled check is not due.'}
    slot, next_run = schedule_slot(now, rule.interval_hours)
    previous = await db.scalar(select(AutomationRun).where(AutomationRun.rule_id == rule.id, AutomationRun.slot == slot))
    if previous:
        existing_log = log_data(previous)
        if rule.next_run_at <= now:
            rule.next_run_at = next_run
            await db.commit()
        return {'status': 'already_checked', 'summary': 'This cadence slot was already checked. Preview remains available.', 'run': existing_log}
    expected_due = rule.next_run_at
    claim = await db.execute(update(AutomationRule).where(
        AutomationRule.id == rule.id, AutomationRule.business_profile_id == profile_id,
        AutomationRule.enabled.is_(True), AutomationRule.next_run_at == expected_due,
    ).values(next_run_at=next_run, updated_at=now))
    if not claim.rowcount:
        await db.rollback()
        return {'status': 'already_checked', 'summary': 'Another worker already claimed this check.'}
    # The update lock serializes concurrent manual checks even when next_run_at remains identical.
    previous = await db.scalar(select(AutomationRun).where(AutomationRun.rule_id == rule.id, AutomationRun.slot == slot))
    if previous:
        existing_log = log_data(previous)
        await db.rollback()
        return {'status': 'already_checked', 'summary': 'This cadence slot was already checked.', 'run': existing_log}
    profile = await db.scalar(select(BusinessProfile).where(BusinessProfile.id == profile_id))
    template = TEMPLATES[rule.template_key]
    skill = advisor_catalog()[template['advisor']]
    evidence = await advisor_evidence(db, profile, template['advisor'], now=now)
    task_ids = []
    skipped = 0
    advisor_run_id = None
    if template['output'] == 'brief':
        context = context_data(profile)
        row = OwnerAgentRun(business_profile_id=profile_id, kind=template['advisor'], objective=skill['default_objective'],
                            status='needs_review', provider='rules',
                            output=rules_output(template['advisor'], skill['default_objective'], context, evidence),
                            context_snapshot={**context, '_advisor': {'name': skill['name'], 'version': skill['version'], 'mode': 'rules'}, '_evidence': {**evidence, 'issues': evidence['issues'][:100]}})
        db.add(row)
        await db.flush()
        advisor_run_id = row.id
        summary = 'Saved one deterministic owner briefing for review. No paid AI request or external message.'
    else:
        for issue in evidence['issues']:
            source_key = hashlib.sha256(issue['source_key'].encode('utf-8')).hexdigest()
            existing = await db.scalar(select(AutomationAction).where(AutomationAction.rule_id == rule.id, AutomationAction.source_key == source_key))
            if existing:
                skipped += 1
                continue
            task = OwnerTask(business_profile_id=profile_id, title=issue['title'][:180],
                             notes=(f"Automation: {template['name']}. Skill: {skill['name']} v{skill['version']}.\n" + issue['notes'])[:4000],
                             owner='', status='open')
            db.add(task)
            await db.flush()
            db.add(AutomationAction(rule_id=rule.id, source_key=source_key, task_id=task.id))
            task_ids.append(task.id)
            if len(task_ids) >= 100:
                break
        summary = f"Created {len(task_ids)} internal review tasks; {skipped} previously raised source issues skipped. {evidence['issue_count']} evidence flags."
        if len(task_ids) >= 100 and evidence['issue_count'] > skipped + len(task_ids):
            summary += ' Batch limit reached; remaining unraised issues are eligible at the next cadence check.'
    status = 'completed' if task_ids or advisor_run_id else 'no_action'
    log = AutomationRun(rule_id=rule.id, business_profile_id=profile_id, slot=slot, status=status,
                        summary=summary, task_ids=task_ids, advisor_run_id=advisor_run_id, created_at=now)
    db.add(log)
    rule.last_run_at = now
    rule.last_status = status
    await db.commit()
    await db.refresh(log)
    return {'status': status, 'summary': summary, 'run': log_data(log)}


async def check_due_rules(session_factory=async_session_maker, now=None):
    now = now or utc_now()
    async with session_factory() as db:
        due = (await db.execute(select(AutomationRule.id, AutomationRule.business_profile_id).where(
            AutomationRule.enabled.is_(True), AutomationRule.next_run_at <= now,
        ).order_by(AutomationRule.next_run_at).limit(100))).all()
    results = []
    for rule_id, profile_id in due:
        async with session_factory() as db:
            try:
                results.append(await run_rule(db, rule_id, profile_id, now=now))
            except Exception:
                await db.rollback()
                logger.exception('Automation check failed for rule %s', rule_id)
                # A failed slot is visible, not reported as success or retried in a tight loop.
                rule = await db.scalar(select(AutomationRule).where(AutomationRule.id == rule_id, AutomationRule.enabled.is_(True)))
                if rule:
                    slot, next_run = schedule_slot(now, rule.interval_hours)
                    found = await db.scalar(select(AutomationRun.id).where(AutomationRun.rule_id == rule_id, AutomationRun.slot == slot))
                    if not found:
                        rule.next_run_at = next_run
                        rule.last_run_at = now
                        rule.last_status = 'failed'
                        db.add(AutomationRun(rule_id=rule_id, business_profile_id=profile_id, slot=slot, status='failed',
                                             summary='Check failed. No partial tasks committed. Review server logs and retry in the next cadence slot.', task_ids=[], created_at=now))
                        try:
                            await db.commit()
                        except Exception:
                            await db.rollback()
                            logger.exception('Could not persist automation failure for rule %s', rule_id)
                results.append({'status': 'failed'})
    return results


async def automation_loop(poll_seconds=60):
    while True:
        try:
            await check_due_rules()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception('Automation scheduler tick failed')
        await asyncio.sleep(poll_seconds)
