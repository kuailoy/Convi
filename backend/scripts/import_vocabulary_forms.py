"""Idempotently import the reviewed word-form pilot for the first three topics."""
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import create_database_engine
from app.models import Content, VocabularyForm, VocabularyTopic


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "vocabulary_forms_topic_1_3.json"
SOURCE_NOTE = "Reviewed pilot: docs/wordforms-topic-1-3.md"
EXPECTED_TOPICS = {
    "pronouns-and-reference": 29,
    "questions-and-connectors": 49,
    "relational-words": 15,
}


def main() -> None:
    records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    lemmas_by_topic: dict[str, set[str]] = {slug: set() for slug in EXPECTED_TOPICS}
    for record in records:
        if record["topic_slug"] not in EXPECTED_TOPICS:
            raise ValueError(f"Unexpected topic: {record['topic_slug']}")
        lemmas_by_topic[record["topic_slug"]].add(record["lemma"])
        if record["target_type"] not in {
            "inflected_form",
            "invariant",
            "related_form",
            "governed_pattern",
        }:
            raise ValueError(f"Unexpected target type: {record['target_type']}")
    for slug, expected_count in EXPECTED_TOPICS.items():
        if len(lemmas_by_topic[slug]) != expected_count:
            raise ValueError(
                f"{slug} has {len(lemmas_by_topic[slug])} lemmas; expected {expected_count}."
            )

    engine = create_database_engine()
    inserted = updated = 0
    with Session(engine) as session, session.begin():
        contents = session.execute(
            select(Content, VocabularyTopic.slug)
            .join(VocabularyTopic, Content.topic_id == VocabularyTopic.id)
            .where(
                Content.content_type == "vocabulary_item",
                VocabularyTopic.slug.in_(EXPECTED_TOPICS),
            )
        ).all()
        content_by_key = {
            (topic_slug, content.topic_order, content.content): content
            for content, topic_slug in contents
        }
        keyed_records = []
        form_orders: dict[tuple[str, int, str], int] = {}
        for record in records:
            key = (record["topic_slug"], record["topic_order"], record["lemma"])
            content = content_by_key.get(key)
            if content is None:
                raise ValueError(f"Vocabulary item not found in database: {key}")
            unique_key = (
                content.id,
                record["form"],
                record["grammatical_label"],
                record["target_type"],
            )
            form_orders[key] = form_orders.get(key, 0) + 1
            keyed_records.append((unique_key, content, record, form_orders[key]))

        existing = session.scalars(
            select(VocabularyForm).where(
                VocabularyForm.content_id.in_([content.id for _, content, _, _ in keyed_records])
            )
        ).all()
        existing_by_key = {
            (row.content_id, row.form, row.grammatical_label, row.target_type): row
            for row in existing
        }

        for (content_id, form, label, target_type), content, record, display_order in keyed_records:
            row = existing_by_key.get((content_id, form, label, target_type))
            if row is None:
                row = VocabularyForm(
                    content_id=content_id,
                    form=form,
                    grammatical_label=label,
                    target_type=target_type,
                    display_order=display_order,
                    notes=record["notes"],
                    review_status="reviewed",
                    source_note=SOURCE_NOTE,
                )
                session.add(row)
                existing_by_key[(content_id, form, label, target_type)] = row
                inserted += 1
            else:
                row.display_order = display_order
                row.notes = record["notes"]
                row.review_status = "reviewed"
                row.source_note = SOURCE_NOTE
                updated += 1

    engine.dispose()
    print(f"Vocabulary form targets: {len(records)}")
    print(f"Inserted: {inserted}; refreshed existing: {updated}")
    for slug, lemmas in lemmas_by_topic.items():
        print(f"{slug}: {len(lemmas)} vocabulary items")


if __name__ == "__main__":
    main()
