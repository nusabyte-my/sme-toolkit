"""Owner-managed employee records, onboarding and reviewed leave. No payroll/statutory claims."""
from datetime import date, datetime, timedelta
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import select, func, update
from sqlalchemy.exc import IntegrityError
from app.auth import get_current_user
from app.database import get_db, Employee, EmployeeTask, LeaveRequest
from app.services.owner_service import business, iso

router = APIRouter()


class EmployeeInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    code: str = Field(min_length=1, max_length=30, pattern=r'^[A-Za-z0-9-]+$')
    name: str = Field(min_length=1, max_length=160)
    email: str = Field(default='', max_length=254)
    department: str = Field(default='', max_length=100)
    job_title: str = Field(default='', max_length=120)
    manager_id: str | None = Field(default=None, max_length=50)
    start_date: date
    status: Literal['active', 'onboarding', 'inactive'] = 'active'
    annual_leave_days: int = Field(default=0, ge=0, le=365)
    version: int | None = Field(default=None, ge=1)

    @field_validator('email')
    @classmethod
    def email_format(cls, value):
        if value and ('@' not in value or any(c.isspace() for c in value)):
            raise ValueError('Enter a valid work email or leave it blank')
        return value


class LeaveInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    employee_id: str = Field(min_length=1, max_length=50)
    start_date: date
    end_date: date
    kind: Literal['annual', 'unpaid'] = 'annual'
    note: str = Field(default='', max_length=1000)

    @model_validator(mode='after')
    def dates(self):
        if self.start_date > self.end_date or self.start_date.year != self.end_date.year:
            raise ValueError('Use an ordered date range within one calendar year; split year-crossing leave into separate requests')
        return self


class DecisionInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['approved', 'rejected', 'cancelled']


class TaskInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    employee_id: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=180)
    due_date: date


class TaskStatus(BaseModel):
    model_config = ConfigDict(extra='forbid')
    completed: bool


def employee_data(row):
    return {key: getattr(row, key) for key in ('id','code','name','email','department','job_title','manager_id','start_date','status','annual_leave_days','version')}


def leave_data(row):
    return {key: getattr(row, key) for key in ('id','employee_id','start_date','end_date','days','kind','note','status','reviewed_by')} | {'reviewed_at': iso(row.reviewed_at), 'created_at': iso(row.created_at)}


def task_data(row):
    return {key: getattr(row, key) for key in ('id','employee_id','title','due_date','completed','completed_by')} | {'completed_at': iso(row.completed_at)}


async def employee_owned(db, profile_id, employee_id):
    row = await db.scalar(select(Employee).where(Employee.business_profile_id == profile_id, Employee.id == employee_id).execution_options(populate_existing=True))
    if not row: raise HTTPException(404, 'Employee not found in this business.')
    return row


async def employee_lock(db, profile_id, employee_id):
    # Leave reservations and decisions serialize on the employee, across workers.
    result = await db.execute(update(Employee).where(Employee.id == employee_id, Employee.business_profile_id == profile_id).values(version=Employee.version+1))
    if not result.rowcount: raise HTTPException(404, 'Employee not found in this business.')
    return await employee_owned(db, profile_id, employee_id)


async def manager_check(db, pid, manager_id, employee_id=None):
    seen = {employee_id} if employee_id else set()
    while manager_id:
        if manager_id in seen: raise HTTPException(422, 'The reporting line cannot contain a cycle.')
        seen.add(manager_id)
        manager = await employee_owned(db, pid, manager_id)
        if manager.status == 'inactive': raise HTTPException(422, 'Choose an active manager.')
        manager_id = manager.manager_id


async def commit(db):
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, 'Employee code already exists or a concurrent update changed this record. Refresh and try again.')


def weekdays(start, end):
    return sum((start+timedelta(days=i)).weekday() < 5 for i in range((end-start).days+1))


