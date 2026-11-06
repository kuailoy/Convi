"""Idempotently import the workbook-derived Finnish vocabulary CSV."""
import csv
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import create_database_engine
from app.models import Content, VocabularyTopic


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "finnish_vocabulary.csv"
SOURCE_NOTE = "Source: finnish_949_semantic_learning_order_en.xlsx; primary topic assignment."


def main() -> None:
    with DATA_FILE.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 949 or len({row["word"] for row in rows}) != 949:
        raise ValueError(f"Expected 949 unique vocabulary items; got {len(rows)} rows.")

    engine = create_database_engine()
    with Session(engine) as session, session.begin():
        topics_by_slug = {topic.slug: topic for topic in session.scalars(select(VocabularyTopic))}
        new_topics = []
        for row in rows:
            slug = row["topic_slug"]
            if slug not in topics_by_slug:
                topic = VocabularyTopic(
                    slug=slug,
                    name_en=row["topic_en"],
                    name_fi=row["topic_fi"],
                    sort_order=int(row["topic_sort_order"]),
                )
                session.add(topic)
                topics_by_slug[slug] = topic
                new_topics.append(topic)
        if new_topics:
            session.flush()

        existing_rows = session.scalars(
            select(Content).where(Content.content_type == "vocabulary_item")
        )
        existing_by_position = {
            (content.topic_id, content.topic_order): content for content in existing_rows
        }
        for row in rows:
            topic = topics_by_slug[row["topic_slug"]]
            existing = existing_by_position.get((topic.id, int(row["topic_order"])))
            values = dict(
                content_type="vocabulary_item",
                practice_mode="vocabulary_phrase_practice",
                practice_method="contextual_use",
                content=row["word"],
                meaning=None,
                language_code="fi",
                meaning_language_code="en",
                topic_id=topic.id,
                topic_order=int(row["topic_order"]),
                source_note=SOURCE_NOTE,
                status="active",
            )
            if existing is None:
                content = Content(**values)
                session.add(content)
                existing_by_position[(topic.id, int(row["topic_order"]))] = content
            else:
                for key, value in values.items():
                    setattr(existing, key, value)

    with Session(engine) as session:
        print(f"Topics: {session.query(VocabularyTopic).count()}")
        print(f"Vocabulary items: {session.query(Content).filter_by(content_type='vocabulary_item').count()}")
        print("Meanings: left blank; meaning_language_code=en")
        grouped = session.execute(
            select(VocabularyTopic.name_en, func.count(Content.id))
            .join(Content, Content.topic_id == VocabularyTopic.id)
            .where(Content.content_type == "vocabulary_item")
            .group_by(VocabularyTopic.id, VocabularyTopic.name_en)
            .order_by(VocabularyTopic.sort_order)
        )
        print("Per-topic counts:")
        for name, count in grouped:
            print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
