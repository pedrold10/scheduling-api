from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models  # noqa: F401

from app.routers import (
    establishments,
    employees,
    services,
    schedule_rules,
    availability,
    clients,
    appointments,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Scheduling API",
    description="MVP de agendamentos para espaços de estética",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(establishments.router)
app.include_router(employees.router)
app.include_router(services.router)
app.include_router(schedule_rules.router)
app.include_router(availability.router)
app.include_router(clients.router)
app.include_router(appointments.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
