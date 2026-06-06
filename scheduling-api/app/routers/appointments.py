from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.appointment import Appointment
from app.models.available_slot import AvailableSlot
from app.schemas.appointment import AppointmentCreate, AppointmentOut

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentOut, status_code=201)
async def create_appointment(data: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    # Busca o slot com lock para evitar double booking
    result = await db.execute(
        select(AvailableSlot)
        .where(AvailableSlot.id == data.slot_id)
        .with_for_update()
    )
    slot = result.scalar_one_or_none()

    if not slot:
        raise HTTPException(404, "Slot não encontrado.")
    if slot.status != "available":
        raise HTTPException(409, "Este horário não está mais disponível.")

    slot.status = "booked"

    appointment = Appointment(
        slot_id=data.slot_id,
        client_id=data.client_id,
        employee_id=slot.employee_id,
        service_id=data.service_id,
        notes=data.notes,
        status="confirmed",
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    await db.refresh(slot)

    out = AppointmentOut.model_validate(appointment)
    out.slot_date = slot.slot_date
    out.start_time = slot.start_time
    return out


@router.get("/", response_model=list[AppointmentOut])
async def list_appointments(
    client_id: str | None = None,
    employee_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Appointment)
    if client_id:
        q = q.where(Appointment.client_id == client_id)
    if employee_id:
        q = q.where(Appointment.employee_id == employee_id)
    result = await db.execute(q.order_by(Appointment.created_at.desc()))
    return result.scalars().all()


@router.patch("/{appointment_id}/cancel", response_model=AppointmentOut)
async def cancel_appointment(appointment_id, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(404, "Agendamento não encontrado.")
    if appointment.status in ("cancelled", "completed"):
        raise HTTPException(409, f"Agendamento já está {appointment.status}.")

    appointment.status = "cancelled"

    # Libera o slot
    slot_result = await db.execute(select(AvailableSlot).where(AvailableSlot.id == appointment.slot_id))
    slot = slot_result.scalar_one_or_none()
    if slot:
        slot.status = "available"

    await db.commit()
    await db.refresh(appointment)
    return appointment
