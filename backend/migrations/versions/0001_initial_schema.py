"""Create the initial Convi learning schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("practice_mode", sa.String(length=50), nullable=False),
        sa.Column("practice_method", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("meaning", sa.Text(), nullable=True),
        sa.Column("language_code", sa.String(length=10), server_default="en", nullable=False),
        sa.Column("cefr_level", sa.String(length=2), nullable=True),
        sa.Column("context", sa.String(length=100), nullable=True),
        sa.Column("register", sa.String(length=20), nullable=True),
        sa.Column("source_note", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contents")),
    )

    op.create_table(
        "exercise_sets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column("schema_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("items", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("generation_model", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["content_id"], ["contents.id"], name=op.f("fk_exercise_sets_content_id_contents"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercise_sets")),
    )
    op.create_index(op.f("ix_exercise_sets_content_id"), "exercise_sets", ["content_id"], unique=False)

    op.create_table(
        "content_progress",
        sa.Column("content_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="not_started", nullable=False),
        sa.Column("practice_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("practice_count >= 0", name="ck_content_progress_count_nonnegative"),
        sa.ForeignKeyConstraint(["content_id"], ["contents.id"], name=op.f("fk_content_progress_content_id_contents"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("content_id", name=op.f("pk_content_progress")),
    )


def downgrade() -> None:
    op.drop_table("content_progress")
    op.drop_index(op.f("ix_exercise_sets_content_id"), table_name="exercise_sets")
    op.drop_table("exercise_sets")
    op.drop_table("contents")
