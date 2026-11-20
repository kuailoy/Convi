"""Build and import vocabulary form targets from a generated set.

Every vocabulary item gets one headword target (option A, see
docs/data-generation/grammatical-label-policy.md#headword-targets) followed by
its generated targets. The import replaces all rows of `vocabulary_forms`.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.content import Content, VocabularyExample, VocabularyExampleTarget, VocabularyForm

UNINFLECTED_POS = {"adverb", "adposition", "conjunction", "particle", "interjection"}
# Words that never change form: their headword target is `invariant`.
INDECLINABLE_WORDS = {"koko", "eri", "viime", "pikku", "täynnä", "monta"}
PLURAL_HEADWORDS = {"molemmat"}
REQUIRED_MIGRATION = "0010_content_reports"


def headword_target(word: str, part_of_speech: str, pos_subtype: str | None) -> tuple[str, str]:
    """(grammatical_label, target_type) of the headword target."""
    if pos_subtype == "negative_auxiliary":
        return "negative_verb_3sg", "inflected_form"
    if part_of_speech == "verb":
        return "first_infinitive", "inflected_form"
    if part_of_speech in UNINFLECTED_POS or word in INDECLINABLE_WORDS:
        return "invariant", "invariant"
    if word in PLURAL_HEADWORDS:
        return "nominative_plural", "inflected_form"
    return "nominative_singular", "inflected_form"


def build_rows(combined: dict, vocabulary: list[dict], model: str) -> list[dict]:
    """Rows for `vocabulary_forms`, one headword target plus the generated targets per item."""
    by_id = {row["id"]: row for row in vocabulary}
    version = combined["prompt_version"]
    rows: list[dict] = []
    seen_items: set[str] = set()
    for item in combined["items"]:
        content_id = item["content_id"]
        if content_id in seen_items:
            raise ValueError(f"Item {item['word']} appears twice.")
        seen_items.add(content_id)
        source = by_id.get(content_id)
        if source is None or source["word"] != item["word"]:
            raise ValueError(f"Item {item['word']} ({content_id}) does not match the vocabulary CSV.")

        label, target_type = headword_target(item["word"], source["part_of_speech"], source["pos_subtype"] or None)
        targets = [{"form": item["word"], "grammatical_label": label, "target_type": target_type,
                    "notes": None, "source_note": f"{version} import: headword target"}]
        for target in item["forms"]:
            note = f"{version} / {model}" + (" / manual correction" if target.get("source") == "correction" else "")
            targets.append({"form": target["form"], "grammatical_label": target["grammatical_label"],
                            "target_type": target["target_type"], "notes": target.get("notes") or None,
                            "source_note": note})

        keys = [(t["form"], t["grammatical_label"], t["target_type"]) for t in targets]
        if len(keys) != len(set(keys)):
            raise ValueError(f"Duplicate target for {item['word']}.")
        for order, target in enumerate(targets, start=1):
            rows.append({"content_id": UUID(content_id), "display_order": order, "review_status": "active", **target})

    missing = set(by_id) - seen_items
    if missing:
        raise ValueError(f"{len(missing)} vocabulary items have no generated entry.")
    return rows


@dataclass
class ImportCounts:
    old_forms: int
    old_example_links: int
    old_examples: int
    new_forms: int
    vocabulary_items: int


def replace_forms(session: Session, rows: list[dict], *, apply: bool) -> ImportCounts:
    """Check the database and, with apply=True, replace all form targets and old examples.

    Runs inside the caller's transaction; the caller commits or rolls back.
    """
    db_items = set(session.scalars(select(Content.id).where(Content.content_type == "vocabulary_item")))
    row_items = {row["content_id"] for row in rows}
    if db_items != row_items:
        raise ValueError(
            f"Vocabulary items differ: {len(row_items - db_items)} not in the database, "
            f"{len(db_items - row_items)} in the database without generated targets."
        )
    counts = ImportCounts(
        old_forms=session.scalar(select(func.count()).select_from(VocabularyForm)),
        old_example_links=session.scalar(select(func.count()).select_from(VocabularyExampleTarget)),
        old_examples=session.scalar(select(func.count()).select_from(VocabularyExample)),
        new_forms=len(rows),
        vocabulary_items=len(row_items),
    )
    if apply:
        # Links to the old forms disappear with them (ON DELETE CASCADE); the examples would be left
        # without targets, so they are removed and regenerated after the import.
        session.execute(delete(VocabularyExampleTarget))
        session.execute(delete(VocabularyExample))
        session.execute(delete(VocabularyForm))
        session.add_all(VocabularyForm(**row) for row in rows)
        session.flush()
    return counts
