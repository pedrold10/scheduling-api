from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.available_slot import AvailableSlot
from app.schemas.available_slot import AvailableSlotOut
from app.services.slot_generator import generate_slots_for_employee
from fastapi import Request
from app.models.employee import Employee
from app.services.auth import (
    get_current_user,
    get_establishment_ids,
)
router = APIRouter(prefix="/availability", tags=["availability"])


@router.get("", response_model=list[AvailableSlotOut])
@router.get("/", response_model=list[AvailableSlotOut], include_in_schema=False)
async def get_availability(
    request: Request,
    employee_id: str = Query(...),
    from_date: date = Query(default=None),
    to_date: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    current = await get_current_user(request, db)

    if current.role == "owner":

        result = await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )

        employee = result.scalar_one_or_none()

        if employee is None:
            raise HTTPException(404, "Funcionário não encontrado.")

        allowed = await get_establishment_ids(db, current.id)

        if employee.establishment_id not in allowed:
            raise HTTPException(403, "Sem acesso.")

    today = date.today()

    from_date = from_date or today
    to_date = to_date or (today + timedelta(days=30))

    await generate_slots_for_employee(
        db,
        employee_id,
        from_date,
        to_date,
    )

    result = await db.execute(
        select(AvailableSlot)
        .where(
            AvailableSlot.employee_id == employee_id,
            AvailableSlot.slot_date >= from_date,
            AvailableSlot.slot_date <= to_date,
            AvailableSlot.status == "available",
        )
        .order_by(
            AvailableSlot.slot_date,
            AvailableSlot.start_time,
        )
    )

    return result.scalars().all()