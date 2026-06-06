import uuid
from datetime import datetime
from pydantic import BaseModel


class ClientCreate(BaseModel):
    name: str
    phone: str
    email: str | None = None


class ClientOut(ClientCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
