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


class VocabularyForm(Base):
    """A reviewed learning target associated with a vocabulary item."""

    __tablename__ = "vocabulary_forms"
    __table_args__ = (
        UniqueConstraint(
            "content_id",
            "form",
            "grammatical_label",
            "target_type",
            name="uq_vocabulary_forms_content_form_label_type",
        ),
        CheckConstraint(
            "target_type IN ('inflected_form', 'invariant', 'related_form', 'governed_pattern')",
            name="ck_vocabulary_forms_target_type",
        ),
        CheckConstraint("display_order >= 1", name="ck_vocabulary_forms_display_order_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    content_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    form: Mapped[str] = mapped_column(Text, nullable=False)
    grammatical_label: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(20), nullable=False, default="reviewed")
    source_note: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class VocabularyExample(Base):
    """A Finnish example sentence and translation for a vocabulary item."""

    __tablename__ = "vocabulary_examples"
    __table_args__ = (
        UniqueConstraint(
            "content_id",
            "normalized_sentence",
            name="uq_vocabulary_examples_content_normalized_sentence",
        ),
        CheckConstraint(
            "validation_status IN ('auto_valid', 'needs_review', 'human_approved', 'rejected')",
            name="ck_vocabulary_examples_validation_status",
        ),
        CheckConstraint("difficulty IN ('A1', 'A2')", name="ck_vocabulary_examples_difficulty"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    content_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    finnish_sentence: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_sentence: Mapped[str] = mapped_column(Text, nullable=False)
    english_translation: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(2), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(20), nullable=False)
    validation_notes: Mapped[str | None] = mapped_column(Text)
    generation_model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class VocabularyExampleTarget(Base):
    """Links an example to its primary target and optional reinforcement targets."""

    __tablename__ = "vocabulary_example_targets"
    __table_args__ = (
        CheckConstraint("role IN ('primary', 'reinforcement')", name="ck_vocabulary_example_targets_role"),
        CheckConstraint(
            "target_validation_status IN ('auto_valid', 'needs_review', 'human_approved', 'rejected')",
            name="ck_vocabulary_example_targets_validation_status",
        ),
    )

    example_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("vocabulary_examples.id", ondelete="CASCADE"), primary_key=True
    )
    vocabulary_form_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("vocabulary_forms.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="primary")
    target_validation_status: Mapped[str] = mapped_column(String(20), nullable=False)
    target_validation_notes: Mapped[str | None] = mapped_column(Text)
