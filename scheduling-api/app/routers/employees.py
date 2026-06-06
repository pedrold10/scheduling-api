from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeOut

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/", response_model=EmployeeOut, status_code=201)
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    employee = Employee(**data.model_dump())
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee


@router.get("/", response_model=list[EmployeeOut])
async def list_employees(establishment_id: str | None = None, db: AsyncSession = Depends(get_db)):
    q = select(Employee).where(Employee.active.is_(True))
    if establishment_id:
        q = q.where(Employee.establishment_id == establishment_id)
    result = await db.execute(q.order_by(Employee.name))
    return result.scalars().all()


@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Funcionário não encontrado.")
    return obj
