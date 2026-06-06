from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
import app.models  # noqa: F401 - garante que todos os models são registrados

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
    # Cria as tabelas ao iniciar (use Alembic em produção)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Scheduling API",
    description="MVP de agendamentos para espaços de estética",
    version="0.1.0",
    lifespan=lifespan,
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
