from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MenuImage(Base):
    __tablename__ = "menu_images"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="camera")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    items: Mapped[list[MenuImageItem]] = relationship(back_populates="menu_image")


class MenuImageItem(Base):
    __tablename__ = "menu_image_items"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )
    menu_image_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("menu_images.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    estimated_calories: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_protein_g: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_carbs_g: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_fat_g: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    menu_image: Mapped[MenuImage] = relationship(back_populates="items")
