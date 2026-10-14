"""Owner-scoped quotes/invoices with exact totals, immutable issue snapshots and ledger handoff."""
import html
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal
from zoneinfo import ZoneInfo
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.auth import get_current_user
from app.database import get_db, BillingCustomer, CommercialDocument, InvoicePayment, BookAccount, BookEntry, BookLine
from app.services.owner_service import business, context_data, iso
from app.api.v1.endpoints.bookkeeping import lock_books, setup_accounts, post_journal, JournalInput, LineInput

router = APIRouter()


class CustomerInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=160)
    email: str = Field(default='', max_length=254)
    address: str = Field(default='', max_length=1000)
    registration_number: str = Field(default='', max_length=80)

    @field_validator('email')
    @classmethod
    def email_format(cls, value):
        if value and ('@' not in value or any(c.isspace() for c in value)):
            raise ValueError('Enter a valid customer email or leave it blank')
        return value


class ItemInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(gt=0, le=1000000, max_digits=10, decimal_places=3, allow_inf_nan=False)
    unit_price: Decimal = Field(ge=0, le=9999999, max_digits=9, decimal_places=2, allow_inf_nan=False)
    discount: Decimal = Field(default=0, ge=0, le=999999999, max_digits=11, decimal_places=2, allow_inf_nan=False)
    tax_percent: Decimal = Field(default=0, ge=0, le=100, max_digits=5, decimal_places=2, allow_inf_nan=False)


class DocumentInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    kind: Literal['quotation','invoice']
    customer_id: str = Field(min_length=1, max_length=50)
    day: date
    due_date: date
    lines: list[ItemInput] = Field(min_length=1, max_length=100)
    notes: str = Field(default='', max_length=4000)
    terms: str = Field(default='', max_length=4000)
    version: int | None = Field(default=None, ge=1)

    @model_validator(mode='after')
    def valid_dates(self):
        if self.due_date < self.day: raise ValueError('Due or valid-until date cannot precede the document date')
        return self


class DecisionInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    action: Literal['issue','accept','decline','void','convert']
    note: str = Field(default='', max_length=1000)
    day: date | None = None


class PaymentInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    day: date
    reference: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, le=999999999, max_digits=11, decimal_places=2, allow_inf_nan=False)
    account_id: str = Field(min_length=1, max_length=50)


class PaymentReverseInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    day: date
    reason: str = Field(min_length=3, max_length=500)


def local_today(profile):
    return datetime.now(ZoneInfo(context_data(profile)['timezone'])).date()


def customer_data(row):
    return {k:getattr(row,k) for k in ('id','name','email','address','registration_number')}


