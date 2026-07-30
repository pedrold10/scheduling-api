import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.service import ServiceSimple

class EmployeeCreate(BaseModel):
    establishment_id: uuid.UUID
    name: str
    role: str | None = None
    phone: str | None = None
    service_ids: list[uuid.UUID] = []



class EmployeeOut(BaseModel):
    id: uuid.UUID
    establishment_id: uuid.UUID
    name: str
    role: str | None
    phone: str | None
    active: bool
    created_at: datetime

    services: list[ServiceSimple] = []

    model_config = ConfigDict(from_attributes=True)