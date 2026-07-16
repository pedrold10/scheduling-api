from pydantic import BaseModel
from uuid import UUID

from app.schemas.employee import EmployeeOut
from app.schemas.service import ServiceOut


class PublicEstablishment(BaseModel):
    id: UUID
    name: str
    slug: str
    phone: str | None
    address: str | None

    employees: list[EmployeeOut]

    services: list[ServiceOut]

    model_config = {
        "from_attributes": True
    }


