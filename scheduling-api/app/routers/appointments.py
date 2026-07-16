from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.models.appointment import Appointment
from app.models.available_slot import AvailableSlot
from app.models.employee import Employee
from app.schemas.appointment import AppointmentCreate, AppointmentOut
from app.services.auth import (
    get_current_user,
    get_establishment_ids,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])

_RELATIONS = (
    joinedload(Appointment.slot),
    joinedload(Appointment.client),
    joinedload(Appointment.employee),
    joinedload(Appointment.service),
)


def _to_out(a: Appointment) -> AppointmentOut:
    out = AppointmentOut.model_validate(a)
    if a.slot:
        out.slot_date  = a.slot.slot_date
        out.start_time = a.slot.start_time
    if a.client:   out.client_name   = a.client.name
    if a.employee: out.employee_name = a.employee.name
    if a.service:
        out.service_name  = a.service.name
        out.service_price = float(a.service.price)
    return out


@router.post("", response_model=AppointmentOut, status_code=201)
@router.post("/", response_model=AppointmentOut, status_code=201, include_in_schema=False)
async def create_appointment(data: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    """Rota pública — usada pelo fluxo do cliente, sem autenticação."""
    result = await db.execute(
        select(AvailableSlot).where(AvailableSlot.id == data.slot_id).with_for_update()
    )
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(404, "Slot não encontrado.")
    if slot.status != "available":
        raise HTTPException(409, "Este horário não está mais disponível.")
    slot.status = "booked"
    appointment = Appointment(
        slot_id=data.slot_id, client_id=data.client_id,
        employee_id=slot.employee_id, service_id=data.service_id,
        notes=data.notes, status="confirmed",
    )
    db.add(appointment)
    await db.commit()
    result = await db.execute(
        select(Appointment).options(*_RELATIONS).where(Appointment.id == appointment.id)
    )
    return _to_out(result.unique().scalar_one())


@router.get("", response_model=list[AppointmentOut])
@router.get("/", response_model=list[AppointmentOut], include_in_schema=False)
async def list_appointments(
    request: Request,
    client_id: str | None = None,
    employee_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # permite requisição sem cookie (cliente consultando os próprios agendamentos)
    try:
        current = await get_current_user(request, db)
        is_auth = True
    except Exception:
        is_auth = False
        current = None

    q = select(Appointment).options(*_RELATIONS).order_by(Appointment.created_at.desc())

    if client_id:
        # rota pública: cliente filtra pelos próprios
        q = q.where(Appointment.client_id == client_id)
    elif is_auth and current.role == "owner":

        est_ids = await get_establishment_ids(
            db,
            current.id,
        )

        emp_res = await db.execute(
            select(Employee.id).where(
                Employee.establishment_id.in_(est_ids)
            )
        )

        emp_ids = [row[0] for row in emp_res.all()]

        q = q.where(
            Appointment.employee_id.in_(emp_ids)
        )

        if employee_id:
            q = q.where(
                Appointment.employee_id == employee_id
            )
    elif employee_id:
        q = q.where(Appointment.employee_id == employee_id)

    result = await db.execute(q)
    return [_to_out(a) for a in result.unique().scalars().all()]


@router.patch("/{appointment_id}/cancel", response_model=AppointmentOut)
async def cancel_appointment(appointment_id, db: AsyncSession = Depends(get_db)):
    """Pública — cliente pode cancelar pelo ID."""
    result = await db.execute(
        select(Appointment).options(*_RELATIONS).where(Appointment.id == appointment_id)
    )
    a = result.unique().scalar_one_or_none()
    if not a:
        raise HTTPException(404, "Agendamento não encontrado.")
    if a.status in ("cancelled", "completed"):
        raise HTTPException(409, f"Agendamento já está {a.status}.")
    a.status = "cancelled"
    if a.slot:
        a.slot.status = "available"
    await db.commit()
    result = await db.execute(
        select(Appointment).options(*_RELATIONS).where(Appointment.id == appointment_id)
    )
    return _to_out(result.unique().scalar_one())
