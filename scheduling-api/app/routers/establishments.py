import re
import unicodedata
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.establishment import Establishment
from app.schemas.establishment import EstablishmentCreate, EstablishmentOut
from app.services.auth import (
    get_current_user,
    get_establishment_ids,
    require_superadmin
)

router = APIRouter(prefix="/establishments", tags=["establishments"])

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text

@router.post("", response_model=EstablishmentOut, status_code=201)
@router.post("/", response_model=EstablishmentOut, status_code=201, include_in_schema=False)
async def create_establishment(
    request: Request,
    data: EstablishmentCreate,
    db: AsyncSession = Depends(get_db)
):
    current = await get_current_user(request, db)
    require_superadmin(current)

    base_slug = slugify(data.name)
    slug = base_slug

    i = 2

    while True:
        result = await db.execute(
            select(Establishment).where(
                Establishment.slug == slug
            )
        )

        if result.scalar_one_or_none() is None:
            break

        slug = f"{base_slug}-{i}"
        i += 1

    establishment = Establishment(
        **data.model_dump(),
        slug=slug
    )

    db.add(establishment)

    await db.commit()

    await db.refresh(establishment)

    return establishment

@router.get("")
async def list_establishments(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    current = await get_current_user(request, db)

    q = select(Establishment)

    if current.role == "owner":
        allowed = await get_establishment_ids(db, current.id)
        q = q.where(Establishment.id.in_(allowed))

    result = await db.execute(q)
    return result.scalars().all()

@router.get("/by-slug/{slug}", response_model=EstablishmentOut)
async def get_establishment_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Establishment).where(
            Establishment.slug == slug
        )
    )

    establishment = result.scalar_one_or_none()

    if establishment is None:
        raise HTTPException(404, "Estabelecimento não encontrado.")

    return establishment

@router.get("/{establishment_id}", response_model=EstablishmentOut)
async def get_establishment(
    establishment_id,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    current = await get_current_user(request, db)

    result = await db.execute(
        select(Establishment).where(
            Establishment.id == establishment_id
        )
    )

    establishment = result.scalar_one_or_none()

    if establishment is None:
        raise HTTPException(
            404,
            "Estabelecimento não encontrado."
        )

    if current.role == "owner":

        allowed = await get_establishment_ids(
            db,
            current.id,
        )

        if establishment.id not in allowed:
            raise HTTPException(
                403,
                "Sem acesso."
            )

    return establishment