from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NutritionTarget(Base):
    __tablename__ = "nutrition_targets"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    calories: Mapped[int] = mapped_column(Integer, nullable=False, default=2200)
    protein_g: Mapped[int] = mapped_column(Integer, nullable=False, default=150)
    carbs_g: Mapped[int] = mapped_column(Integer, nullable=False, default=250)
    fat_g: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    water_ml: Mapped[int] = mapped_column(Integer, nullable=False, default=2500)
    fiber_g: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    sodium_mg: Mapped[int] = mapped_column(Integer, nullable=False, default=2000)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="nutrition_target")
