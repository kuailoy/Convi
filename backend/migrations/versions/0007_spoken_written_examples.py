"""Store a spoken Finnish sentence and its written counterpart.

Revision ID: 0007_spoken_written_examples
Revises: 0006_vocabulary_examples
Create Date: 2026-11-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_spoken_written_examples"
down_revision: Union[str, None] = "0006_vocabulary_examples"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "vocabulary_examples",
        sa.Column("written_finnish_sentence", sa.Text(), nullable=True),
    )
    op.execute(
        "UPDATE vocabulary_examples "
        "SET written_finnish_sentence = finnish_sentence "
        "WHERE written_finnish_sentence IS NULL"
    )
    op.alter_column("vocabulary_examples", "written_finnish_sentence", nullable=False)

    # Previous examples had no register pair. Keep the saved sentence, but require a
    # new paired generation or manual review before it contributes to coverage.
    op.execute(
        "UPDATE vocabulary_examples "
        "SET validation_status = 'needs_review', "
        "validation_notes = 'Generated before spoken/written sentence pairs were required.' "
        "WHERE prompt_version = 'fi-example-v1'"
    )
    op.execute(
        "UPDATE vocabulary_example_targets AS target "
        "SET target_validation_status = 'needs_review', "
        "target_validation_notes = 'Regenerate or review the spoken/written sentence pair.' "
        "FROM vocabulary_examples AS example "
        "WHERE target.example_id = example.id "
        "AND example.prompt_version = 'fi-example-v1'"
    )


def downgrade() -> None:
    op.drop_column("vocabulary_examples", "written_finnish_sentence")
