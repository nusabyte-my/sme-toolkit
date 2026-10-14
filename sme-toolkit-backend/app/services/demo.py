"""Fictional enterprise records, isolated under a fresh demo actor. Never seed real accounts."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from pathlib import Path
from sqlalchemy import select

from app.database import (BusinessProfile, SalesTransaction, Lead, OwnerCampaign,
                          WorkspaceDocument, OwnerTask, AdProfile, AdDraft, AdPerformance,
                          OwnerAgentRun, AutomationRule, AdAsset, BookAccount, Employee, EmployeeTask, LeaveRequest, BillingCustomer, BusinessAgent, AgentConversation, AgentMessage)
from app.schemas.creative_editor import EditorFields, VideoScene
from app.services.advisors import advisor_catalog, advisor_evidence, rules_output
from app.services.owner_service import context_data
from app.agents.workflow_engine import TEMPLATES


async def seed_demo(db):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    actor = 'demo-' + str(uuid4())
    context = dict(company_name='Meranti Supply Co.', industry='Retail & wholesale · demo enterprise',
                   business_description='Fictional Malaysian business selling reusable drinkware to shoppers and workplace buyers. Every record is illustrative, not a real customer or trading result.',
                   products_services='Everyday Flask — MYR 89; Desk Set — MYR 149; Team Welcome Kit — MYR 249. Sample catalog for this demonstration.',
                   target_market='Urban shoppers, office managers and corporate-gifting buyers in Malaysia.',
                   brand_voice='Practical, warm and specific. English with familiar Malaysian phrasing. No environmental certifications or performance claims without evidence.',
                   goals='Review overdue corporate enquiries; reconcile pending orders; test the Team Welcome Kit campaign before increasing spend.',
                   currency='MYR', timezone='Asia/Kuala_Lumpur', website='https://meranti.example',
                   proof_points='Demonstration only. No real testimonials, certifications or delivery guarantees.',
                   constraints='Sample data only. No live marketplace connection, publishing, outbound contact or paid AI generation in the demo.')
    profile = BusinessProfile(user_id=actor, company_name=context['company_name'], industry=context['industry'],
                              website=context['website'], meta_json={'owner_context': context, 'demo': True,
                              'ad_targets': {'target_cpa': 35, 'target_roas': 3, 'min_impressions': 1000,
                                             'min_conversions': 10, 'conversion_lag_days': 3}})
    db.add(profile)
    await db.flush()
    pid = profile.id
    for day in range(60):
        for channel_index, channel in enumerate(('manual', 'shopee', 'lazada')):
            quantity = 1 + (day + channel_index) % 4
            price = (89, 149, 249)[(day + channel_index) % 3]
            state = 'pending' if day < 3 and channel_index == 0 else 'refunded' if day in (9, 23) and channel_index == 1 else 'completed'
            db.add(SalesTransaction(business_profile_id=pid, platform=channel,
                    external_id=f'DEMO-{day:02d}-{channel_index}', amount=quantity * price, currency='MYR', status=state,
                    product_details={'demo': True, 'quantity': quantity, 'unit_price': price},
                    transaction_date=now-timedelta(days=day, hours=1)))
    for index, (name, company, state, hours) in enumerate([
        ('Aina · sample buyer', 'Studio Pagi (fictional)', 'proposal', -26),
        ('Daniel · sample buyer', 'Northline Works (fictional)', 'qualified', -5),
        ('Mei · sample buyer', 'Orchard Team (fictional)', 'contacted', 20),
        ('Farah · sample buyer', 'Ruang Office (fictional)', 'new', None),
        ('Kumar · sample buyer', 'Fieldwork Co. (fictional)', 'won', -72),
        ('Sofia · sample buyer', 'Gather House (fictional)', 'lost', None),
    ]):
        db.add(Lead(business_profile_id=pid, name=name, email=f'buyer{index}@meranti.example', company=company,
                    status=state, lead_source='Demo corporate-gifting enquiry',
                    notes='Fictional enquiry for 40 Team Welcome Kits. Confirm quantity, artwork and delivery date. Do not contact.',
                    next_follow_up_at=now+timedelta(hours=hours) if hours is not None else None))
    for title, channel, state, hours in [
        ('Team Welcome Kit launch · sample', 'LinkedIn', 'draft', 24),
        ('Everyday carry, fewer loose ends · sample', 'Instagram', 'approved', 48),
        ('Desk Set product story · sample', 'TikTok', 'draft', -12),
    ]:
        db.add(OwnerCampaign(business_profile_id=pid, title=title, platform=channel, status=state,
                            caption='Sample campaign: Meet the Meranti Team Welcome Kit. Flask, desk essentials and a welcome note in one considered set. Request the kit details. Demonstration copy only.',
                            scheduled_at=now+timedelta(hours=hours)))
    documents = [
        ('canvas', 'Meranti operating model · sample', {
            'partners': 'Sample packaging supplier; local fulfilment partner; corporate buyers.',
            'activities': 'Source drinkware, prepare bundles, qualify enquiries, fulfil verified orders.',
            'resources': 'Product catalog, sample creative library, sales ledger and owner review queue.',
            'value': 'Useful daily essentials packaged for individual shoppers and workplace welcome kits.',
            'relationships': 'Product support for shoppers; consultative follow-up for team orders.',
            'channels': 'Retail counter, marketplace exports and direct corporate enquiries. No live sync in demo.',
            'customers': 'Urban shoppers; office managers; corporate-gifting buyers.',
            'costs': 'Collect real product, packaging, labour and delivery costs before evaluating margin.',
            'revenue': 'Individual flasks, desk bundles and team welcome kits. Figures in this workspace are synthetic.'}),
        ('strategy', 'Choose the next channel test · sample', {
            'goal': 'Test corporate-gifting demand without committing to a large production run.',
            'baseline': 'Illustrative leads and sales only; no real baseline is established.',
            'target': 'Pilot with five qualified buyers; owner must validate this target.',
            'deadline': str((now+timedelta(days=14)).date()), 'constraints': 'No proven acquisition cost or gross margin yet.',
            'options': 'A: corporate pilot with direct follow-up. B: broad paid launch with higher evidence and budget requirements.',
            'decision': 'Pilot first; reconcile costs before approving scale.', 'evidence': 'Sample CRM pipeline and attributed campaign reports, not market proof.',
            'next_action': 'Review Aina’s sample enquiry, prepare a quote checklist and assign follow-up.'}),
        ('ideation', 'Refill reminder insert · sample', {
            'problem': 'A new flask may be left unused after onboarding.', 'audience': 'New team members receiving welcome kits.',
            'idea': 'Include a simple desk reminder card with the kit.', 'benefit': 'Make the product’s daily use obvious.',
            'assumptions': 'Recipients want a physical reminder. Not validated.', 'experiment': 'Show two card concepts to five consenting pilot users.',
            'metric': 'Record preference and reasons; no conversion claim from this small qualitative sample.', 'decision': 'Draft concept; collect evidence before production.'}),
        ('seo', 'Team Welcome Kit page · sample', {
            'page_title': 'Team Welcome Kits | Meranti Supply Co.',
            'description': 'Explore a practical welcome kit for your team: reusable drinkware, desk essentials and a personal note. Request product details.',
            'url': 'https://meranti.example/team-welcome-kit', 'business_name': 'Meranti Supply Co. (fictional)',
            'business_type': 'Retail and corporate gifting', 'keywords': 'team welcome kit, office gifting',
            'content_outline': 'Product contents; options; quote requirements; shipping questions. Demo metadata, not a live page.'}),
        ('research', 'Corporate buyer interview plan · sample', {
            'question': 'Which details block a corporate buyer from requesting a quote?', 'segment': 'Office managers arranging welcome kits.',
            'source_url': '', 'source_title': 'Planned interviews — no published source yet', 'published_date': '',
            'evidence': '', 'assumptions': 'Quantity, budget and delivery timing may be key. These are hypotheses, not findings.',
            'conclusion': 'Interview buyers before claiming market demand. Run Research Quality to expose the missing evidence.'}),
    ]
    for kind, title, fields in documents:
        db.add(WorkspaceDocument(business_profile_id=pid, kind=kind, title=title, fields=fields))
    for title, owner, status, days in [
        ('Review Team Welcome Kit quote requirements · sample', 'Aina / Sales (fictional)', 'open', -1),
        ('Reconcile pending retail orders · sample', 'Daniel / Operations (fictional)', 'in_progress', 0),
        ('Check campaign claims before approval · sample', '', 'open', 2),
    ]:
        db.add(OwnerTask(business_profile_id=pid, title=title, owner=owner, status=status,
                        due_date=str((now+timedelta(days=days)).date()), notes='Demo action. Internal review only; no message or payment is triggered.'))
    ad_data = dict(name='Team Welcome Kit · sample profile', product='Team Welcome Kit — sample price MYR 249',
                   offer='Reusable flask, desk essentials and a welcome note. Illustrative catalog only.',
                   audience=context['target_market'], voice=context['brand_voice'], channel='Meta', cta='Explore the kit',
                   landing_url='https://meranti.example/team-welcome-kit', language='English',
                   prohibited_claims='No invented reviews, certifications, discounts or guaranteed outcomes.', brand_color='#7C3AED')
    ad_profile = AdProfile(business_profile_id=pid, data=ad_data)
    db.add(ad_profile)
    artwork = AdAsset(business_profile_id=pid, name='Meranti typography · sample artwork.png', mime='image/png',
                      content=(Path(__file__).resolve().parents[2] / 'assets' / 'meranti-demo.png').read_bytes())
    db.add(artwork)
    await db.flush()
    for title, headline, body, ratio in [
        ('Team Welcome Kit · sample creative', 'A considered welcome.', 'A flask. Desk essentials. A personal note. Build a welcome kit your team can make their own. Sample creative — fictional products.', '1:1'),
        ('Everyday carry · sample creative', 'Make room for the everyday.', 'Useful drinkware for the desk, the commute and the next meeting. Demonstration copy only.', '9:16'),
    ]:
        editor = EditorFields(scenes=[VideoScene(id='welcome', caption=headline, duration=3, asset_id=artwork.id),
                                     VideoScene(id='contents', caption='Flask. Desk essentials. A welcome note.', duration=3, transition='fade', asset_id=artwork.id),
                                     VideoScene(id='action', caption='Explore the kit · sample campaign', duration=3, transition='fade', asset_id=artwork.id)],
                              copy_variants=[body, 'A practical first-day welcome. Explore the Team Welcome Kit. Sample copy.']).model_dump()
        db.add(AdDraft(business_profile_id=pid, profile_id=ad_profile.id, profile_snapshot=ad_data, status='draft',
                       data={**editor, 'title': title, 'headline': headline, 'body': body, 'cta': 'Explore the kit',
                             'image_prompt': 'Owner-authored sample: typographic welcome-kit campaign. No product photo or AI generation is claimed.',
                             'video_prompt': 'Owner-authored sample: a three-scene welcome-kit story.',
                             'script': 'Introduce the kit. Show the contents. Invite a product enquiry.',
                             'aspect_ratio': ratio, 'duration': 9, 'asset_id': artwork.id, 'video_asset_id': None}))
    for day in range(3, 31):
        for creative, clicks, conversions, spend, revenue in [
            ('Kit contents · sample', 80, 4, 9000, 99600), ('Broad gifting · sample', 30, 1, 12000, 24900),
        ]:
            db.add(AdPerformance(business_profile_id=pid, day=str((now+timedelta(hours=8)-timedelta(days=day)).date()),
                        platform='Meta', campaign='Team Welcome Kit · sample', creative=creative, currency='MYR',
                        attribution='7-day click · synthetic', impressions=2000, clicks=clicks, conversions=conversions,
                        spend_cents=spend, revenue_cents=revenue))
    for key, template in TEMPLATES.items():
        db.add(AutomationRule(business_profile_id=pid, template_key=key, enabled=False,
                              interval_hours=template['interval_hours'], next_run_at=now))
    await db.flush()
    from app.api.v1.endpoints.bookkeeping import setup_accounts, post_journal, JournalInput
    await setup_accounts(db, profile)
    books = {row.code: row for row in await db.scalars(select(BookAccount).where(BookAccount.business_profile_id == pid))}
    for ref, memo, debit, credit, amount in [
        ('DEMO-OPEN','Sample owner capital','1000','3000','10000.00'),
        ('DEMO-RECEIPT','Sample direct customer receipt','1000','4000','2400.00'),
        ('DEMO-COST','Sample inventory cost consumed','5000','1000','850.00'),
        ('DEMO-RENT','Sample operating expense','6000','1000','400.00'),
    ]:
        await post_journal(db, profile, actor, JournalInput(day=now.date(), reference=ref, memo=memo,
            lines=[{'account_id':books[debit].id,'debit':amount},{'account_id':books[credit].id,'credit':amount}]))
    people=[]
    for index, (name,department,role,status) in enumerate([
        ('Aina · sample employee','Sales','Sales lead','active'),('Daniel · sample employee','Operations','Operations coordinator','active'),
        ('Mei · sample employee','Marketing','Creative producer','onboarding'),
    ]):
        employee=Employee(business_profile_id=pid,code=f'DEMO-E{index+1}',name=name,email=f'employee{index+1}@meranti.example',
                          department=department,job_title=role,start_date=str((now-timedelta(days=30)).date()),status=status,annual_leave_days=18)
        db.add(employee);people.append(employee)
    await db.flush()
    people[2].manager_id=people[1].id
    due=(now+timedelta(days=3)).date()
    while due.weekday()>4: due+=timedelta(days=1)
    db.add(LeaveRequest(business_profile_id=pid,employee_id=people[0].id,start_date=str(due),end_date=str(due),days=1,kind='annual',note='Sample annual leave request. No real employee data.',status='pending'))
    db.add(EmployeeTask(business_profile_id=pid,employee_id=people[2].id,title='Prepare creative workstation · sample',due_date=str((now-timedelta(days=1)).date())))
    await db.flush()
    from app.api.v1.endpoints.billing import create_document_record, DocumentInput
    customer=BillingCustomer(business_profile_id=pid,name='Studio Pagi (fictional)',email='buyer@meranti.example',address='Sample billing address, Kuala Lumpur',registration_number='DEMO-ONLY')
    db.add(customer);await db.flush()
    await create_document_record(db,profile,DocumentInput(kind='quotation',customer_id=customer.id,day=now.date(),due_date=(now+timedelta(days=30)).date(),
        lines=[{'description':'Team Welcome Kit — fictional sample','quantity':'10','unit_price':'249.00','discount':'0','tax_percent':'0'}],notes='Sample quotation only. No real customer commitment.',terms='Owner to confirm delivery and payment instructions.'))
    agent=BusinessAgent(business_profile_id=pid,name='Meranti sales desk',instructions='Review recorded sales and invoice status. Propose owner follow-ups; never contact customers or issue invoices without review.',
        tools=['sales_summary','billing_summary','advisor_review','propose_task'],public_context='Meranti Supply Co. is fictional. This demonstration sells sample welcome kits; ask the owner for verified product and delivery details.',enabled=True,interval_hours=0,schedule_prompt='')
    db.add(agent);await db.flush()
    conversation=AgentConversation(business_profile_id=pid,agent_id=None,title='Build your next agent',builder_state={})
    db.add(conversation);await db.flush()
    db.add(AgentMessage(conversation_id=conversation.id,role='assistant',content='Start with /create to build an agent through guided chat. Review its tools before approving. Select Meranti sales desk and send /run to inspect sample evidence. No paid AI or external messaging is enabled in this demo.',trace=[]))
    for kind in ('business_review', 'lead_followup', 'ad_efficiency'):
        skill = advisor_catalog()[kind]
        evidence = await advisor_evidence(db, profile, kind, now=now)
        snapshot = context_data(profile)
        db.add(OwnerAgentRun(business_profile_id=pid, kind=kind, objective=skill['default_objective'],
                            status='needs_review', provider='rules',
                            output='DEMO — findings calculated from synthetic records.\n\n'+rules_output(kind, skill['default_objective'], snapshot, evidence),
                            context_snapshot={**snapshot, '_advisor': {k: skill[k] for k in ('name','version','mode')}, '_evidence': evidence}))
    await db.commit()
    return actor
