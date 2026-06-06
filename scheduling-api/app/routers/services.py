from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceOut

router = APIRouter(prefix="/services", tags=["services"])


@router.post("/", response_model=ServiceOut, status_code=201)
async def create_service(data: ServiceCreate, db: AsyncSession = Depends(get_db)):
    service = Service(**data.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.get("/", response_model=list[ServiceOut])
async def list_services(establishment_id: str | None = None, db: AsyncSession = Depends(get_db)):
    q = select(Service).where(Service.active.is_(True))
    if establishment_id:
        q = q.where(Service.establishment_id == establishment_id)
    result = await db.execute(q.order_by(Service.name))
    return result.scalars().all()
