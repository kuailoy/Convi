"""Export a read-only database snapshot and a ChatGPT-ready content review package."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import MetaData, Table, select, text

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import create_database_engine  # noqa: E402

DEFAULT_OUTPUT = BACKEND_ROOT / "data-generation" / "exports" / "chatgpt_export"
DATA_TABLES = (
    "vocabulary_topics",
    "contents",
    "vocabulary_forms",
    "vocabulary_examples",
    "vocabulary_example_targets",
    "exercise_sets",
    "content_progress",
    "alembic_version",
)
CHATGPT_TABLES = {
    "vocabulary_topics",
    "contents",
    "vocabulary_forms",
    "vocabulary_examples",
    "vocabulary_example_targets",
    "exercise_sets",
}


def json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (UUID, Decimal)):
        return str(value)
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    return value


def fetch_rows(connection: Any, table_name: str) -> list[dict[str, Any]]:
    table = Table(table_name, MetaData(), autoload_with=connection)
    statement = select(table)
    primary_key = list(table.primary_key.columns)
    if primary_key:
        statement = statement.order_by(*primary_key)
    return [
        {key: json_value(value) for key, value in row.items()}
        for row in connection.execute(statement).mappings()
    ]


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: compact_json(value) if isinstance(value, (dict, list)) else value
                    for key, value in row.items()
                }
            )


def build_review_data(tables: dict[str, list[dict[str, Any]]], generated_at: str) -> dict[str, Any]:
    topics = {row["id"]: row for row in tables.get("vocabulary_topics", [])}
    forms_by_content: dict[str, list[dict[str, Any]]] = defaultdict(list)
    forms_by_id: dict[str, dict[str, Any]] = {}
    for form in tables.get("vocabulary_forms", []):
        forms_by_content[form["content_id"]].append(form)
        forms_by_id[form["id"]] = form
    for forms in forms_by_content.values():
        forms.sort(key=lambda row: (row["display_order"], row["id"]))

    links_by_example: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for link in tables.get("vocabulary_example_targets", []):
        form = forms_by_id.get(link["vocabulary_form_id"])
        links_by_example[link["example_id"]].append(
            {
                "vocabulary_form_id": link["vocabulary_form_id"],
                "form": form["form"] if form else None,
                "grammatical_label": form["grammatical_label"] if form else None,
                "target_type": form["target_type"] if form else None,
                "role": link["role"],
                "target_validation_status": link["target_validation_status"],
                "target_validation_notes": link["target_validation_notes"],
            }
        )

    examples_by_content: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for example in tables.get("vocabulary_examples", []):
        examples_by_content[example["content_id"]].append(
            {
                key: example[key]
                for key in (
                    "id",
                    "finnish_sentence",
                    "written_finnish_sentence",
                    "english_translation",
                    "difficulty",
                    "validation_status",
                    "validation_notes",
                    "generation_model",
                    "prompt_version",
                )
            }
            | {"targets": links_by_example.get(example["id"], [])}
        )

    items = []
    for content in tables.get("contents", []):
        topic = topics.get(content.get("topic_id"))
        items.append(
            {
                "id": content["id"],
                "content_type": content["content_type"],
                "practice_mode": content["practice_mode"],
                "practice_method": content["practice_method"],
                "content": content["content"],
                "meaning": content["meaning"],
                "language_code": content["language_code"],
                "meaning_language_code": content["meaning_language_code"],
                "topic": (
                    {
                        "id": topic["id"],
                        "slug": topic["slug"],
                        "name_en": topic["name_en"],
                        "name_fi": topic["name_fi"],
                        "sort_order": topic["sort_order"],
                    }
                    if topic
                    else None
                ),
                "topic_order": content["topic_order"],
                "cefr_level": content["cefr_level"],
                "context": content["context"],
                "register": content["register"],
                "source_note": content["source_note"],
                "status": content["status"],
                "forms": [
                    {
                        key: form[key]
                        for key in (
                            "id",
                            "form",
                            "grammatical_label",
                            "target_type",
                            "display_order",
                            "notes",
                            "review_status",
                            "source_note",
                        )
                    }
                    for form in forms_by_content.get(content["id"], [])
                ],
                "examples": examples_by_content.get(content["id"], []),
            }
        )
    items.sort(
        key=lambda row: (
            row["topic"]["sort_order"] if row["topic"] else 10**9,
            row["topic_order"] if row["topic_order"] is not None else 10**9,
            row["content"],
        )
    )
    topic_rows = sorted(topics.values(), key=lambda row: row["sort_order"])
    return {
        "format": "convi-chatgpt-review",
        "format_version": 1,
        "generated_at_utc": generated_at,
        "language": "Finnish (fi)",
        "meaning_language": "English (en)",
        "topics": [
            {key: row[key] for key in ("slug", "name_en", "name_fi", "sort_order")}
            for row in topic_rows
        ],
        "items": items,
    }


def source_comparison(tables: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    vocab_csv = BACKEND_ROOT / "data-generation" / "vocabulary" / "finnish_vocabulary.csv"

    db_topics = {row["id"]: row for row in tables.get("vocabulary_topics", [])}
    db_vocab = {
        (db_topics[row["topic_id"]]["slug"], row["topic_order"], row["content"])
        for row in tables.get("contents", [])
        if row.get("topic_id") in db_topics and row["content_type"] == "vocabulary_item"
    }
    with vocab_csv.open(encoding="utf-8-sig", newline="") as file:
        source_vocab_rows = list(csv.DictReader(file))
    source_vocab = {
        (row["topic_slug"], int(row["topic_order"]), row["word"])
        for row in source_vocab_rows
    }

    # Form targets are compared with the generated set that the import uses (v3_all + headword targets).
    from app.services.form_target_generator import OUTPUTS_DIR, VOCABULARY_CSV, load_vocabulary, output_dir_for
    from app.services.form_target_import import build_rows

    generated = output_dir_for("all", OUTPUTS_DIR)
    manifest = json.loads((generated / "manifest.json").read_text(encoding="utf-8"))
    combined = json.loads((generated / "combined.json").read_text(encoding="utf-8"))
    source_form_rows = build_rows(combined, load_vocabulary(VOCABULARY_CSV), manifest["model"])
    form_key = ("form", "grammatical_label", "target_type", "display_order")
    source_forms = {(str(row["content_id"]), *(row[k] for k in form_key), row["notes"] or None)
                    for row in source_form_rows}
    db_forms = {(str(row["content_id"]), *(row[k] for k in form_key), row["notes"] or None)
                for row in tables.get("vocabulary_forms", [])}
    return {
        "vocabulary_source_rows": len(source_vocab_rows),
        "vocabulary_source_matches_database": source_vocab == db_vocab,
        "vocabulary_rows_only_in_source": len(source_vocab - db_vocab),
        "vocabulary_rows_only_in_database": len(db_vocab - source_vocab),
        "forms_source_rows": len(source_form_rows),
        "forms_source_matches_database": source_forms == db_forms,
        "form_targets_only_in_source": len(source_forms - db_forms),
        "form_targets_only_in_database": len(db_forms - source_forms),
    }


def make_summary(
    tables: dict[str, list[dict[str, Any]]], generated_at: str
) -> tuple[str, dict[str, Any]]:
    topics = {row["id"]: row for row in tables.get("vocabulary_topics", [])}
    contents = tables.get("contents", [])
    content_by_id = {row["id"]: row for row in contents}
    forms = tables.get("vocabulary_forms", [])
    examples = tables.get("vocabulary_examples", [])
    links = tables.get("vocabulary_example_targets", [])
    item_count = sum(row["content_type"] == "vocabulary_item" for row in contents)
    missing_meanings = sum(row["meaning"] in (None, "") for row in contents)
    content_ids_with_forms = {row["content_id"] for row in forms}
    form_types = Counter(row["target_type"] for row in forms)
    form_reviews = Counter(row["review_status"] for row in forms)
    example_statuses = Counter(row["validation_status"] for row in examples)
    example_difficulties = Counter(row["difficulty"] for row in examples)
    target_statuses = Counter(row["target_validation_status"] for row in links)
    topic_item_counts = Counter(
        row["topic_id"] for row in contents if row["content_type"] == "vocabulary_item"
    )
    topic_form_counts = Counter(
        content_by_id[row["content_id"]]["topic_id"]
        for row in forms
        if row["content_id"] in content_by_id
    )
    grouped_topics = [
        {
            "slug": topic["slug"],
            "name_en": topic["name_en"],
            "items": topic_item_counts[topic["id"]],
            "form_targets": topic_form_counts[topic["id"]],
        }
        for topic in sorted(topics.values(), key=lambda row: row["sort_order"])
    ]

    source_diff = source_comparison(tables)
    qa = {
        "vocabulary_source_matches_database": source_diff["vocabulary_source_matches_database"],
        "form_source_matches_database": source_diff["forms_source_matches_database"],
        "content_rows_missing_meaning": missing_meanings,
        "vocabulary_items_with_form_targets": len(content_ids_with_forms),
        "vocabulary_items_without_form_targets": item_count
        - len(content_ids_with_forms & {row["id"] for row in contents if row["content_type"] == "vocabulary_item"}),
        "examples_without_target_links": sum(
            example["id"] not in {link["example_id"] for link in links} for example in examples
        ),
        "invalid_or_orphaned_content_topic_links": sum(
            row["topic_id"] is not None and row["topic_id"] not in topics for row in contents
        ),
    }
    summary = {
        "database": "configured PostgreSQL database",
        "generated_at_utc": generated_at,
        "table_counts": {name: len(rows) for name, rows in tables.items()},
        "content_counts": {
            "topics": len(topics),
            "vocabulary_items": item_count,
            "form_targets": len(forms),
            "items_with_form_targets": len(content_ids_with_forms),
            "examples": len(examples),
            "example_target_links": len(links),
            "exercise_sets": len(tables.get("exercise_sets", [])),
            "content_progress_rows": len(tables.get("content_progress", [])),
        },
        "content_distribution": {
            "forms_by_target_type": dict(sorted(form_types.items())),
            "forms_by_review_status": dict(sorted(form_reviews.items())),
            "examples_by_validation_status": dict(sorted(example_statuses.items())),
            "examples_by_difficulty": dict(sorted(example_difficulties.items())),
            "example_targets_by_validation_status": dict(sorted(target_statuses.items())),
            "meanings_present": len(contents) - missing_meanings,
            "meanings_missing": missing_meanings,
        },
        "source_comparison": source_diff,
        "quality_checks": qa,
        "topics": grouped_topics,
    }

    lines = [
        "# Convi database export summary",
        "",
        f"Snapshot created (UTC): {summary['generated_at_utc']}",
        "Source: configured PostgreSQL database. Export used a read-only transaction.",
        "",
        "## Record counts",
        "",
        "| Data | Rows |",
        "| --- | ---: |",
    ]
    labels = {
        "vocabulary_topics": "Topics",
        "contents": "Content items",
        "vocabulary_forms": "Vocabulary form targets",
        "vocabulary_examples": "Vocabulary examples",
        "vocabulary_example_targets": "Example-to-form links",
        "exercise_sets": "Exercise sets",
        "content_progress": "Progress rows",
        "alembic_version": "Migration version rows",
    }
    for table_name in DATA_TABLES:
        lines.append(f"| {labels.get(table_name, table_name)} | {summary['table_counts'].get(table_name, 0)} |")
    lines.extend(
        [
            "",
            "## Review findings",
            "",
            f"- {missing_meanings} of {len(contents)} content rows have no meaning/translation. This is consistent with the current vocabulary import source, which leaves meanings blank.",
            f"- Form targets cover {len(content_ids_with_forms & {row['id'] for row in contents if row['content_type'] == 'vocabulary_item'})} of {item_count} vocabulary items.",
            f"- Form review statuses: {', '.join(f'{key}={value}' for key, value in sorted(form_reviews.items())) or 'none'}.",
            f"- Example validation statuses: {', '.join(f'{key}={value}' for key, value in sorted(example_statuses.items())) or 'none'}.",
            f"- Example-target validation statuses: {', '.join(f'{key}={value}' for key, value in sorted(target_statuses.items())) or 'none'}.",
            f"- {len(tables.get('exercise_sets', []))} exercise sets and {len(tables.get('content_progress', []))} progress rows are present.",
            f"- Vocabulary CSV matches the database: {source_diff['vocabulary_source_matches_database']} ({source_diff['vocabulary_rows_only_in_source']} source-only; {source_diff['vocabulary_rows_only_in_database']} database-only rows).",
            f"- Generated form targets (v3_all + headword targets) match the database: {source_diff['forms_source_matches_database']} ({source_diff['form_targets_only_in_source']} source-only; {source_diff['form_targets_only_in_database']} database-only targets).",
            "",
            "## Quality checks",
            "",
            "| Check | Result |",
            "| --- | --- |",
        ]
    )
    for key, value in qa.items():
        lines.append(f"| {key.replace('_', ' ')} | {value} |")
    lines.extend(["", "## Topic coverage", "", "| # | Topic | Vocabulary items | Form targets |", "| ---: | --- | ---: | ---:"])
    for order, topic in enumerate(grouped_topics, 1):
        lines.append(f"| {order} | {topic['name_en']} (`{topic['slug']}`) | {topic['items']} | {topic['form_targets']} |")
    lines.extend(
        [
            "",
            "## Export files",
            "",
            "- `database_snapshot.json` is the complete table-by-table data snapshot, including progress and exercise tables.",
            "- `chatgpt_review.json` is a smaller, linked content view with topics, vocabulary, forms, examples, and example targets.",
            "- `tables/*.csv` contains one CSV per database table.",
            "- `database-schema.md` documents table fields and relationships.",
            "- `new_data_template.json` is a draft-only shape for proposed additions; generated records require linguistic review before import.",
            "- `chatgpt_review_package.zip` bundles the review view, CSVs for language content, summary, prompt, and template. It excludes learner progress rows.",
            "",
        ]
    )
    return "\n".join(lines), summary


def review_prompt() -> str:
    return """# ChatGPT review and new Finnish data prompt

