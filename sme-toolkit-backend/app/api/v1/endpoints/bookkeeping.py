"""Owner-scoped double-entry bookkeeping. Integer cents; posted journals are immutable."""
import csv
import io
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select, func, update
from sqlalchemy.exc import IntegrityError
from app.auth import get_current_user
from app.database import get_db, BusinessProfile, BookAccount, BookEntry, BookLine, BookReconciliation
from app.services.owner_service import business, context_data, iso

router = APIRouter()
Money = Decimal


class AccountInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    code: str = Field(min_length=1, max_length=20, pattern=r'^[A-Za-z0-9-]+$')
    name: str = Field(min_length=1, max_length=120)
    kind: Literal['asset', 'liability', 'equity', 'income', 'expense']
    is_cash: bool = False

    @model_validator(mode='after')
    def cash_asset(self):
        if self.is_cash and self.kind != 'asset':
            raise ValueError('Cash and bank accounts must be assets')
        return self


class LineInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    account_id: str = Field(min_length=1, max_length=50)
    debit: Money = Field(default=0, ge=0, le=999999999, max_digits=11, decimal_places=2, allow_inf_nan=False)
    credit: Money = Field(default=0, ge=0, le=999999999, max_digits=11, decimal_places=2, allow_inf_nan=False)

    @model_validator(mode='after')
    def one_side(self):
        if (self.debit > 0) == (self.credit > 0):
            raise ValueError('Each line needs a debit or a credit, not both')
        return self


class JournalInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    day: date
    reference: str = Field(min_length=1, max_length=100)
    memo: str = Field(min_length=1, max_length=1000)
    lines: list[LineInput] = Field(min_length=2, max_length=30)

    @model_validator(mode='after')
    def balanced(self):
        if sum(line.debit for line in self.lines) != sum(line.credit for line in self.lines):
            raise ValueError('Total debits must equal total credits')
        if len({line.account_id for line in self.lines}) != len(self.lines):
            raise ValueError('Use one line per account')
        return self


class ReverseInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    day: date
    reference: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=3, max_length=800)


class ReconcileInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    account_id: str = Field(min_length=1, max_length=50)
    day: date
    statement_balance: Money = Field(ge=-999999999, le=999999999, max_digits=11, decimal_places=2, allow_inf_nan=False)
    reference: str = Field(min_length=1, max_length=100)


def account_data(row):
    return {key: getattr(row, key) for key in ('id', 'code', 'name', 'kind', 'currency', 'is_cash')}


async def lock_books(db, profile):
    # Serialize posting/reconciliation so a new posting cannot race a period lock.
    await db.execute(update(BusinessProfile).where(BusinessProfile.id == profile.id).values(id=BusinessProfile.id))


async def setup_accounts(db, profile):
    await lock_books(db, profile)
    if await db.scalar(select(BookAccount.id).where(BookAccount.business_profile_id == profile.id).limit(1)):
        return
    currency = context_data(profile)['currency']
    for code, name, kind, cash in [('1000','Bank','asset',True), ('1010','Cash on hand','asset',True),
                                  ('1100','Accounts receivable','asset',False), ('2000','Accounts payable','liability',False),
                                  ('3000','Owner equity','equity',False), ('4000','Sales income','income',False),
                                  ('5000','Cost of sales','expense',False), ('6000','Operating expenses','expense',False),
                                  ('6100','Payroll expense','expense',False)]:
        db.add(BookAccount(business_profile_id=profile.id, code=code, name=name, kind=kind, is_cash=cash, currency=currency))
    await db.flush()


async def post_journal(db, profile, actor, data, reversal_of=None):
    await lock_books(db, profile)
    today = datetime.now(ZoneInfo(context_data(profile)['timezone'])).date()
    if data.day > today:
        raise HTTPException(422, 'A posted journal cannot have a future date.')
    accounts = list(await db.scalars(select(BookAccount).where(BookAccount.business_profile_id == profile.id,
                                                                  BookAccount.id.in_([line.account_id for line in data.lines]))))
    if len(accounts) != len(data.lines):
        raise HTTPException(404, 'One or more accounts do not belong to this business.')
    currencies = {account.currency for account in accounts}
    if len(currencies) != 1:
        raise HTTPException(422, 'All journal accounts must use the same currency. No exchange rate is inferred.')
    locked = await db.scalar(select(BookReconciliation.id).where(BookReconciliation.business_profile_id == profile.id,
                            BookReconciliation.account_id.in_([a.id for a in accounts if a.is_cash]),
                            BookReconciliation.day >= str(data.day)).limit(1))
    if locked:
        raise HTTPException(409, 'A bank reconciliation locks this date. Post an adjustment after the reconciled date instead.')
    if await db.scalar(select(BookEntry.id).where(BookEntry.business_profile_id == profile.id, BookEntry.reference == data.reference)):
        raise HTTPException(409, 'This journal reference already exists. Open the posted entry instead of posting it again.')
    if reversal_of and await db.scalar(select(BookEntry.id).where(BookEntry.reversal_of == reversal_of)):
        raise HTTPException(409, 'This entry has already been reversed.')
    row = BookEntry(business_profile_id=profile.id, day=str(data.day), reference=data.reference, memo=data.memo,
                    currency=next(iter(currencies)), created_by=actor, reversal_of=reversal_of)
    db.add(row)
    await db.flush()
    for line in data.lines:
        db.add(BookLine(entry_id=row.id, account_id=line.account_id, debit_cents=int(line.debit*100), credit_cents=int(line.credit*100)))
    await db.flush()
    return row


