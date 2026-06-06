import uuid
from datetime import datetime
from pydantic import BaseModel


class ServiceCreate(BaseModel):
    establishment_id: uuid.UUID
    name: str
    duration_minutes: int
    price: float


class ServiceOut(ServiceCreate):
    id: uuid.UUID
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