You are reviewing Convi, a Finnish speaking-practice vocabulary database. The attached `chatgpt_review.json` is the current content snapshot. It contains 41 ordered topics, vocabulary items, reviewed or draft form targets, and example sentences with their validation states. `summary.md` reports coverage and data-source comparisons. Existing item IDs are reference-only; never invent or change IDs.

## Review the current data

1. Check Finnish spelling, naturalness, meaning, grammatical labels, target types, and sentence-to-target fit.
2. Separate definite errors from suggestions that need a native-speaker or authoritative dictionary check.
3. Preserve the distinction between `inflected_form`, `invariant`, `related_form`, and `governed_pattern`. For postpositions, identify the governed complement case; do not force an inflection paradigm onto an invariant word.
4. Keep written Finnish as the default. Do not silently add colloquial forms.
5. Respect the current validation fields. Model-generated content is not human-approved just because it sounds plausible.

Return proposed corrections separately from accepted facts, using item IDs and exact current values so changes can be applied safely. Do not rewrite the entire snapshot.

## Generate additions

Use `new_data_template.json` for proposed vocabulary additions. First compare against all existing words and forms in `chatgpt_review.json` to avoid duplicates. Use an existing `topic_slug`; suggest new topics separately if necessary. Assign new `topic_order` values after the current maximum for that topic. Include a concise English meaning, useful Finnish forms or usage targets, and at least one simple, natural example with an English translation.

