import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, func, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


# Tabela N:N associando owners aos seus estabelecimentos
user_establishments = Table(
    "user_establishments",
    Base.metadata,
    Column("user_id",            ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("establishment_id",   ForeignKey("establishments.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """
    Roles:
        superadmin  — acesso total, gerencia owners
        owner       — acesso filtrado aos próprios estabelecimentos
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="owner")  # superadmin | owner
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    establishments: Mapped[list["Establishment"]] = relationship(
        secondary=user_establishments,
        back_populates="owners",
    )
