from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.schedule_rule import ScheduleRule
from app.schemas.schedule_rule import ScheduleRuleCreate, ScheduleRuleOut

router = APIRouter(prefix="/schedule-rules", tags=["schedule-rules"])


@router.post("/", response_model=ScheduleRuleOut, status_code=201)
async def create_rule(data: ScheduleRuleCreate, db: AsyncSession = Depends(get_db)):
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


@router.get("/", response_model=list[ScheduleRuleOut])
async def list_rules(employee_id: str | None = None, db: AsyncSession = Depends(get_db)):
    q = select(ScheduleRule).where(ScheduleRule.active.is_(True))
    if employee_id:
        q = q.where(ScheduleRule.employee_id == employee_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.delete("/{rule_id}", status_code=204)
async def deactivate_rule(rule_id, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScheduleRule).where(ScheduleRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "Regra não encontrada.")
    rule.active = False
    await db.commit()
