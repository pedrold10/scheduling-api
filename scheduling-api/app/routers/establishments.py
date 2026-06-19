from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.establishment import Establishment
from app.schemas.establishment import EstablishmentCreate, EstablishmentOut
from app.services.auth import get_current_user, require_superadmin

router = APIRouter(prefix="/establishments", tags=["establishments"])


@router.post("", response_model=EstablishmentOut, status_code=201)
@router.post("/", response_model=EstablishmentOut, status_code=201, include_in_schema=False)
async def create_establishment(request: Request, data: EstablishmentCreate, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    require_superadmin(current)
    establishment = Establishment(**data.model_dump())
    db.add(establishment)
    await db.commit()
    await db.refresh(establishment)
    return establishment


@router.get("", response_model=list[EstablishmentOut])
@router.get("/", response_model=list[EstablishmentOut], include_in_schema=False)
async def list_establishments(request: Request, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    q = select(Establishment).order_by(Establishment.name)
    if current.role == "owner":
        ids = [e.id for e in current.establishments]
        q = q.where(Establishment.id.in_(ids))
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{establishment_id}", response_model=EstablishmentOut)
async def get_establishment(establishment_id, request: Request, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Estabelecimento não encontrado.")
    if current.role == "owner" and obj.id not in [e.id for e in current.establishments]:
        raise HTTPException(403, "Acesso não autorizado.")
    return obj
