from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.establishment import Establishment
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.auth import get_current_user, require_superadmin, hash_password

router = APIRouter(prefix="/users", tags=["users"])


async def _load_user(db, user_id) -> User:
    result = await db.execute(
        select(User).options(selectinload(User.establishments)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Usuário não encontrado.")
    return user


def _to_out(user: User) -> UserOut:
    out = UserOut.model_validate(user)
    out.establishment_ids = [e.id for e in user.establishments]
    return out


@router.get("", response_model=list[UserOut])
@router.get("/", response_model=list[UserOut], include_in_schema=False)
async def list_users(request: Request, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    require_superadmin(current)
    result = await db.execute(
        select(User).options(selectinload(User.establishments)).order_by(User.name)
    )
    return [_to_out(u) for u in result.unique().scalars().all()]


@router.post("", response_model=UserOut, status_code=201)
@router.post("/", response_model=UserOut, status_code=201, include_in_schema=False)
async def create_user(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    require_superadmin(current)

    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "E-mail já cadastrado.")

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    if data.establishment_ids:
        res = await db.execute(
            select(Establishment).where(Establishment.id.in_(data.establishment_ids))
        )
        user.establishments = list(res.scalars().all())

    db.add(user)
    await db.commit()
    user = await _load_user(db, user.id)
    return _to_out(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(user_id, request: Request, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    require_superadmin(current)

    user = await _load_user(db, user_id)

    if data.name is not None:      user.name = data.name
    if data.email is not None:     user.email = data.email
    if data.active is not None:    user.active = data.active
    if data.password is not None:  user.hashed_password = hash_password(data.password)
    if data.establishment_ids is not None:
        res = await db.execute(
            select(Establishment).where(Establishment.id.in_(data.establishment_ids))
        )
        user.establishments = list(res.scalars().all())

    await db.commit()
    user = await _load_user(db, user.id)
    return _to_out(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id, request: Request, db: AsyncSession = Depends(get_db)):
    current = await get_current_user(request, db)
    require_superadmin(current)
    user = await _load_user(db, user_id)
    await db.delete(user)
    await db.commit()
