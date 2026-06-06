import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Appointment(Base):
    """
    Status:
        pending    - aguardando confirmação
        confirmed  - confirmado
        cancelled  - cancelado
        completed  - atendimento realizado
    """
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("available_slots.id", ondelete="RESTRICT"), unique=True)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"))
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id", ondelete="RESTRICT"))
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    slot: Mapped["AvailableSlot"] = relationship(back_populates="appointment")
    client: Mapped["Client"] = relationship(back_populates="appointments")
    employee: Mapped["Employee"] = relationship(back_populates="appointments")
    service: Mapped["Service"] = relationship(back_populates="appointments")
