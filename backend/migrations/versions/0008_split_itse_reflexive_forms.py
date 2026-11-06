"""Split the two 1st-person reflexive forms into separate targets.

Revision ID: 0008_split_itse_reflexive_forms
Revises: 0007_spoken_written_examples
Create Date: 2026-11-06
"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = "0008_split_itse_reflexive_forms"
down_revision: Union[str, None] = "0007_spoken_written_examples"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    topics = sa.table(
        "vocabulary_topics",
        sa.column("id", sa.Uuid()),
        sa.column("slug", sa.String()),
    )
    forms = sa.table(
        "vocabulary_forms",
        sa.column("id", sa.Uuid()),
        sa.column("content_id", sa.Uuid()),
        sa.column("form", sa.Text()),
        sa.column("grammatical_label", sa.String()),
        sa.column("target_type", sa.String()),
        sa.column("display_order", sa.Integer()),
        sa.column("notes", sa.Text()),
        sa.column("review_status", sa.String()),
        sa.column("source_note", sa.String()),
    )
    contents_table = sa.table(
        "contents",
        sa.column("id", sa.Uuid()),
        sa.column("content", sa.Text()),
        sa.column("topic_id", sa.Uuid()),
    )
    row = bind.execute(
        sa.select(forms, contents_table.c.id.label("word_id"))
        .select_from(
            forms.join(contents_table, forms.c.content_id == contents_table.c.id)
            .join(topics, contents_table.c.topic_id == topics.c.id)
        )
        .where(
            topics.c.slug == "pronouns-and-reference",
            contents_table.c.content == "itse",
            forms.c.form == "itseni / itseäni",
        )
    ).mappings().first()
    if row is None:
        return

    old_id = row["id"]
    new_id = uuid4()
    bind.execute(
        forms.update()
        .where(forms.c.id == old_id)
        .values(
            form="itseni",
            grammatical_label="accusative; 1st-person reflexive with possessive suffix",
            target_type="inflected_form",
            notes="Accusative object form with the 1st-person possessive suffix; use for a bounded object.",
        )
    )
    bind.execute(
        forms.update()
        .where(
            forms.c.content_id == row["content_id"],
            forms.c.display_order > row["display_order"],
        )
        .values(display_order=forms.c.display_order + 1)
    )
    bind.execute(
        forms.insert().values(
            id=new_id,
            content_id=row["content_id"],
            form="itseäni",
            grammatical_label="partitive; 1st-person reflexive with possessive suffix",
            target_type="inflected_form",
            display_order=row["display_order"] + 1,
            notes="Partitive form with the 1st-person possessive suffix; common with verbs such as rakastaa.",
            review_status=row["review_status"],
            source_note=row["source_note"],
        )
    )

    # The saved rejected example contains itseäni, so associate it with the new
    # partitive target and require review/regeneration under the updated prompt.
    example_targets = sa.table(
        "vocabulary_example_targets",
        sa.column("example_id", sa.Uuid()),
        sa.column("vocabulary_form_id", sa.Uuid()),
        sa.column("target_validation_status", sa.String()),
        sa.column("target_validation_notes", sa.Text()),
    )
    examples = sa.table(
        "vocabulary_examples",
        sa.column("id", sa.Uuid()),
        sa.column("finnish_sentence", sa.Text()),
        sa.column("written_finnish_sentence", sa.Text()),
        sa.column("validation_status", sa.String()),
        sa.column("validation_notes", sa.Text()),
    )
    linked = bind.execute(
        sa.select(example_targets.c.example_id)
        .select_from(example_targets.join(examples, examples.c.id == example_targets.c.example_id))
        .where(
            example_targets.c.vocabulary_form_id == old_id,
            sa.or_(
                examples.c.finnish_sentence.ilike("%itseäni%"),
                examples.c.written_finnish_sentence.ilike("%itseäni%"),
            ),
        )
    ).scalars().all()
    for example_id in linked:
        bind.execute(
            example_targets.update()
            .where(
                example_targets.c.example_id == example_id,
                example_targets.c.vocabulary_form_id == old_id,
            )
            .values(
                vocabulary_form_id=new_id,
                target_validation_status="needs_review",
                target_validation_notes="Target split into separate accusative and partitive forms; regenerate or review this example.",
            )
        )
        bind.execute(
            examples.update()
            .where(examples.c.id == example_id)
            .values(
                validation_status="needs_review",
                validation_notes="Target split into separate accusative and partitive forms; regenerate or review this example.",
            )
        )


def downgrade() -> None:
    # Keep the corrected targets on downgrade; combining distinct forms again
    # would recreate the validation issue this revision fixes.
    pass
