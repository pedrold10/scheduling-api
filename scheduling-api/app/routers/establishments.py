from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.establishment import Establishment
from app.schemas.establishment import EstablishmentCreate, EstablishmentOut

router = APIRouter(prefix="/establishments", tags=["establishments"])


@router.post("/", response_model=EstablishmentOut, status_code=201)
async def create_establishment(data: EstablishmentCreate, db: AsyncSession = Depends(get_db)):
    establishment = Establishment(**data.model_dump())
    db.add(establishment)
    await db.commit()
    await db.refresh(establishment)
    return establishment


@router.get("/", response_model=list[EstablishmentOut])
async def list_establishments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Establishment).order_by(Establishment.name))
    return result.scalars().all()


@router.get("/{establishment_id}", response_model=EstablishmentOut)
async def get_establishment(establishment_id, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Estabelecimento não encontrado.")
    return obj