def totals(items):
    lines=[]
    for item in items:
        gross=int((item.quantity*item.unit_price*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
        discount=int(item.discount*100)
        if discount > gross: raise HTTPException(422, 'A line discount cannot exceed its rounded line amount.')
        net=gross-discount
        tax=int((Decimal(net)*item.tax_percent/100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
        lines.append({'description':item.description,'quantity':str(item.quantity),'unit_price_cents':int(item.unit_price*100),
                      'gross_cents':gross,'discount_cents':discount,'tax_percent':str(item.tax_percent),'tax_cents':tax,'total_cents':net+tax})
    subtotal=sum(l['gross_cents'] for l in lines);discount=sum(l['discount_cents'] for l in lines);tax=sum(l['tax_cents'] for l in lines)
    total=subtotal-discount+tax
    if total <= 0 or total > 99999999900: raise HTTPException(422, 'Document total must be positive and no more than 999,999,999.00.')
    return dict(lines=lines,subtotal_cents=subtotal,discount_cents=discount,tax_cents=tax,total_cents=total)


async def owned(db, profile, document_id):
    row=await db.scalar(select(CommercialDocument).where(CommercialDocument.id==document_id,CommercialDocument.business_profile_id==profile.id).execution_options(populate_existing=True))
    if not row: raise HTTPException(404,'Document not found in this business.')
    return row


async def create_document_record(db, profile, data):
    await lock_books(db,profile)
    customer=await db.scalar(select(BillingCustomer).where(BillingCustomer.id==data.customer_id,BillingCustomer.business_profile_id==profile.id))
    if not customer: raise HTTPException(404,'Customer not found in this business.')
    sequence=1+(await db.scalar(select(func.coalesce(func.max(CommercialDocument.sequence),0)).where(CommercialDocument.business_profile_id==profile.id,CommercialDocument.kind==data.kind,CommercialDocument.year==data.day.year)))
    number=f"{'QUO' if data.kind=='quotation' else 'INV'}-{data.day.year}-{sequence:05d}"
    context=context_data(profile)
    meta=profile.meta_json or {}
    seller_address=', '.join(part for part in [profile.city, profile.country] if part)
    seller_reg=str(meta.get('registration_number') or (meta.get('owner_context') or {}).get('registration_number') or '').strip()
    seller_snapshot={
        'name':profile.company_name,
        'website':profile.website or '',
        'email':profile.contact_email or '',
        'address':seller_address,
        'registration_number':seller_reg,
        'logo_data_url':(context.get('logo_data_url') if context else '') or '',
        'demo':bool(meta.get('demo')),
    }
    row=CommercialDocument(business_profile_id=profile.id,customer_id=customer.id,kind=data.kind,number=number,sequence=sequence,year=data.day.year,
                           status='draft',day=str(data.day),due_date=str(data.due_date),currency=context['currency'],
                           seller=seller_snapshot,
                           customer=customer_data(customer),notes=data.notes,terms=data.terms,**totals(data.lines))
    db.add(row);await db.flush()
    return row


async def paid_amount(db, document_id):
    return int(await db.scalar(select(func.coalesce(func.sum(InvoicePayment.amount_cents),0)).where(InvoicePayment.document_id==document_id,InvoicePayment.reversal_id.is_(None))))


def document_data(row, paid=0):
    return {k:getattr(row,k) for k in ('id','kind','number','status','day','due_date','currency','seller','customer','customer_id','lines','subtotal_cents','discount_cents','tax_cents','total_cents','notes','terms','decision_note','source_quote_id','journal_id','version')} | {'paid_cents':paid,'balance_cents':row.total_cents-paid,'created_at':iso(row.created_at)}


async def commit(db):
    try: await db.commit()
    except IntegrityError:
        await db.rollback();raise HTTPException(409,'This reference or document action already exists. Refresh before trying again.')


async def billing_accounts(db,profile,currency):
    await setup_accounts(db,profile)
    accounts={a.code:a for a in await db.scalars(select(BookAccount).where(BookAccount.business_profile_id==profile.id,BookAccount.currency==currency))}
    if not all(code in accounts for code in ('1100','4000')) or accounts['1100'].kind!='asset' or accounts['4000'].kind!='income':
        raise HTTPException(409,'Bookkeeping needs accounts 1100 (receivable/asset) and 4000 (sales/income) in this document currency.')
    if '2100' not in accounts:
        exists=await db.scalar(select(BookAccount.id).where(BookAccount.business_profile_id==profile.id,BookAccount.code=='2100'))
        if exists: raise HTTPException(409,'Tax account 2100 uses another currency; configure the books before issuing.')
        account=BookAccount(business_profile_id=profile.id,code='2100',name='Tax payable',kind='liability',currency=currency,is_cash=False)
        db.add(account);await db.flush();accounts['2100']=account
    if accounts['2100'].kind!='liability': raise HTTPException(409,'Tax account 2100 must be a liability.')
    return accounts


async def reverse_journal(db,profile,actor,journal_id,day,reference,reason):
    original=await db.scalar(select(BookEntry).where(BookEntry.id==journal_id,BookEntry.business_profile_id==profile.id))
    if not original: raise HTTPException(409,'The linked bookkeeping entry is missing. Resolve the books before proceeding.')
    if str(day)<original.day: raise HTTPException(422,'Reversal date cannot precede the original entry.')
    lines=await db.scalars(select(BookLine).where(BookLine.entry_id==original.id))
    data=JournalInput(day=day,reference=reference,memo=reason,lines=[LineInput(account_id=l.account_id,debit=Decimal(l.credit_cents)/100,credit=Decimal(l.debit_cents)/100) for l in lines])
    return await post_journal(db,profile,actor,data,reversal_of=original.id)


@router.get('/')
async def overview(actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor)
    customers=list(await db.scalars(select(BillingCustomer).where(BillingCustomer.business_profile_id==profile.id).order_by(BillingCustomer.name)))
    rows=list(await db.scalars(select(CommercialDocument).where(CommercialDocument.business_profile_id==profile.id).order_by(CommercialDocument.created_at.desc()).limit(200)))
    payments=list(await db.scalars(select(InvoicePayment).where(InvoicePayment.business_profile_id==profile.id).order_by(InvoicePayment.created_at.desc())))
    paid={}
    for payment in payments:
        if not payment.reversal_id: paid[payment.document_id]=paid.get(payment.document_id,0)+payment.amount_cents
    accounts=await db.scalars(select(BookAccount).where(BookAccount.business_profile_id==profile.id,BookAccount.is_cash.is_(True)))
    return {'customers':[customer_data(c) for c in customers], 'documents':[document_data(r,paid.get(r.id,0)) for r in rows],
            'payments':[{k:getattr(p,k) for k in ('id','document_id','day','reference','amount_cents','account_id','journal_id','reversal_id')} for p in payments],
            'cash_accounts':[{'id':a.id,'name':a.name,'currency':a.currency} for a in accounts],
            'notice':'Issuing an invoice posts receivable, income and supplied tax to bookkeeping. Recording payment posts cash/bank against receivable; it does not charge a customer. Tax rates and acceptance evidence are owner-supplied. No tax filing, e-invoice submission or legal acceptance verification.'}


@router.post('/customers',status_code=201)
async def create_customer(data:CustomerInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);row=BillingCustomer(business_profile_id=profile.id,**data.model_dump());db.add(row);await commit(db);return customer_data(row)


@router.post('/documents',status_code=201)
async def create_document(data:DocumentInput,actor=Depends(get_current_user),db=Depends(get_db)):
    row=await create_document_record(db,await business(db,actor),data);await commit(db);return document_data(row)


@router.put('/documents/{document_id}')
async def save_document(document_id:str,data:DocumentInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);await lock_books(db,profile);row=await owned(db,profile,document_id)
    if row.status!='draft' or row.version!=data.version: raise HTTPException(409,'Only the latest draft can be edited. Reload the document.')
    if row.kind!=data.kind: raise HTTPException(422,'Document type cannot change.')
    customer=await db.scalar(select(BillingCustomer).where(BillingCustomer.id==data.customer_id,BillingCustomer.business_profile_id==profile.id))
    if not customer: raise HTTPException(404,'Customer not found.')
    if data.day.year!=row.year: raise HTTPException(422,'The document number belongs to another year. Create a new draft for that year.')
    row.customer_id=customer.id;row.customer=customer_data(customer);row.day=str(data.day);row.due_date=str(data.due_date);row.notes=data.notes;row.terms=data.terms
    for key,value in totals(data.lines).items(): setattr(row,key,value)
    row.version+=1;row.updated_at=datetime.utcnow();await commit(db);return document_data(row)


@router.post('/documents/{document_id}/action')
async def action(document_id:str,data:DecisionInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);await lock_books(db,profile);row=await owned(db,profile,document_id)
    today=local_today(profile);day=data.day or today
    if day>today: raise HTTPException(422,'Action date cannot be in the future.')
    if data.action=='issue':
        if row.status!='draft': raise HTTPException(409,'Only a draft can be issued.')
        if row.day>str(today): raise HTTPException(422,'The document date is in the future.')
        if row.kind=='invoice':
            accounts=await billing_accounts(db,profile,row.currency)
            lines=[LineInput(account_id=accounts['1100'].id,debit=Decimal(row.total_cents)/100)]
            net=row.subtotal_cents-row.discount_cents
            if net: lines.append(LineInput(account_id=accounts['4000'].id,credit=Decimal(net)/100))
            if row.tax_cents: lines.append(LineInput(account_id=accounts['2100'].id,credit=Decimal(row.tax_cents)/100))
            journal=await post_journal(db,profile,actor,JournalInput(day=date.fromisoformat(row.day),reference='ISSUE-'+row.number,memo='Issued '+row.number,lines=lines))
            row.journal_id=journal.id
        row.status='issued'
    elif data.action in ('accept','decline'):
        if row.kind!='quotation' or row.status!='issued': raise HTTPException(409,'Only an issued quotation can be accepted or declined.')
        if not data.note.strip(): raise HTTPException(422,'Record the customer decision evidence or reference.')
        if data.action=='accept' and row.due_date<str(today): raise HTTPException(409,'This quotation has expired. Create a revised quotation before acceptance.')
        row.status='accepted' if data.action=='accept' else 'declined';row.decision_note=data.note
    elif data.action=='convert':
        if row.kind!='quotation' or row.status!='accepted': raise HTTPException(409,'Accept the quotation before creating its invoice.')
        existing=await db.scalar(select(CommercialDocument).where(CommercialDocument.source_quote_id==row.id))
        if existing:return document_data(existing,await paid_amount(db,existing.id))
        items=[ItemInput(description=l['description'],quantity=l['quantity'],unit_price=Decimal(l['unit_price_cents'])/100,discount=Decimal(l['discount_cents'])/100,tax_percent=l['tax_percent']) for l in row.lines]
        invoice=await create_document_record(db,profile,DocumentInput(kind='invoice',customer_id=row.customer_id,day=today,due_date=max(today,date.fromisoformat(row.due_date)),lines=items,notes=row.notes,terms=row.terms))
        invoice.source_quote_id=row.id;invoice.customer=dict(row.customer);invoice.seller=dict(row.seller);invoice.currency=row.currency
        await commit(db);return document_data(invoice)
    else:
        if row.status in ('void','paid') or row.kind=='quotation' and row.status!='draft' and row.status!='issued': raise HTTPException(409,'This document cannot be voided in its current state.')
        if not data.note.strip(): raise HTTPException(422,'A void reason is required.')
        if await paid_amount(db,row.id): raise HTTPException(409,'Reverse recorded payments before voiding this invoice.')
        if row.journal_id: await reverse_journal(db,profile,actor,row.journal_id,day,'VOID-'+row.number,data.note)
        row.status='void';row.decision_note=data.note
    row.version+=1;row.updated_at=datetime.utcnow();await commit(db);return document_data(row,await paid_amount(db,row.id))


@router.post('/documents/{document_id}/payments',status_code=201)
async def record_payment(document_id:str,data:PaymentInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);await lock_books(db,profile);row=await owned(db,profile,document_id)
    if row.kind!='invoice' or row.status!='issued':raise HTTPException(409,'Record payments against an issued unpaid invoice.')
    if str(data.day)<row.day or data.day>local_today(profile):raise HTTPException(422,'Payment date must be between issue date and today.')
    amount=int(data.amount*100);paid=await paid_amount(db,row.id)
    if amount>row.total_cents-paid:raise HTTPException(409,'Payment exceeds the outstanding invoice balance.')
    if await db.scalar(select(InvoicePayment.id).where(InvoicePayment.business_profile_id==profile.id,InvoicePayment.reference==data.reference)):raise HTTPException(409,'This payment reference was already recorded.')
    cash=await db.scalar(select(BookAccount).where(BookAccount.id==data.account_id,BookAccount.business_profile_id==profile.id,BookAccount.is_cash.is_(True),BookAccount.currency==row.currency))
    if not cash:raise HTTPException(404,'Choose a cash/bank account in the invoice currency belonging to this business.')
    accounts=await billing_accounts(db,profile,row.currency);payment_id=str(uuid4())
    journal=await post_journal(db,profile,actor,JournalInput(day=data.day,reference='PAY-'+payment_id,memo='Payment for '+row.number,
             lines=[LineInput(account_id=cash.id,debit=data.amount),LineInput(account_id=accounts['1100'].id,credit=data.amount)]))
    payment=InvoicePayment(id=payment_id,business_profile_id=profile.id,document_id=row.id,reference=data.reference,day=str(data.day),amount_cents=amount,account_id=cash.id,journal_id=journal.id,created_by=actor)
    db.add(payment)
    if paid+amount==row.total_cents:row.status='paid'
    row.version+=1;row.updated_at=datetime.utcnow();await commit(db);return {'id':payment.id,'status':row.status}


@router.post('/payments/{payment_id}/reverse')
async def reverse_payment(payment_id:str,data:PaymentReverseInput,actor=Depends(get_current_user),db=Depends(get_db)):
    profile=await business(db,actor);await lock_books(db,profile)
    payment=await db.scalar(select(InvoicePayment).where(InvoicePayment.id==payment_id,InvoicePayment.business_profile_id==profile.id))
    if not payment:raise HTTPException(404,'Payment not found.')
    if payment.reversal_id:raise HTTPException(409,'This payment has already been reversed.')
    row=await owned(db,profile,payment.document_id)
    reversal=await reverse_journal(db,profile,actor,payment.journal_id,data.day,'REV-PAY-'+payment.id,data.reason)
    payment.reversal_id=reversal.id;row.status='issued';row.version+=1;await commit(db);return {'status':'reversed'}


def build_document_html(row, paid: int, is_preview: bool = False, context: dict | None = None) -> str:
    esc = lambda v: html.escape(str(v if v is not None else ''), quote=True)
    money = lambda cents: f"{row.currency} {int(cents or 0)/100:,.2f}"
    seller = row.seller or {}
    customer = row.customer or {}
    logo = seller.get('logo_data_url') or (context.get('logo_data_url') if context else '') or ''
    logo_tag = f'<img src="{esc(logo)}" alt="Logo" class="logo">' if (logo and (logo.startswith('data:image/') or logo.startswith('http://') or logo.startswith('https://'))) else ''

    kind_title = 'QUOTATION' if row.kind == 'quotation' else 'INVOICE'
    due_label = 'Valid Until' if row.kind == 'quotation' else 'Due Date'

    lines = row.lines or []
    table_rows = []
    for l in lines:
        desc = esc(l.get('description', ''))
        qty = esc(l.get('quantity', 1))
        unit = money(l.get('unit_price_cents', 0))
        disc = money(l.get('discount_cents', 0))
        tax_pct = f"{esc(l.get('tax_percent', 0))}%"
        tot = money(l.get('total_cents', 0))
        table_rows.append(
            f'<tr><td class="col-desc">{desc}</td>'
            f'<td class="col-qty">{qty}</td>'
            f'<td class="col-money">{unit}</td>'
            f'<td class="col-money">{disc}</td>'
            f'<td class="col-tax">{tax_pct}</td>'
            f'<td class="col-money col-tot">{tot}</td></tr>'
        )
    rows_html = '\n'.join(table_rows) if table_rows else '<tr><td colspan="6" class="col-desc empty-cell">No items</td></tr>'

    seller_meta = []
    if seller.get('address'):
        seller_meta.append(esc(seller['address']).replace('\n', '<br>'))
    if seller.get('registration_number'):
        seller_meta.append(f"Reg No: {esc(seller['registration_number'])}")
    if seller.get('email'):
        seller_meta.append(esc(seller['email']))
    if seller.get('website'):
        seller_meta.append(esc(seller['website']))
    seller_meta_html = '<br>'.join(seller_meta)

    customer_meta = []
    if customer.get('address'):
        customer_meta.append(esc(customer['address']).replace('\n', '<br>'))
    if customer.get('registration_number'):
        customer_meta.append(f"Reg No: {esc(customer['registration_number'])}")
    if customer.get('email'):
        customer_meta.append(esc(customer['email']))
    customer_meta_html = '<br>'.join(customer_meta)

    notices = []
    if seller.get('demo'):
        notices.append('<span class="badge badge-demo">DEMO — fictional business and values</span>')
    if row.status == 'draft':
        notices.append('<span class="badge badge-draft">DRAFT — not an issued document</span>')
    elif row.status == 'paid':
        notices.append('<span class="badge badge-paid">PAID</span>')
    elif row.status == 'void':
        notices.append('<span class="badge badge-void">VOID</span>')
    elif row.status == 'accepted':
        notices.append('<span class="badge badge-paid">ACCEPTED</span>')
    elif row.status == 'declined':
        notices.append('<span class="badge badge-void">DECLINED</span>')
    notices_html = f'<div class="badges-row">{" ".join(notices)}</div>' if notices else ''

    balance = row.total_cents - paid
    invoice_extra_totals = ''
    if row.kind == 'invoice':
        invoice_extra_totals = f'''
        <tr>
            <td class="tot-label">Paid:</td>
            <td class="tot-val tot-paid">{money(paid)}</td>
        </tr>
        <tr class="tot-balance-row">
            <td class="tot-label">Balance Due:</td>
            <td class="tot-val tot-balance">{money(balance)}</td>
        </tr>
        '''

    notes_section = f'''
    <div class="footer-block">
        <h4>Notes</h4>
        <div class="pre-text">{esc(row.notes)}</div>
    </div>
    ''' if row.notes else ''

    terms_section = f'''
    <div class="footer-block">
        <h4>Terms & Payment Instructions</h4>
        <div class="pre-text">{esc(row.terms)}</div>
    </div>
    ''' if row.terms else ''

    body_attrs = 'data-preview' if is_preview else ''

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(row.number)}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    line-height: 1.5;
    padding: 40px;
    max-width: 860px;
    margin: 0 auto;
}}
@media print {{
    body {{
        padding: 0;
        margin: 0;
        max-width: 100%;
    }}
    @page {{
        size: A4;
        margin: 14mm;
    }}
}}
body[data-preview] {{
    border-top: 4px solid #2563eb;
}}
.header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid #e2e8f0;
}}
.header-left {{
    max-width: 55%;
}}
.logo {{
    max-width: 180px;
    max-height: 80px;
    object-fit: contain;
    display: block;
    margin-bottom: 12px;
}}
.seller-name {{
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.25;
}}
.seller-meta {{
    margin-top: 6px;
    font-size: 13px;
    color: #475569;
    line-height: 1.45;
}}
.header-right {{
    text-align: right;
    min-width: 200px;
}}
.doc-title {{
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #0f172a;
    text-transform: uppercase;
}}
.doc-number {{
    font-size: 14px;
    font-weight: 600;
    color: #475569;
    margin-top: 4px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}}
