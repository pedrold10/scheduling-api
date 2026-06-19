from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.models.schedule_rule import ScheduleRule
from app.models.employee import Employee
from app.schemas.schedule_rule import ScheduleRuleCreate, ScheduleRuleOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/schedule-rules", tags=["schedule-rules"])


@router.post("", response_model=ScheduleRuleOut, status_code=201)
@router.post("/", response_model=ScheduleRuleOut, status_code=201, include_in_schema=False)
async def create_rule(request: Request, data: ScheduleRuleCreate, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    if current.role == "owner":
        emp = await db.execute(select(Employee).where(Employee.id == data.employee_id))
        emp = emp.scalar_one_or_none()
        if not emp or emp.establishment_id not in [e.id for e in current.establishments]:
            raise HTTPException(403, "Funcionário não pertence ao seu estabelecimento.")
    rule = ScheduleRule(
        employee_id=data.employee_id,
        days_of_week=data.days_as_csv(),
        start_time=data.start_time,
        end_time=data.end_time,
        slot_duration_minutes=data.slot_duration_minutes,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("", response_model=list[ScheduleRuleOut])
@router.get("/", response_model=list[ScheduleRuleOut], include_in_schema=False)
async def list_rules(request: Request, employee_id: str | None = None, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    q = select(ScheduleRule).where(ScheduleRule.active.is_(True))
    if current.role == "owner":
        est_ids = [e.id for e in current.establishments]
        emp_res = await db.execute(select(Employee.id).where(Employee.establishment_id.in_(est_ids)))
        emp_ids = [r[0] for r in emp_res.all()]
        q = q.where(ScheduleRule.employee_id.in_(emp_ids))
    if employee_id:
        q = q.where(ScheduleRule.employee_id == employee_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.delete("/{rule_id}", status_code=204)
async def deactivate_rule(rule_id, request: Request, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    result = await db.execute(select(ScheduleRule).where(ScheduleRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "Regra não encontrada.")
    rule.active = False
    await db.commit()
