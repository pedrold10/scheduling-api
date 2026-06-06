import uuid
from datetime import datetime, time, date
from pydantic import BaseModel, field_validator, model_validator


class ScheduleRuleCreate(BaseModel):
    employee_id: uuid.UUID
    days_of_week: list[int]        # [0,1,2,3,4] → seg a sex
    start_time: time
    end_time: time
    slot_duration_minutes: int = 30
    valid_from: date
    valid_until: date | None = None

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, v):
        if not v:
            raise ValueError("Informe pelo menos um dia da semana.")
        if any(d < 0 or d > 6 for d in v):
            raise ValueError("Dias devem estar entre 0 (seg) e 6 (dom).")
        return sorted(set(v))

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time deve ser maior que start_time.")
        return self

    def days_as_csv(self) -> str:
        return ",".join(str(d) for d in self.days_of_week)


class ScheduleRuleOut(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    days_of_week: list[int]
    start_time: time
    end_time: time
    slot_duration_minutes: int
    valid_from: date
    valid_until: date | None
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("days_of_week", mode="before")
    @classmethod
    def parse_days(cls, v):
        if isinstance(v, str):
            return [int(d) for d in v.split(",") if d.strip()]
        return v
