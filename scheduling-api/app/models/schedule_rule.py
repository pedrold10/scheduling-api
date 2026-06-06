import uuid
from datetime import datetime, time, date
from sqlalchemy import String, Integer, Time, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ScheduleRule(Base):
    """
    Define a disponibilidade recorrente de um funcionário.

    Exemplo: segunda a sexta (days_of_week=[0,1,2,3,4]),
    das 08:00 às 18:00, com slots de 30 minutos.

    days_of_week é armazenado como string CSV: "0,1,2,3,4"
    0=segunda ... 6=domingo (padrão Python weekday())
    """
    __tablename__ = "schedule_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    days_of_week: Mapped[str] = mapped_column(String(20))  # ex: "0,1,2,3,4"
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    valid_from: Mapped[date] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee: Mapped["Employee"] = relationship(back_populates="schedule_rules")

    @property
    def days_list(self) -> list[int]:
        return [int(d) for d in self.days_of_week.split(",") if d.strip()]
