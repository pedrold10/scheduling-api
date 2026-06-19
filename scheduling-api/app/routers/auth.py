from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, MeOut
from app.services.auth import (
    verify_password, create_token, get_current_user, COOKIE_NAME
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_OPTS = dict(
    key=COOKIE_NAME,
    httponly=True,
    samesite="lax",
    secure=False,   # True em produção com HTTPS
    max_age=settings.jwt_expire_minutes * 60,
)


@router.post("/login")
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "E-mail ou senha incorretos.")
    if not user.active:
        raise HTTPException(403, "Conta desativada.")
    token = create_token(str(user.id), user.role)
    response.set_cookie(**COOKIE_OPTS, value=token)
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "establishment_ids": [str(e.id) for e in user.establishments],
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=MeOut)
async def me(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    out = MeOut.model_validate(user)
    out.establishment_ids = [e.id for e in user.establishments]
    return out
