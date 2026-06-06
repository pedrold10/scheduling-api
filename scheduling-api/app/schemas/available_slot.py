import uuid
from datetime import date, time, datetime
from pydantic import BaseModel


class AvailableSlotOut(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    slot_date: date
    start_time: time
    end_time: time
    status: str

    model_config = {"from_attributes": True}
