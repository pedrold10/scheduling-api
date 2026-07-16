from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceOut
from app.services.auth import (
    get_current_user,
    get_establishment_ids,
)

router = APIRouter(prefix="/services", tags=["services"])




@router.post("", response_model=ServiceOut, status_code=201)
@router.post("/", response_model=ServiceOut, status_code=201, include_in_schema=False)
async def create_service(request: Request, data: ServiceCreate, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    if current.role == "owner":
        allowed = await get_establishment_ids(
            db,
            current.id,
        )

    if data.establishment_id not in allowed:
        raise HTTPException(403, "Estabelecimento não pertence a você.")
    service = Service(**data.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.get("", response_model=list[ServiceOut])
@router.get("/", response_model=list[ServiceOut], include_in_schema=False)
async def list_services(request: Request, establishment_id: str | None = None, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    q = select(Service).where(Service.active.is_(True))
    if current.role == "owner":
        allowed = await get_establishment_ids(
            db,
            current.id,
        )
        q = q.where(Service.establishment_id.in_(allowed))
    if establishment_id:
        q = q.where(Service.establishment_id == establishment_id)
    result = await db.execute(q.order_by(Service.name))
    return result.scalars().all()
