from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientOut

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=ClientOut, status_code=201)
async def create_client(data: ClientCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Client).where(Client.phone == data.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Telefone já cadastrado.")
    client = Client(**data.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/", response_model=list[ClientOut])
async def list_clients(
    phone: str | None = Query(default=None, description="Filtrar por telefone"),
    db: AsyncSession = Depends(get_db),
):
    q = select(Client)
    if phone:
        q = q.where(Client.phone == phone)
    result = await db.execute(q.order_by(Client.name))
    return result.scalars().all()


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(client_id, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Cliente não encontrado.")
    return obj