.meta-table {{
    margin-top: 12px;
    margin-left: auto;
    font-size: 13px;
    color: #334155;
    border-collapse: collapse;
}}
.meta-table td {{
    padding: 3px 0 3px 12px;
}}
.meta-table .meta-label {{
    color: #64748b;
    font-weight: 500;
    text-align: right;
}}
.meta-table .meta-value {{
    font-weight: 600;
    text-align: right;
    white-space: nowrap;
}}
.badges-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 16px 0 20px 0;
}}
.badge {{
    display: inline-block;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 600;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
.badge-demo {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
.badge-draft {{ background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }}
.badge-paid {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
.badge-void {{ background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}

.parties-grid {{
    display: flex;
    justify-content: space-between;
    gap: 24px;
    margin: 24px 0 28px 0;
}}
.party-card {{
    flex: 1;
    background: #f8fafc;
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #e2e8f0;
}}
.party-label {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    margin-bottom: 6px;
}}
.party-name {{
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 4px;
}}
.party-meta {{
    font-size: 13px;
    color: #475569;
    line-height: 1.45;
}}

.table-wrap {{
    margin: 28px 0;
    width: 100%;
    overflow-x: auto;
}}
table.items-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}}
table.items-table th {{
    background: #f8fafc;
    color: #475569;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 10px 12px;
    border-top: 1px solid #e2e8f0;
    border-bottom: 2px solid #cbd5e1;
}}
table.items-table td {{
    padding: 12px;
    border-bottom: 1px solid #f1f5f9;
    vertical-align: top;
}}
.col-desc {{ text-align: left; }}
.col-qty {{ text-align: center; width: 60px; }}
.col-money {{ text-align: right; width: 110px; font-variant-numeric: tabular-nums; }}
.col-tax {{ text-align: right; width: 70px; }}
.col-tot {{ font-weight: 600; color: #0f172a; }}
.empty-cell {{ text-align: center; color: #64748b; }}

.totals-container {{
    display: flex;
    justify-content: flex-end;
    margin-bottom: 32px;
}}
.totals-table {{
    border-collapse: collapse;
    min-width: 280px;
    font-size: 13px;
}}
.totals-table td {{
    padding: 6px 12px;
}}
.tot-label {{
    text-align: right;
    color: #64748b;
    font-weight: 500;
}}
.tot-val {{
    text-align: right;
    color: #1e293b;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}}
.tot-grand-row td {{
    border-top: 2px solid #e2e8f0;
    padding-top: 10px;
    padding-bottom: 10px;
}}
.tot-grand {{
    font-size: 18px;
    font-weight: 800;
    color: #0f172a;
}}
.tot-paid {{
    color: #16a34a;
}}
.tot-balance-row td {{
    border-top: 1px solid #f1f5f9;
    padding-top: 8px;
}}
.tot-balance {{
    font-size: 15px;
    font-weight: 700;
    color: #dc2626;
}}

.footer-section {{
    margin-top: 32px;
    padding-top: 20px;
    border-top: 1px solid #e2e8f0;
}}
.footer-block {{
    margin-bottom: 18px;
}}
.footer-block h4 {{
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #475569;
    margin-bottom: 6px;
}}
.pre-text {{
    font-size: 13px;
    color: #475569;
    white-space: pre-wrap;
    line-height: 1.5;
}}
.disclaimer {{
    font-size: 11px;
    color: #94a3b8;
    margin-top: 24px;
    text-align: center;
}}
</style>
</head>
<body {body_attrs}>
<header class="header">
    <div class="header-left">
        {logo_tag}
        <div class="seller-name">{esc(seller.get('name', ''))}</div>
        <div class="seller-meta">{seller_meta_html}</div>
    </div>
    <div class="header-right">
        <div class="doc-title">{kind_title}</div>
        <div class="doc-number">{esc(row.number)}</div>
        <table class="meta-table">
            <tr>
                <td class="meta-label">Date:</td>
                <td class="meta-value">{esc(row.day)}</td>
            </tr>
            <tr>
                <td class="meta-label">{due_label}:</td>
                <td class="meta-value">{esc(row.due_date)}</td>
            </tr>
            <tr>
                <td class="meta-label">Currency:</td>
                <td class="meta-value">{esc(row.currency)}</td>
            </tr>
        </table>
    </div>
</header>

{notices_html}

<section class="parties-grid">
    <div class="party-card">
        <div class="party-label">{'Quote For' if row.kind == 'quotation' else 'Bill To'}</div>
        <div class="party-name">{esc(customer.get('name', ''))}</div>
        <div class="party-meta">{customer_meta_html}</div>
    </div>
</section>

<div class="table-wrap">
    <table class="items-table">
        <thead>
            <tr>
                <th class="col-desc">Description</th>
                <th class="col-qty">Qty</th>
                <th class="col-money">Unit Price</th>
                <th class="col-money">Discount</th>
                <th class="col-tax">Tax</th>
                <th class="col-money">Total</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
</div>

<div class="totals-container">
    <table class="totals-table">
        <tr>
            <td class="tot-label">Subtotal:</td>
            <td class="tot-val">{money(row.subtotal_cents)}</td>
        </tr>
        <tr>
            <td class="tot-label">Discount:</td>
            <td class="tot-val">{money(row.discount_cents)}</td>
        </tr>
        <tr>
            <td class="tot-label">Tax:</td>
            <td class="tot-val">{money(row.tax_cents)}</td>
        </tr>
        <tr class="tot-grand-row">
            <td class="tot-label tot-grand">Total:</td>
            <td class="tot-val tot-grand">{money(row.total_cents)}</td>
        </tr>
        {invoice_extra_totals}
    </table>
</div>

<footer class="footer-section">
    {notes_section}
    {terms_section}
    <div class="disclaimer">Tax rates supplied by the issuer. This document is not a tax-authority e-invoice submission.</div>
</footer>
</body>
</html>'''


@router.get('/documents/{document_id}/print')
async def print_document(document_id: str, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await owned(db, profile, document_id)
    paid = await paid_amount(db, row.id)
    context = context_data(profile)
    content = build_document_html(row, paid, is_preview=False, context=context)
    return Response(
        content,
        media_type='text/html',
        headers={
            'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; base-uri 'none'; form-action 'none'"
        }
    )


@router.get('/documents/{document_id}/preview')
async def preview_document(document_id: str, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await owned(db, profile, document_id)
    paid = await paid_amount(db, row.id)
    context = context_data(profile)
    content = build_document_html(row, paid, is_preview=True, context=context)
    return Response(
        content,
        media_type='text/html',
        headers={
            'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; base-uri 'none'; form-action 'none'"
        }
    )
