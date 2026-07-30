from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.employee import Employee
from app.models.service import Service
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.services.auth import (
    get_current_user,
    get_establishment_ids,
)
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("", response_model=EmployeeOut, status_code=201)
@router.post("/", response_model=EmployeeOut, status_code=201, include_in_schema=False)
async def create_employee(request: Request, data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)

    if current.role == "owner":
        allowed = await get_establishment_ids(db, current.id)

        if data.establishment_id not in allowed:
            raise HTTPException(
                403,
                "Estabelecimento não pertence a você."
            )
    employee = Employee(
        establishment_id=data.establishment_id,
        name=data.name,
        role=data.role,
        phone=data.phone,
    )
    result = await db.execute(
        select(Service).where(
            Service.id.in_(data.service_ids),
            Service.establishment_id == data.establishment_id
        )
    )

    services = result.scalars().all()

    print(data.service_ids)
    print(services)

    employee.services.extend(services)
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    result = await db.execute(
        select(Employee)
        .options(selectinload(Employee.services))
        .where(Employee.id == employee.id)
    )

    return result.scalar_one()


@router.get("", response_model=list[EmployeeOut])
@router.get("/", response_model=list[EmployeeOut], include_in_schema=False)
async def list_employees(request: Request, establishment_id: str | None = None, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)

    q = (
        select(Employee)
        .options(selectinload(Employee.services))
        .where(Employee.active.is_(True))
    )

    if current.role == "owner":
        allowed = await get_establishment_ids(
            db,
            current.id,
        )

        q = q.where(
            Employee.establishment_id.in_(allowed)
        )

    if establishment_id:
        q = q.where(
            Employee.establishment_id == establishment_id
        )

    result = await db.execute(
        q.order_by(Employee.name)
    )

    return result.scalars().all()

@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id, request: Request, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    result = await db.execute(
        select(Employee)
        .options(selectinload(Employee.services))
        .where(Employee.id == employee_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Funcionário não encontrado.")

    if current.role == "owner":
        allowed = await get_establishment_ids(db, current.id)

        if obj.establishment_id not in allowed:
            raise HTTPException(403, "Acesso não autorizado.")

    return obj
