import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "owner"
    establishment_ids: list[uuid.UUID] = []


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    active: bool | None = None
    establishment_ids: list[uuid.UUID] | None = None


class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    active: bool
    created_at: datetime
    establishment_ids: list[uuid.UUID] = []

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class MeOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    establishment_ids: list[uuid.UUID] = []

    model_config = {"from_attributes": True}
