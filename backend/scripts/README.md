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
| `generate_form_targets` | Generate form targets into local files (resumable) | No |
| `check_form_targets` | Check a generated set with Voikko; writes `voikko_report.csv` | No |
| `import_form_targets` | Replace all form targets with a generated set (+ headword targets); dry run unless `--apply` | Yes |
| `export_database` | Read-only snapshot and review package (use as a backup before data changes) | No |
| `legacy_try_pattern_drill_en` | **Legacy prototype.** Interactive English Pattern Drill | No |

Scripts prefixed with `legacy_` are kept for reference only and are not part of the current workflow.

## Import vocabulary

```bash
alembic upgrade head
python -m scripts.import_vocabulary
python -m scripts.import_form_targets --apply   # form targets, see below
```

- `import_vocabulary` reads `data-generation/vocabulary/finnish_vocabulary.csv`, checks for 949 unique words, and creates or refreshes topics and vocabulary items. Meanings are left blank.

The vocabulary import is idempotent; the form-target import replaces all targets each time.

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

## Generate form targets

```bash
./scripts/generate_form_targets.zsh topic:food-and-drink      # asks for OPENAI_API_KEY if it is not set
python -m scripts.generate_form_targets --set pilot --dry-run  # plan and inputs only
python -m scripts.generate_form_targets --set pilot            # rerun the same command to resume
python -m scripts.generate_form_targets --set pilot --retry-failed
python -m scripts.generate_form_targets --set all --reuse pilot   # copy the pilot's accepted batches instead of regenerating them
```

Manual fixes for a run go in `data-generation/form_targets/corrections.json` (optional; create it when needed and delete it after the import; add, remove or replace a form for a word). They are applied when the combined files are built, so the model output stays unchanged and the fixes survive reruns. Rerunning a finished set rebuilds the combined files without calling the model.

With Voikko installed (free Finnish morphological analyser; see `app/services/voikko_check.py`), generation adds Voikko findings as warnings, and `python -m scripts.check_form_targets --set all` writes `voikko_report.csv` for an existing set.

Writes to `data-generation/form_targets/outputs/<prompt version>_<set>/` (now `v3_<set>`): `manifest.json` (progress), accepted `batches/`, rejected attempts in `errors/`, and `combined.json` / `combined.csv`; `--dry-run` also writes the model inputs to `inputs/`. Nothing is written to the database. After a set is imported, its `batches/` can be deleted; `combined.json` and `manifest.json` are kept (the import and the export comparison use them). Design and validation rules: [form-target-batch-tool.md](../../docs/data-generation/form-target-batch-tool.md).

## Import form targets

```bash
python -m scripts.export_database --output data-generation/exports/backup-YYYY-MM-DD   # backup first, own directory
alembic upgrade head                              # needs migration 0010
python -m scripts.import_form_targets             # dry run: checks and counts
python -m scripts.import_form_targets --apply     # write
```

Imports `data-generation/form_targets/outputs/v3_all/combined.json` (`--set` chooses another set). Each word gets a headword target first (`nominative_singular`, `first_infinitive`, `invariant`, …), then its generated targets, all `active`. In one transaction it deletes all existing form targets and the example sentences linked to them (they are regenerated afterwards) and inserts the new rows. It stops if any batch is unfinished, the database is not at migration `0010`, or the vocabulary does not match (every word in the database must have an entry; for new vocabulary an append mode still has to be added).

## Export the database for review

```bash
python -m scripts.export_database
```

The script reads PostgreSQL in a read-only transaction and writes to `data-generation/exports/chatgpt_export/` (ignored by Git). It creates a complete `database_snapshot.json`, per-table CSVs, a linked `chatgpt_review.json`, a data-quality summary, a proposed-content template and `chatgpt_review_package.zip`. The ChatGPT package omits learner progress rows; the full snapshot retains all tables.

To rebuild the review files from an existing snapshot without connecting to PostgreSQL:

```bash
python -m scripts.export_database --from-snapshot data-generation/exports/chatgpt_export/database_snapshot.json
```

Use `--output <dir>` to choose another directory. **For a backup before a data change, always use its own directory**: the default directory is overwritten by every export. The form-target comparison in the summary checks the database against `form_targets/outputs/v3_all` plus headword targets.

## Legacy: English Pattern Drill prototype

```bash
python -m scripts.legacy_try_pattern_drill_en
```

Uses a fixed English sentence pattern and generates five exercises. One API request asks the model for suitable substitutions; Python fills them into the pattern and runs the practice flow locally.
