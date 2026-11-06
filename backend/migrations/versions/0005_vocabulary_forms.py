"""Store reviewed vocabulary forms and usage targets.

Revision ID: 0005_vocabulary_forms
Revises: 0004_vocabulary_topic_integrity
Create Date: 2026-11-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_vocabulary_forms"
down_revision: Union[str, None] = "0004_vocabulary_topic_integrity"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vocabulary_forms",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column("form", sa.Text(), nullable=False),
        sa.Column("grammatical_label", sa.String(length=100), server_default="", nullable=False),
        sa.Column("target_type", sa.String(length=30), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(length=20), server_default="reviewed", nullable=False),
        sa.Column("source_note", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "target_type IN ('inflected_form', 'invariant', 'related_form', 'governed_pattern')",
            name="ck_vocabulary_forms_target_type",
        ),
        sa.CheckConstraint("display_order >= 1", name="ck_vocabulary_forms_display_order_positive"),
        sa.ForeignKeyConstraint(["content_id"], ["contents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "content_id",
            "form",
            "grammatical_label",
            "target_type",
            name="uq_vocabulary_forms_content_form_label_type",
        ),
    )
    op.create_index("ix_vocabulary_forms_content_id", "vocabulary_forms", ["content_id"])


def downgrade() -> None:
    op.drop_index("ix_vocabulary_forms_content_id", table_name="vocabulary_forms")
    op.drop_table("vocabulary_forms")