@router.get('/')
async def overview(year: int | None = Query(default=None, ge=2000, le=2100), search: str = Query('', max_length=160), actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    year = year or date.today().year
    employees = list(await db.scalars(select(Employee).where(Employee.business_profile_id == profile.id).order_by(Employee.name)))
    leaves = list(await db.scalars(select(LeaveRequest).where(LeaveRequest.business_profile_id == profile.id, LeaveRequest.start_date >= f'{year}-01-01', LeaveRequest.end_date <= f'{year}-12-31').order_by(LeaveRequest.created_at.desc())))
    tasks = list(await db.scalars(select(EmployeeTask).where(EmployeeTask.business_profile_id == profile.id).order_by(EmployeeTask.completed, EmployeeTask.due_date)))
    rows = []
    for employee in employees:
        if search.casefold() not in f'{employee.name} {employee.code} {employee.department} {employee.job_title}'.casefold(): continue
        used = sum(r.days for r in leaves if r.employee_id == employee.id and r.kind == 'annual' and r.status == 'approved')
        reserved = sum(r.days for r in leaves if r.employee_id == employee.id and r.kind == 'annual' and r.status == 'pending')
        rows.append({**employee_data(employee), 'used_days': used, 'pending_days': reserved, 'available_days': employee.annual_leave_days-used-reserved})
    return {'year': year, 'employees': rows, 'leave': [leave_data(r) for r in leaves], 'tasks': [task_data(r) for r in tasks],
            'summary': {'active': sum(e.status != 'inactive' for e in employees), 'onboarding': sum(e.status == 'onboarding' for e in employees),
                        'departments': len({e.department for e in employees if e.department and e.status != 'inactive'}),
                        'pending_leave': sum(r.status == 'pending' for r in leaves), 'open_tasks': sum(not r.completed for r in tasks)},
            'notice': 'Private owner-managed HR records. Annual allowance is configured per employee, not a statutory entitlement calculation. Leave counts Monday–Friday, excludes weekends only, and has no public-holiday calendar, accrual or carry-forward. No payroll, tax filing, attendance tracking or employee self-service is claimed.'}


@router.post('/employees', status_code=201)
async def create_employee(data: EmployeeInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    from app.database import BusinessProfile
    await db.execute(update(BusinessProfile).where(BusinessProfile.id == profile.id).values(id=BusinessProfile.id))
    await manager_check(db, profile.id, data.manager_id)
    values = data.model_dump(exclude={'version'}); values['start_date'] = str(data.start_date)
    row = Employee(business_profile_id=profile.id, **values)
    db.add(row)
    await commit(db)
    return employee_data(row)


@router.put('/employees/{employee_id}')
async def save_employee(employee_id: str, data: EmployeeInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    if data.version is None: raise HTTPException(422, 'Employee version is required; reload this record.')
    row = await employee_owned(db, profile.id, employee_id)
    # Lock a single shared parent to serialize manager graph edits, preventing concurrent cycles.
    from app.database import BusinessProfile
    await db.execute(update(BusinessProfile).where(BusinessProfile.id == profile.id).values(id=BusinessProfile.id))
    await db.execute(update(Employee).where(Employee.id == employee_id, Employee.business_profile_id == profile.id).values(id=Employee.id))
    await db.refresh(row)
    if row.version != data.version:
        raise HTTPException(409, 'Employee changed in another request. Reload before saving.')
    await manager_check(db, profile.id, data.manager_id, employee_id)
    active_leave = list(await db.scalars(select(LeaveRequest).where(LeaveRequest.employee_id == employee_id, LeaveRequest.status.in_(['pending','approved']))))
    if any(str(data.start_date) > request.start_date for request in active_leave):
        raise HTTPException(409, 'Employment start cannot move after pending or approved leave. Review those requests first.')
    reserved_by_year = {}
    for request in active_leave:
        if request.kind == 'annual': reserved_by_year[request.start_date[:4]] = reserved_by_year.get(request.start_date[:4],0)+request.days
    if any(days > data.annual_leave_days for days in reserved_by_year.values()):
        raise HTTPException(409, 'Allowance cannot be lower than approved and pending annual leave. Review the requests first.')
    if data.status == 'inactive':
        if any(r.status == 'pending' or r.end_date >= str(date.today()) for r in active_leave):
            raise HTTPException(409, 'Review pending or upcoming leave before making this employee inactive.')
        if await db.scalar(select(Employee.id).where(Employee.manager_id == employee_id, Employee.status != 'inactive').limit(1)):
            raise HTTPException(409, 'Reassign active direct reports before making their manager inactive.')
    values = data.model_dump(exclude={'version'}); values.update(start_date=str(data.start_date), version=Employee.version+1, updated_at=datetime.utcnow())
    result = await db.execute(update(Employee).where(Employee.id == employee_id, Employee.business_profile_id == profile.id, Employee.version == data.version).values(**values))
    if not result.rowcount:
        await db.rollback(); raise HTTPException(409, 'Employee changed in another request. Reload before saving.')
    await commit(db)
    await db.refresh(row)
    return employee_data(row)


@router.post('/leave', status_code=201)
async def request_leave(data: LeaveInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    employee = await employee_lock(db, profile.id, data.employee_id)
    if employee.status == 'inactive': raise HTTPException(409, 'Inactive employees cannot request leave.')
    if str(data.start_date) < employee.start_date: raise HTTPException(422, 'Leave cannot begin before employment starts.')
    days = weekdays(data.start_date, data.end_date)
    if not days: raise HTTPException(422, 'This range contains no Monday–Friday working days.')
    overlap = await db.scalar(select(LeaveRequest.id).where(LeaveRequest.employee_id == employee.id,
                    LeaveRequest.status.in_(['pending','approved']), LeaveRequest.start_date <= str(data.end_date), LeaveRequest.end_date >= str(data.start_date)).limit(1))
    if overlap: raise HTTPException(409, 'This employee already has pending or approved leave in that date range.')
    if data.kind == 'annual':
        used = await db.scalar(select(func.coalesce(func.sum(LeaveRequest.days),0)).where(LeaveRequest.employee_id == employee.id, LeaveRequest.kind == 'annual',
                            LeaveRequest.status.in_(['pending','approved']), LeaveRequest.start_date >= f'{data.start_date.year}-01-01', LeaveRequest.end_date <= f'{data.start_date.year}-12-31'))
        if used+days > employee.annual_leave_days: raise HTTPException(409, 'Requested days exceed the available annual allowance, including pending requests.')
    row = LeaveRequest(business_profile_id=profile.id, employee_id=employee.id, start_date=str(data.start_date), end_date=str(data.end_date), days=days, kind=data.kind, note=data.note)
    db.add(row)
    await commit(db)
    return leave_data(row)


@router.patch('/leave/{leave_id}')
async def review_leave(leave_id: str, data: DecisionInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await db.scalar(select(LeaveRequest).where(LeaveRequest.id == leave_id, LeaveRequest.business_profile_id == profile.id))
    if not row: raise HTTPException(404, 'Leave request not found.')
    await employee_lock(db, profile.id, row.employee_id)
    await db.refresh(row)
    allowed = row.status == 'pending' or (row.status == 'approved' and data.status == 'cancelled')
    if not allowed: raise HTTPException(409, 'This request is already closed. Reload the leave list.')
    row.status = data.status; row.reviewed_by = actor; row.reviewed_at = datetime.utcnow()
    await commit(db)
    return leave_data(row)


@router.post('/tasks', status_code=201)
async def add_task(data: TaskInput, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    employee = await employee_owned(db, profile.id, data.employee_id)
    if employee.status == 'inactive': raise HTTPException(409, 'Choose an active or onboarding employee.')
    row = EmployeeTask(business_profile_id=profile.id, employee_id=employee.id, title=data.title, due_date=str(data.due_date))
    db.add(row)
    await commit(db)
    return task_data(row)


@router.patch('/tasks/{task_id}')
async def task_status(task_id: str, data: TaskStatus, actor=Depends(get_current_user), db=Depends(get_db)):
    profile = await business(db, actor)
    row = await db.scalar(select(EmployeeTask).where(EmployeeTask.id == task_id, EmployeeTask.business_profile_id == profile.id))
    if not row: raise HTTPException(404, 'Employee task not found.')
    row.completed = data.completed
    row.completed_at = datetime.utcnow() if data.completed else None
    row.completed_by = actor if data.completed else None
    await commit(db)
    return task_data(row)
