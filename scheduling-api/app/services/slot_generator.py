from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schedule_rule import ScheduleRule
from app.models.available_slot import AvailableSlot


async def generate_slots_for_employee(
    db: AsyncSession,
    employee_id,
    from_date: date,
    to_date: date,
) -> int:
    """
    Gera AvailableSlots para um funcionário entre from_date e to_date
    com base nas ScheduleRules ativas.

    Slots já existentes são ignorados (upsert seguro via UNIQUE constraint).
    Retorna o número de slots criados.
    """
    result = await db.execute(
        select(ScheduleRule).where(
            ScheduleRule.employee_id == employee_id,
            ScheduleRule.active.is_(True),
            ScheduleRule.valid_from <= to_date,
            (ScheduleRule.valid_until == None) | (ScheduleRule.valid_until >= from_date),
        )
    )
    rules = result.scalars().all()

    if not rules:
        return 0

    created = 0
    current_date = from_date

    while current_date <= to_date:
        weekday = current_date.weekday()  # 0=seg, 6=dom

        for rule in rules:
            if weekday not in rule.days_list:
                continue

            slot_start = datetime.combine(current_date, rule.start_time)
            slot_end = datetime.combine(current_date, rule.end_time)
            delta = timedelta(minutes=rule.slot_duration_minutes)

            while slot_start + delta <= slot_end:
                exists = await db.execute(
                    select(AvailableSlot).where(
                        AvailableSlot.employee_id == employee_id,
                        AvailableSlot.slot_date == current_date,
                        AvailableSlot.start_time == slot_start.time(),
                    )
                )
                if not exists.scalar_one_or_none():
                    db.add(AvailableSlot(
                        employee_id=employee_id,
                        slot_date=current_date,
                        start_time=slot_start.time(),
                        end_time=(slot_start + delta).time(),
                        status="available",
                    ))
                    created += 1

                slot_start += delta

        current_date += timedelta(days=1)

    await db.commit()
    return created