Mark all generated forms with `review_status: "needs_review"`, all examples with `validation_status: "needs_review"`, and all example target links with `target_validation_status: "needs_review"`. Do not mark generated content as reviewed or human-approved. Use CEFR A1 or A2 for examples. Keep `source_note` explicit; do not invent sources or dictionary attestations.

Return only the completed `new_data_template.json` structure for additions, followed by a short review report. Use `snake_case` grammatical labels as defined in the project's grammatical label policy (for example `genitive_singular`, `partitive_singular`, `present_1sg`, `partitive_complement`). Do not repeat the headword as a form target. Existing topic 1–3 forms use a legacy label style (for example `N sg`) and are scheduled for regeneration. Leave uncertain morphology or meanings as explicit questions/notes rather than guessing. `normalized_sentence` is derived from the Finnish sentence by the backend during import; do not invent a second normalization format.
"""


def generation_template() -> dict[str, Any]:
    return {
        "format": "convi-generated-vocabulary",
        "format_version": 1,
        "instructions": "Proposed records only. Assign topic_order after comparing the exported snapshot. Do not add database IDs. Keep every generated form and example in a review state.",
        "new_vocabulary_items": [
            {
                "topic_slug": "existing-topic-slug",
                "topic_order": None,
                "content_type": "vocabulary_item",
                "practice_mode": "vocabulary_phrase_practice",
                "practice_method": "contextual_use",
                "word": "Finnish lemma",
                "meaning": "Concise English meaning",
                "language_code": "fi",
                "meaning_language_code": "en",
                "cefr_level": "A1",
                "context": None,
                "register": "neutral",
                "source_note": "Generated proposal; source not independently verified",
                "status": "draft",
                "forms": [
                    {
                        "form": "Finnish form or compact usage target",
                        "grammatical_label": "snake_case label, e.g. genitive_singular or present_1sg",
                        "target_type": "inflected_form",
                        "display_order": 1,
                        "notes": "Why this form or usage is useful; mark uncertainty",
                        "review_status": "needs_review",
                        "source_note": "Generated proposal; source not independently verified",
                    }
                ],
                "examples": [
                    {
                        "finnish_sentence": "Natural spoken Finnish sentence",
                        "written_finnish_sentence": "Standard written Finnish counterpart",
                        "english_translation": "Accurate English translation",
                        "difficulty": "A1",
                        "validation_status": "needs_review",
                        "validation_notes": "Generated; requires Finnish review",
                        "generation_model": "record the model used",
                        "prompt_version": "chatgpt-generated-v1",
                        "targets": [
                            {
                                "form": "Finnish form or usage target above",
                                "role": "primary",
                                "target_validation_status": "needs_review",
                                "target_validation_notes": "Confirm the sentence demonstrates this target",
                            }
                        ],
                    }
                ],
            }
        ],
    }


def export(output: Path, snapshot_file: Path | None = None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    tables_dir = output / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    if snapshot_file:
        previous_snapshot = json.loads(snapshot_file.read_text(encoding="utf-8"))
        current_schema = previous_snapshot["schema"]
        generated_at = previous_snapshot["generated_at_utc"]
        tables = previous_snapshot["tables"]
    else:
        engine = create_database_engine()
        try:
            with engine.connect() as connection:
                with connection.begin():
                    connection.exec_driver_sql("SET TRANSACTION READ ONLY")
                    current_schema = connection.execute(text("SELECT current_schema()")).scalar_one()
                    available = set(
                        connection.execute(
                            text("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")
                        ).scalars()
                    )
                    missing = set(DATA_TABLES) - available
                    if missing:
                        raise RuntimeError(
                            f"Expected database tables are missing: {', '.join(sorted(missing))}"
                        )
                    table_order = [name for name in DATA_TABLES if name in available]
                    table_order.extend(sorted(available - set(table_order)))
                    tables = {name: fetch_rows(connection, name) for name in table_order}
        finally:
            engine.dispose()
        generated_at = datetime.now(timezone.utc).isoformat()

    snapshot = {
        "format": "convi-postgresql-data-snapshot",
        "format_version": 1,
        "generated_at_utc": generated_at,
        "schema": current_schema,
        "tables": tables,
    }
    review_data = build_review_data(tables, generated_at)
    summary_markdown, summary_json = make_summary(tables, generated_at)
    template = generation_template()

    write_json(output / "database_snapshot.json", snapshot)
    write_json(output / "chatgpt_review.json", review_data)
    write_json(output / "summary.json", summary_json)
    write_json(output / "new_data_template.json", template)
    (output / "summary.md").write_text(summary_markdown, encoding="utf-8")
    (output / "CHATGPT_REVIEW_PROMPT.md").write_text(review_prompt(), encoding="utf-8")
    schema_document = BACKEND_ROOT.parent / "docs" / "database-schema.md"
    (output / "database-schema.md").write_text(schema_document.read_text(encoding="utf-8"), encoding="utf-8")
    for table_name, rows in tables.items():
        write_csv(tables_dir / f"{table_name}.csv", rows)

    package_path = output / "chatgpt_review_package.zip"
    package_paths = [
        output / "chatgpt_review.json",
        output / "summary.md",
        output / "database-schema.md",
        output / "new_data_template.json",
        output / "CHATGPT_REVIEW_PROMPT.md",
            *[tables_dir / f"{name}.csv" for name in tables if name in CHATGPT_TABLES],
    ]
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in package_paths:
            archive.write(path, arcname=path.relative_to(output))

    print(f"Export directory: {output}")
    print(f"Database schema: {current_schema}")
    print(f"Table rows: {sum(len(rows) for rows in tables.values())}")
    print(f"ChatGPT package: {package_path}")
    print(f"Quality checks: {json.dumps(summary_json['quality_checks'], ensure_ascii=False, sort_keys=True)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Export directory")
    parser.add_argument(
        "--from-snapshot",
        type=Path,
        help="Rebuild review files from an existing database_snapshot.json without connecting to PostgreSQL",
    )
    args = parser.parse_args()
    export(
        args.output.expanduser().resolve(),
        args.from_snapshot.expanduser().resolve() if args.from_snapshot else None,
    )


if __name__ == "__main__":
    main()