async def commit(db):
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, 'This record was saved by another request. Refresh before trying again.')


@router.post('/setup')
async def setup(actor=Depends(get_current_user), db=Depends(get_db)):
    await setup_accounts(db, await business(db, actor))
    await commit(db)
    return {'status': 'ready'}


@router.post('/accounts', status_code=201)
async def add_account(data: AccountInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = BookAccount(business_profile_id=profile.id, currency=context_data(profile)['currency'], **data.model_dump())
    db.add(row)
    await commit(db)
    return account_data(row)


async def account_balance(db, pid, account_id, day):
    value = await db.scalar(select(func.coalesce(func.sum(BookLine.debit_cents-BookLine.credit_cents), 0)).join(BookEntry, BookLine.entry_id == BookEntry.id)
                            .where(BookEntry.business_profile_id == pid, BookLine.account_id == account_id, BookEntry.day <= str(day)))
    return int(value)


@router.get('/')
async def overview(start: date | None = None, end: date | None = None, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    end = end or datetime.now(ZoneInfo(context_data(profile)['timezone'])).date()
    start = start or end.replace(day=1)
    if start > end:
        raise HTTPException(422, 'Start date must be on or before the end date.')
    accounts = list(await db.scalars(select(BookAccount).where(BookAccount.business_profile_id == profile.id).order_by(BookAccount.code)))
    grouped = (await db.execute(select(BookLine.account_id, func.sum(BookLine.debit_cents), func.sum(BookLine.credit_cents))
                               .join(BookEntry, BookEntry.id == BookLine.entry_id)
                               .where(BookEntry.business_profile_id == profile.id, BookEntry.day <= str(end))
                               .group_by(BookLine.account_id))).all()
    balances = {aid: (int(debit), int(credit)) for aid, debit, credit in grouped}
    period = (await db.execute(select(BookAccount.currency, BookAccount.kind, func.sum(BookLine.debit_cents), func.sum(BookLine.credit_cents))
                              .join(BookLine, BookLine.account_id == BookAccount.id).join(BookEntry, BookEntry.id == BookLine.entry_id)
                              .where(BookEntry.business_profile_id == profile.id, BookEntry.day >= str(start), BookEntry.day <= str(end))
                              .group_by(BookAccount.currency, BookAccount.kind))).all()
    reports = {}
    for account in accounts:
        reports.setdefault(account.currency, {'currency': account.currency, 'income_cents': 0, 'expense_cents': 0, 'net_cents': 0, 'debits_cents': 0, 'credits_cents': 0})
    for currency, kind, debit, credit in period:
        if kind == 'income': reports[currency]['income_cents'] += int(credit-debit)
        if kind == 'expense': reports[currency]['expense_cents'] += int(debit-credit)
    trial = []
    for account in accounts:
        debit, credit = balances.get(account.id, (0, 0))
        balance = debit-credit
        trial.append({**account_data(account), 'debit_cents': max(balance, 0), 'credit_cents': max(-balance, 0), 'balance_cents': balance})
        reports[account.currency]['debits_cents'] += max(balance, 0)
        reports[account.currency]['credits_cents'] += max(-balance, 0)
    for report in reports.values(): report['net_cents'] = report['income_cents']-report['expense_cents']
    entries = list(await db.scalars(select(BookEntry).where(BookEntry.business_profile_id == profile.id, BookEntry.day >= str(start), BookEntry.day <= str(end)).order_by(BookEntry.day.desc(), BookEntry.created_at.desc()).limit(100)))
    lines = list(await db.scalars(select(BookLine).where(BookLine.entry_id.in_([e.id for e in entries])))) if entries else []
    reversals = dict((await db.execute(select(BookEntry.reversal_of, BookEntry.id).where(BookEntry.business_profile_id == profile.id, BookEntry.reversal_of.in_([e.id for e in entries])))).all()) if entries else {}
    reconciliations = list(await db.scalars(select(BookReconciliation).where(BookReconciliation.business_profile_id == profile.id).order_by(BookReconciliation.day.desc()).limit(100)))
    return {'accounts': [account_data(a) for a in accounts], 'start': str(start), 'end': str(end), 'trial_balance': trial, 'reports': list(reports.values()),
            'entries': [{**{k: getattr(e, k) for k in ('id','day','reference','memo','currency','reversal_of','created_by')}, 'created_at': iso(e.created_at), 'reversed_by': reversals.get(e.id),
                         'lines': [{'account_id': l.account_id, 'debit_cents': l.debit_cents, 'credit_cents': l.credit_cents} for l in lines if l.entry_id == e.id]} for e in entries],
            'reconciliations': [{k: getattr(r, k) for k in ('id','account_id','day','reference','statement_cents','book_cents','created_by')} for r in reconciliations],
            'notice': 'Posted bookkeeping only; sales ledger entries are not imported automatically. Currencies remain separate. Reconciliation compares a supplied closing balance, not a live bank feed. No tax filing or statutory financial statement is claimed.'}


@router.post('/entries', status_code=201)
async def create_entry(data: JournalInput, actor=Depends(get_current_user), db=Depends(get_db)):
    row = await post_journal(db, await business(db, actor), actor, data)
    await commit(db)
    return {'id': row.id, 'reference': row.reference}


@router.post('/entries/{entry_id}/reverse', status_code=201)
async def reverse_entry(entry_id: str, data: ReverseInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    original = await db.scalar(select(BookEntry).where(BookEntry.id == entry_id, BookEntry.business_profile_id == profile.id))
    if not original: raise HTTPException(404, 'Journal not found.')
    from app.database import CommercialDocument, InvoicePayment
    if await db.scalar(select(CommercialDocument.id).where(CommercialDocument.journal_id==entry_id)) or await db.scalar(select(InvoicePayment.id).where(InvoicePayment.journal_id==entry_id)):
        raise HTTPException(409, 'This journal belongs to an invoice or payment. Use its billing reversal/void action to keep both records consistent.')
    if original.reversal_of: raise HTTPException(409, 'Do not reverse a reversal. Post a new documented adjustment.')
    if str(data.day) < original.day: raise HTTPException(422, 'The reversal date cannot precede the original entry.')
    lines = await db.scalars(select(BookLine).where(BookLine.entry_id == original.id))
    journal = JournalInput(day=data.day, reference=data.reference, memo='Reversal: '+data.reason,
                           lines=[LineInput(account_id=l.account_id, debit=Decimal(l.credit_cents)/100, credit=Decimal(l.debit_cents)/100) for l in lines])
    row = await post_journal(db, profile, actor, journal, original.id)
    await commit(db)
    return {'id': row.id, 'reference': row.reference}


@router.post('/reconciliations', status_code=201)
async def reconcile(data: ReconcileInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    await lock_books(db, profile)
    account = await db.scalar(select(BookAccount).where(BookAccount.id == data.account_id, BookAccount.business_profile_id == profile.id, BookAccount.is_cash.is_(True)))
    if not account: raise HTTPException(404, 'Choose a cash or bank account belonging to this business.')
    if data.day > datetime.now(ZoneInfo(context_data(profile)['timezone'])).date(): raise HTTPException(422, 'Statement date cannot be in the future.')
    balance = await account_balance(db, profile.id, account.id, data.day)
    statement = int(data.statement_balance*100)
    if statement != balance:
        raise HTTPException(409, f'Statement and books differ by {account.currency} {(statement-balance)/100:,.2f}. Record or correct the missing transactions before reconciling.')
    row = BookReconciliation(business_profile_id=profile.id, account_id=account.id, day=str(data.day), statement_cents=statement,
                             book_cents=balance, reference=data.reference, created_by=actor)
    db.add(row)
    await commit(db)
    return {'id': row.id, 'status': 'reconciled'}


@router.get('/export')
async def export(start: date, end: date, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    if start > end: raise HTTPException(422, 'Choose a valid date range.')
    rows = await db.execute(select(BookEntry, BookLine, BookAccount).join(BookLine, BookLine.entry_id == BookEntry.id).join(BookAccount, BookAccount.id == BookLine.account_id)
                           .where(BookEntry.business_profile_id == profile.id, BookEntry.day >= str(start), BookEntry.day <= str(end)).order_by(BookEntry.day, BookEntry.reference, BookAccount.code))
    stream = io.StringIO(); writer = csv.writer(stream)
    writer.writerow(['Date','Reference','Memo','Account','Account name','Currency','Debit','Credit'])
    def safe(value):
        value = str(value)
        return "'"+value if value.lstrip().startswith(('=','+','-','@')) else value
    for entry, line, account in rows:
        writer.writerow([entry.day, safe(entry.reference), safe(entry.memo), safe(account.code), safe(account.name), account.currency, f'{line.debit_cents/100:.2f}', f'{line.credit_cents/100:.2f}'])
    return Response(stream.getvalue(), media_type='text/csv', headers={'Content-Disposition':'attachment; filename="bookkeeping-journal.csv"'})
