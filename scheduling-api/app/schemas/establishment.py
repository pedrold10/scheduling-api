import uuid
from datetime import datetime
from pydantic import BaseModel


class EstablishmentCreate(BaseModel):
    name: str
    type: str
    phone: str | None = None
    address: str | None = None


class EstablishmentOut(EstablishmentCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
