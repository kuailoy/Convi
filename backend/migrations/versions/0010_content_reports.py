"""Store problem reports from the app; new form targets default to active.

Revision ID: 0010_content_reports
Revises: 0009_order_itse_reflexive_forms
Create Date: 2026-11-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0010_content_reports"
down_revision: Union[str, None] = "0009_order_itse_reflexive_forms"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "content_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column("vocabulary_form_id", sa.Uuid(), nullable=True),
        sa.Column("example_id", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.String(length=30), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="open", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "reason IN ('finnish_sentence', 'translation', 'word_form', 'other')",
            name="ck_content_reports_reason",
        ),
        sa.CheckConstraint(
            "status IN ('open', 'resolved', 'dismissed')",
            name="ck_content_reports_status",
        ),
        sa.ForeignKeyConstraint(["content_id"], ["contents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vocabulary_form_id"], ["vocabulary_forms.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["example_id"], ["vocabulary_examples.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_reports_content_id", "content_reports", ["content_id"])
    op.create_index("ix_content_reports_vocabulary_form_id", "content_reports", ["vocabulary_form_id"])
    op.create_index("ix_content_reports_example_id", "content_reports", ["example_id"])

    # Generated targets are not reviewed by a person; they start as active.
    op.alter_column("vocabulary_forms", "review_status", server_default="active")


def downgrade() -> None:
    op.alter_column("vocabulary_forms", "review_status", server_default="reviewed")
    op.drop_index("ix_content_reports_example_id", table_name="content_reports")
    op.drop_index("ix_content_reports_vocabulary_form_id", table_name="content_reports")
    op.drop_index("ix_content_reports_content_id", table_name="content_reports")
    op.drop_table("content_reports")
