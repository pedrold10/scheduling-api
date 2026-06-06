import uuid
from datetime import datetime, date, time
from sqlalchemy import String, Date, Time, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AvailableSlot(Base):
    """
    Representa uma janela concreta de atendimento para um funcionário
    em uma data e horário específicos.

    Status:
        available - livre para agendamento
        booked    - já tem um Appointment vinculado
        blocked   - bloqueado manualmente (folga, feriado, etc.)
    """
    __tablename__ = "available_slots"
    __table_args__ = (
        UniqueConstraint("employee_id", "slot_date", "start_time", name="uq_slot_employee_date_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    slot_date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    status: Mapped[str] = mapped_column(String(20), default="available")  # available | booked | blocked
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee: Mapped["Employee"] = relationship(back_populates="available_slots")
    appointment: Mapped["Appointment | None"] = relationship(back_populates="slot", uselist=False)
