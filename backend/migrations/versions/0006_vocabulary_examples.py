"""Store generated vocabulary example sentences and target associations.

Revision ID: 0006_vocabulary_examples
Revises: 0005_vocabulary_forms
Create Date: 2026-11-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_vocabulary_examples"
down_revision: Union[str, None] = "0005_vocabulary_forms"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vocabulary_examples",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column("finnish_sentence", sa.Text(), nullable=False),
        sa.Column("normalized_sentence", sa.Text(), nullable=False),
        sa.Column("english_translation", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=2), nullable=False),
        sa.Column("validation_status", sa.String(length=20), nullable=False),
        sa.Column("validation_notes", sa.Text(), nullable=True),
        sa.Column("generation_model", sa.String(length=100), nullable=False),
        sa.Column("prompt_version", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "validation_status IN ('auto_valid', 'needs_review', 'human_approved', 'rejected')",
            name="ck_vocabulary_examples_validation_status",
        ),
        sa.CheckConstraint("difficulty IN ('A1', 'A2')", name="ck_vocabulary_examples_difficulty"),
        sa.ForeignKeyConstraint(["content_id"], ["contents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "content_id",
            "normalized_sentence",
            name="uq_vocabulary_examples_content_normalized_sentence",
        ),
    )
    op.create_index("ix_vocabulary_examples_content_id", "vocabulary_examples", ["content_id"])

    op.create_table(
        "vocabulary_example_targets",
        sa.Column("example_id", sa.Uuid(), nullable=False),
        sa.Column("vocabulary_form_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=20), server_default="primary", nullable=False),
        sa.Column("target_validation_status", sa.String(length=20), nullable=False),
        sa.Column("target_validation_notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "role IN ('primary', 'reinforcement')",
            name="ck_vocabulary_example_targets_role",
        ),
        sa.CheckConstraint(
            "target_validation_status IN ('auto_valid', 'needs_review', 'human_approved', 'rejected')",
            name="ck_vocabulary_example_targets_validation_status",
        ),
        sa.ForeignKeyConstraint(["example_id"], ["vocabulary_examples.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vocabulary_form_id"], ["vocabulary_forms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("example_id", "vocabulary_form_id"),
    )
    op.create_index(
        "ix_vocabulary_example_targets_vocabulary_form_id",
        "vocabulary_example_targets",
        ["vocabulary_form_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_vocabulary_example_targets_vocabulary_form_id",
        table_name="vocabulary_example_targets",
    )
    op.drop_table("vocabulary_example_targets")
    op.drop_index("ix_vocabulary_examples_content_id", table_name="vocabulary_examples")
    op.drop_table("vocabulary_examples")
