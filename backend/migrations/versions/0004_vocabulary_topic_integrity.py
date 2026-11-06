"""Require complete topic placement for vocabulary content.

Revision ID: 0004_vocabulary_topic_integrity
Revises: 0003_vocabulary_topics
Create Date: 2026-11-06
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0004_vocabulary_topic_integrity"
down_revision: Union[str, None] = "0003_vocabulary_topics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_contents_topic_fields_together",
        "contents",
        "(topic_id IS NULL AND topic_order IS NULL) OR "
        "(topic_id IS NOT NULL AND topic_order IS NOT NULL)",
    )
    op.create_check_constraint(
        "ck_vocabulary_items_require_topic",
        "contents",
        "content_type <> 'vocabulary_item' OR "
        "(topic_id IS NOT NULL AND topic_order IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_vocabulary_items_require_topic", "contents", type_="check")
    op.drop_constraint("ck_contents_topic_fields_together", "contents", type_="check")
