from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Content(Base):
    __tablename__ = "contents"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    practice_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    practice_method: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meaning: Mapped[str | None] = mapped_column(Text)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    cefr_level: Mapped[str | None] = mapped_column(String(2))
    context: Mapped[str | None] = mapped_column(String(100))
    register: Mapped[str | None] = mapped_column(String(20))
    source_note: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    content_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    generation_model: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ContentProgress(Base):
    __tablename__ = "content_progress"
    __table_args__ = (CheckConstraint("practice_count >= 0", name="ck_content_progress_count_nonnegative"),)

    content_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("contents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")
    practice_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_practiced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
