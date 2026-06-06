import uuid
from datetime import datetime
from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    establishment_id: uuid.UUID
    name: str
    role: str | None = None
    phone: str | None = None


class EmployeeOut(EmployeeCreate):
    id: uuid.UUID
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
