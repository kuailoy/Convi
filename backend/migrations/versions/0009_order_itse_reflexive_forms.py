"""Keep the split reflexive targets in their reviewed display order.

Revision ID: 0009_order_itse_reflexive_forms
Revises: 0008_split_itse_reflexive_forms
Create Date: 2026-11-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_order_itse_reflexive_forms"
down_revision: Union[str, None] = "0008_split_itse_reflexive_forms"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE vocabulary_forms AS form "
        "SET display_order = form.display_order + 1 "
        "FROM contents AS word "
        "JOIN vocabulary_topics AS topic ON topic.id = word.topic_id "
        "WHERE form.content_id = word.id "
        "AND topic.slug = 'pronouns-and-reference' "
        "AND word.content = 'itse' "
        "AND form.form = 'itsensä'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE vocabulary_forms AS form "
        "SET display_order = form.display_order - 1 "
        "FROM contents AS word "
        "JOIN vocabulary_topics AS topic ON topic.id = word.topic_id "
        "WHERE form.content_id = word.id "
        "AND topic.slug = 'pronouns-and-reference' "
        "AND word.content = 'itse' "
        "AND form.form = 'itsensä'"
    )
