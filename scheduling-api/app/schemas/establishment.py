import uuid
from datetime import datetime

from uuid import UUID
from pydantic import BaseModel


class EstablishmentCreate(BaseModel):
    name: str
    type: str
    phone: str | None = None
    address: str | None = None


class EstablishmentUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    phone: str | None = None
    address: str | None = None
    public_enabled: bool | None = None


class EstablishmentOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    type: str
    phone: str | None
    address: str | None
    public_enabled: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }