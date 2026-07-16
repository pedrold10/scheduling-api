from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models.establishment import Establishment

from app.schemas.establishment import EstablishmentOut
from app.models.employee import Employee
from app.schemas.employee import EmployeeOut
from app.models.service import Service
from app.schemas.service import ServiceOut
from datetime import date

from sqlalchemy.orm import joinedload

from app.models.available_slot import AvailableSlot
from app.models.appointment import Appointment
from app.models.client import Client

from app.schemas.appointment import (
    AppointmentCreate,
    PublicAppointmentCreate,
    AppointmentOut,
)

from sqlalchemy.orm import selectinload

from app.schemas.public import PublicEstablishment

router = APIRouter(
    prefix="/public",
    tags=["public"],
)


async def get_establishment_by_slug(
    slug: str,
    db: AsyncSession,
) -> Establishment:
    """
    Busca um estabelecimento público pelo slug.
    """

    result = await db.execute(
        select(Establishment).where(
            Establishment.slug == slug
        )
    )

    establishment = result.scalar_one_or_none()

    if establishment is None:
        raise HTTPException(
            status_code=404,
            detail="Estabelecimento não encontrado.",
        )

    if not establishment.public_enabled:
        raise HTTPException(
            status_code=403,
            detail="Agendamento online desativado.",
        )

    return establishment


@router.get(
    "/{slug}",
    response_model=PublicEstablishment,
)
async def public_establishment(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(

        select(Establishment)

        .options(

            selectinload(
                Establishment.employees
            ),

            selectinload(
                Establishment.services
            ),

        )

        .where(
            Establishment.slug == slug
        )

    )

    establishment = result.scalar_one_or_none()

    if establishment is None:
        raise HTTPException(
            404,
            "Estabelecimento não encontrado.",
        )

    if not establishment.public_enabled:
        raise HTTPException(
            403,
            "Agendamento indisponível.",
        )

    establishment.employees = [
        e
        for e in establishment.employees
        if e.active
    ]

    establishment.services = [
        s
        for s in establishment.services
        if s.active
    ]

    return establishment

@router.get(
    "/{slug}/employees",
    response_model=list[EmployeeOut],
)
async def public_employees(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista apenas os funcionários ativos
    daquele estabelecimento.
    """

    establishment = await get_establishment_by_slug(
        slug,
        db,
    )

    result = await db.execute(
        select(Employee)
        .where(
            Employee.establishment_id == establishment.id,
            Employee.active.is_(True),
        )
        .order_by(Employee.name)
    )

    return result.scalars().all()

@router.get(
    "/{slug}/services",
    response_model=list[ServiceOut],
)
async def public_services(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista os serviços públicos do estabelecimento.
    """

    establishment = await get_establishment_by_slug(
        slug,
        db,
    )

    result = await db.execute(
        select(Service)
        .where(
            Service.establishment_id == establishment.id,
            Service.active.is_(True),
        )
        .order_by(Service.name)
    )

    return result.scalars().all()

@router.get(
    "/{slug}/slots",
)
async def public_slots(
    slug: str,
    employee_id: str,
    day: date,
    db: AsyncSession = Depends(get_db),
):
    establishment = await get_establishment_by_slug(
        slug,
        db,
    )

    employee = await db.get(
        Employee,
        employee_id,
    )

    if employee is None:
        raise HTTPException(
            404,
            "Funcionário não encontrado.",
        )

    if employee.establishment_id != establishment.id:
        raise HTTPException(
            403,
            "Funcionário não pertence ao estabelecimento.",
        )

    result = await db.execute(
        select(AvailableSlot)
        .where(
            AvailableSlot.employee_id == employee.id,
            AvailableSlot.slot_date == day,
            AvailableSlot.status == "available",
        )
        .order_by(AvailableSlot.start_time)
    )

    return result.scalars().all()

@router.post(
    "/{slug}/appointments",
    response_model=AppointmentOut,
    status_code=201,
)
async def public_create_appointment(
    slug: str,
    data: PublicAppointmentCreate,
    db: AsyncSession = Depends(get_db),
):
    establishment = await get_establishment_by_slug(
        slug,
        db,
    )

    result = await db.execute(
        select(AvailableSlot)
        .options(
            joinedload(AvailableSlot.employee)
            .joinedload(Employee.services)
        )
        .where(
            AvailableSlot.id == data.slot_id
        )
        .with_for_update()
    )

    slot = result.scalar_one_or_none()

    if slot is None:
        raise HTTPException(
            404,
            "Horário não encontrado.",
        )

    if slot.status != "available":
        raise HTTPException(
            409,
            "Este horário não está mais disponível.",
        )

    if slot.employee.establishment_id != establishment.id:
        raise HTTPException(
            403,
            "Este horário pertence a outro estabelecimento.",
        )

    service = await db.get(
        Service,
        data.service_id,
    )

    if service is None:
        raise HTTPException(
            404,
            "Serviço não encontrado.",
        )

    if service.establishment_id != establishment.id:
        raise HTTPException(
            403,
            "Serviço pertence a outro estabelecimento.",
        )

    if not service.active:
        raise HTTPException(
            400,
            "Serviço indisponível.",
        )

    if service not in slot.employee.services:
        raise HTTPException(
            400,
            "Este profissional não realiza este serviço.",
        )

    result = await db.execute(
        select(Client).where(
            Client.phone == data.phone
        )
    )

    client = result.scalar_one_or_none()

    if client is None:
        client = Client(
            name=data.name,
            phone=data.phone,
            email=data.email,
        )

        db.add(client)

        await db.flush()

    appointment = Appointment(
        slot_id=slot.id,
        client_id=client.id,
        employee_id=slot.employee_id,
        service_id=service.id,
        notes=data.notes,
        status="confirmed",
    )

    slot.status = "booked"

    db.add(appointment)

    await db.commit()

    result = await db.execute(
        select(Appointment)
        .options(
            joinedload(Appointment.slot),
            joinedload(Appointment.client),
            joinedload(Appointment.employee),
            joinedload(Appointment.service),
        )
        .where(
            Appointment.id == appointment.id
        )
    )

    appointment = result.unique().scalar_one()

    return _to_out(appointment)

def _to_out(a: Appointment) -> AppointmentOut:
    out = AppointmentOut.model_validate(a)

    if a.slot:
        out.slot_date = a.slot.slot_date
        out.start_time = a.slot.start_time

    if a.client:
        out.client_name = a.client.name

    if a.employee:
        out.employee_name = a.employee.name

    if a.service:
        out.service_name = a.service.name
        out.service_price = float(a.service.price)

    return out