import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.database import engine, Base, AsyncSessionLocal
from app.config import settings
import app.models
from app.routers import public

from app.routers import (
    auth, users,
    establishments, employees, services,
    schedule_rules, availability, clients, appointments,
)
from app.models.user import User
from app.services.auth import hash_password


async def _ensure_superadmin():
    email    = os.getenv("SUPERADMIN_EMAIL", "admin@agenda.app")
    password = os.getenv("SUPERADMIN_PASSWORD", "admin123")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        if not result.scalar_one_or_none():
            db.add(User(
                name="Superadmin",
                email=email,
                hashed_password=hash_password(password),
                role="superadmin",
            ))
            await db.commit()
            print(f"[startup] Superadmin criado: {email}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _ensure_superadmin()
    yield


app = FastAPI(
    title="Scheduling API",
    version="0.2.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(establishments.router)
app.include_router(employees.router)
app.include_router(services.router)
app.include_router(schedule_rules.router)
app.include_router(availability.router)
app.include_router(clients.router)
app.include_router(appointments.router)
app.include_router(public.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
