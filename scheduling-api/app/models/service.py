import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.employee import employee_services


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    establishment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("establishments.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    establishment: Mapped["Establishment"] = relationship(back_populates="services")
    employees: Mapped[list["Employee"]] = relationship(secondary=employee_services, back_populates="services")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service")
