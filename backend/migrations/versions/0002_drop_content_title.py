"""Drop the redundant title column from contents.

Revision ID: 0002_drop_content_title
Revises: 0001_initial
Create Date: 2026-10-27
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002_drop_content_title"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE contents DROP COLUMN IF EXISTS title")


def downgrade() -> None:
    op.execute("ALTER TABLE contents ADD COLUMN IF NOT EXISTS title VARCHAR(255)")
