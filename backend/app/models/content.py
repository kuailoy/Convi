from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Content(Base):
    __tablename__ = "contents"
    __table_args__ = (
        CheckConstraint("topic_order IS NULL OR topic_order >= 1", name="ck_contents_topic_order_positive"),
        CheckConstraint(
            "(topic_id IS NULL AND topic_order IS NULL) OR "
            "(topic_id IS NOT NULL AND topic_order IS NOT NULL)",
            name="ck_contents_topic_fields_together",
        ),
        CheckConstraint(
            "content_type <> 'vocabulary_item' OR "
            "(topic_id IS NOT NULL AND topic_order IS NOT NULL)",
            name="ck_vocabulary_items_require_topic",
        ),
        UniqueConstraint("topic_id", "topic_order", name="uq_contents_topic_order"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    practice_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    practice_method: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meaning: Mapped[str | None] = mapped_column(Text)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    meaning_language_code: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    topic_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("vocabulary_topics.id", ondelete="RESTRICT"), index=True
    )
    topic_order: Mapped[int | None] = mapped_column(Integer)
    topic: Mapped[VocabularyTopic | None] = relationship()
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


class VocabularyTopic(Base):
    __tablename__ = "vocabulary_topics"
    __table_args__ = (UniqueConstraint("slug", name="uq_vocabulary_topics_slug"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(150), nullable=False)
    name_fi: Mapped[str] = mapped_column(String(150), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
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
