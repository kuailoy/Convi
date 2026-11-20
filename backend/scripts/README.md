# Backend scripts

Run every script from the `backend/` directory with the virtual environment active:

```bash
source .venv/bin/activate
python -m pip install -e .
```

Datasets used by these scripts are in [`../data-generation/`](../data-generation/). See the [documentation index](../../docs/README.md) for an overview of the data files.

| Script | Purpose | Writes to database |
| --- | --- | --- |
| `import_vocabulary` | Import the 949 words and 41 topics | Yes |
| `generate_topic_examples` | Generate, validate and save missing example sentences for one topic | Yes |
| `export_database` | Read-only snapshot and review package (use as a backup before data changes) | No |
| `legacy_import_vocabulary_forms_v0` | **Legacy.** Import the v0 form targets for topics 1–3 | Yes |
| `legacy_try_pattern_drill_en` | **Legacy prototype.** Interactive English Pattern Drill | No |

Scripts prefixed with `legacy_` are kept for reference or to reproduce the current database state. They are not part of the current workflow and can be removed once their replacement exists.

## Import vocabulary

```bash
alembic upgrade head
python -m scripts.import_vocabulary
python -m scripts.legacy_import_vocabulary_forms_v0   # legacy, see below
```

- `import_vocabulary` reads `data-generation/vocabulary/finnish_vocabulary.csv`, checks for 949 unique words, and creates or refreshes topics and vocabulary items. Meanings are left blank.
- `legacy_import_vocabulary_forms_v0` reads `data-generation/legacy_v0/vocabulary_forms_topic_1_3.json` and adds or refreshes the 233 v0 word-form and usage targets. It expects the vocabulary to be imported first.

Both imports are idempotent. The v0 form targets will be replaced by v1 generated targets; see the [form-target checkpoint](../../docs/data-generation/FORM_TARGET_GENERATION_CHECKPOINT.md).

## Generate example sentences

```bash
python -m scripts.generate_topic_examples --topic pronouns-and-reference --limit 10
```

Set `OPENAI_API_KEY` in the backend environment first. Each result includes a natural spoken Finnish sentence and its standard written counterpart; when the word is mainly written or has no register difference, the sentences can be identical. Prompts prioritise the common everyday sense, high-frequency concrete supporting words and a simple main clause; they avoid abstract nominalisations and uncommon grammar.

The script saves each result immediately, so later failures do not discard earlier examples. The limit supports reviewing a small pilot before generating the rest of a topic. Relational usage targets are saved as `needs_review` because the backend does not yet include a Finnish morphology analyser; they do not count as covered until reviewed.

For an interactive terminal run that prompts for the key without echoing it:

```zsh
./scripts/generate_topic_examples.zsh                              # first topic, 10 targets
./scripts/generate_topic_examples.zsh questions-and-connectors 20  # topic and limit
```

## Export the database for review

```bash
python -m scripts.export_database
```

The script reads PostgreSQL in a read-only transaction and writes to `data-generation/exports/chatgpt_export/` (ignored by Git). It creates a complete `database_snapshot.json`, per-table CSVs, a linked `chatgpt_review.json`, a data-quality summary, a proposed-content template and `chatgpt_review_package.zip`. The ChatGPT package omits learner progress rows; the full snapshot retains all tables.

To rebuild the review files from an existing snapshot without connecting to PostgreSQL:

```bash
python -m scripts.export_database --from-snapshot data-generation/exports/chatgpt_export/database_snapshot.json
```

Use `--output <dir>` to choose another directory.

## Legacy: English Pattern Drill prototype

```bash
python -m scripts.legacy_try_pattern_drill_en
```

Uses a fixed English sentence pattern and generates five exercises. One API request asks the model for suitable substitutions; Python fills them into the pattern and runs the practice flow locally.
