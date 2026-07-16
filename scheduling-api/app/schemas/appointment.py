import uuid
from datetime import datetime, date, time
from pydantic import BaseModel, EmailStr


class AppointmentCreate(BaseModel):
    slot_id: uuid.UUID
    client_id: uuid.UUID
    service_id: uuid.UUID
    notes: str | None = None


class PublicAppointmentCreate(BaseModel):
    slot_id: uuid.UUID

    service_id: uuid.UUID

    name: str

    phone: str

    email: EmailStr | None = None

    notes: str | None = None

class AppointmentOut(BaseModel):
    id: uuid.UUID
    slot_id: uuid.UUID
    client_id: uuid.UUID
    employee_id: uuid.UUID
    service_id: uuid.UUID
    status: str
    notes: str | None
    created_at: datetime

    # campos desnormalizados para conveniência do frontend
    slot_date: date | None = None
    start_time: time | None = None
    client_name: str | None = None
    employee_name: str | None = None
    service_name: str | None = None
    service_price: float | None = None

    model_config = {"from_attributes": True}
