from datetime import datetime, timedelta, timezone
import uuid
import bcrypt
from jose import jwt, JWTError
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.user import User, user_establishments

COOKIE_NAME = "access_token"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": expire},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado.")


async def get_establishment_ids(db: AsyncSession, user_id) -> list[uuid.UUID]:
    result = await db.execute(
        select(user_establishments.c.establishment_id)
        .where(user_establishments.c.user_id == user_id)
    )
    return [row[0] for row in result.all()]


async def get_current_user(request: Request, db: AsyncSession) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado.")
    payload = decode_token(token)
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user or not user.active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário inativo ou não encontrado.")
    return user


def require_superadmin(user: User):
    if user.role != "superadmin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito ao superadmin.")
