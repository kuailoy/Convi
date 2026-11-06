"""Add vocabulary topics and ordering metadata.

Revision ID: 0003_vocabulary_topics
Revises: 0002_drop_content_title
Create Date: 2026-11-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_vocabulary_topics"
down_revision: Union[str, None] = "0002_drop_content_title"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vocabulary_topics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name_en", sa.String(length=150), nullable=False),
        sa.Column("name_fi", sa.String(length=150), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vocabulary_topics")),
        sa.UniqueConstraint("slug", name="uq_vocabulary_topics_slug"),
    )
    op.add_column(
        "contents",
        sa.Column("meaning_language_code", sa.String(length=10), server_default="en", nullable=False),
    )
    op.add_column("contents", sa.Column("topic_id", sa.Uuid(), nullable=True))
    op.add_column("contents", sa.Column("topic_order", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_contents_topic_id_vocabulary_topics", "contents", "vocabulary_topics",
        ["topic_id"], ["id"], ondelete="RESTRICT"
    )
    op.create_index(op.f("ix_contents_topic_id"), "contents", ["topic_id"], unique=False)
    op.create_check_constraint(
        "ck_contents_topic_order_positive", "contents", "topic_order IS NULL OR topic_order >= 1"
    )
    op.create_unique_constraint("uq_contents_topic_order", "contents", ["topic_id", "topic_order"])


def downgrade() -> None:
    op.drop_constraint("uq_contents_topic_order", "contents", type_="unique")
    op.drop_constraint("ck_contents_topic_order_positive", "contents", type_="check")
    op.drop_index(op.f("ix_contents_topic_id"), table_name="contents")
    op.drop_constraint("fk_contents_topic_id_vocabulary_topics", "contents", type_="foreignkey")
    op.drop_column("contents", "topic_order")
    op.drop_column("contents", "topic_id")
    op.drop_column("contents", "meaning_language_code")
    op.drop_table("vocabulary_topics")
