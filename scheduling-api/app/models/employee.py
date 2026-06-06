import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Table, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


employee_services = Table(
    "employee_services",
    Base.metadata,
    Column("employee_id", ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
)


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    establishment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("establishments.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str | None] = mapped_column(String(80))  # barbeiro, cabeleireiro, manicure…
    phone: Mapped[str | None] = mapped_column(String(20))
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    establishment: Mapped["Establishment"] = relationship(back_populates="employees")
    schedule_rules: Mapped[list["ScheduleRule"]] = relationship(back_populates="employee", cascade="all, delete-orphan")
    available_slots: Mapped[list["AvailableSlot"]] = relationship(back_populates="employee", cascade="all, delete-orphan")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="employee")
    services: Mapped[list["Service"]] = relationship(secondary=employee_services, back_populates="employees")
