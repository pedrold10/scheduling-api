import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Establishment(Base):
    __tablename__ = "establishments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120))
    type: Mapped[str] = mapped_column(String(40))  # barbershop, salon, spa, etc.
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employees: Mapped[list["Employee"]] = relationship(back_populates="establishment", cascade="all, delete-orphan")
    services: Mapped[list["Service"]] = relationship(back_populates="establishment", cascade="all, delete-orphan")
    owners: Mapped[list["User"]] = relationship(secondary="user_establishments", back_populates="establishments")
