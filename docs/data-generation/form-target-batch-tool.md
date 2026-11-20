# Form-Target Batch Generation Tool — Design

**Status:** Implemented and used for all 949 words (2026-11-20).
**Last updated:** 2026-11-20

## 1. Purpose and scope

Generate form targets for the vocabulary in `vocabulary_classification.csv` with the current prompt (`PROMPT_VERSION` in the generator, now `form_generation_v3`), validate them, and save them as local files for import.

There is no separate manual review step (decided 2026-11-20): automatic validation is the gate, and problems found while using the app are reported from the app (planned report button).

In scope:
- batching by topic, model calls, validation, resumable progress, combined output files.

Not in scope:
- writing to PostgreSQL;
- headword targets (added by the import step, option A);
- example sentences;
- a review interface (problems are reported from the app instead).

## 2. Commands

Run from `backend/`, like the other scripts:

```bash
python -m scripts.generate_form_targets --set pilot                   # plan (first run) and generate
python -m scripts.generate_form_targets --set pilot                   # rerun = resume
python -m scripts.generate_form_targets --set pilot --retry-failed    # also retry failed batches
python -m scripts.generate_form_targets --set pilot --only pronouns-and-reference__02
python -m scripts.generate_form_targets --set pilot --dry-run         # show the plan and inputs, no API calls
python -m scripts.generate_form_targets --set topic:food-and-drink    # one topic
python -m scripts.generate_form_targets --set all                     # all 949 words
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--set` | required | `pilot`, `all`, `topic:<slug>`, or the name of a set file (§3) |
| `--model` | `gpt-6-luna` | Same default as example generation |
| `--batch-size` | `15` | Maximum words per batch when a topic is split |
| `--retry-failed` | off | Also run batches with status `failed` |
| `--only <batch_id>` | — | Run one batch, whatever its status |
| `--dry-run` | off | Write the plan and batch inputs; do not call the model |
| `--reuse <set>` | — | Copy accepted batches with identical words from another set made with the same prompt, schema, labels and model (`--set all --reuse pilot`) |

A zsh wrapper (`scripts/generate_form_targets.zsh`) asks for `OPENAI_API_KEY` without echoing it, like `generate_topic_examples.zsh`.

## 3. Sets and batching

- Sets are small JSON files in `data-generation/form_targets/sets/`, so the pilot scope is versioned and reviewable. `pilot.json`:

  ```json
  { "topics": ["ability-and-necessity", "relational-words", "food-and-drink", "pronouns-and-reference"] }
  ```

  `all` and `topic:<slug>` need no file.
- Words keep their CSV order within each topic.
- A topic with at most 20 words is one batch. A larger topic is split into `ceil(n / batch_size)` contiguous batches of nearly equal size (29 → 15 + 14; 49 → 13 + 12 + 12 + 12).
- Batch IDs are `<topic_slug>__NN` (`pronouns-and-reference__02`). The same CSV and options always give the same plan.
- The pilot set gives 68 words in 5 batches.

## 4. Model call

- OpenAI Responses API, as in `sentence_generator.py`:
  - `instructions`: the text of `form_generation_v3.md`, read verbatim;
  - `input`: the batch as JSON (`{"items": [...]}`), with `id` → `content_id`, `topic_name_en` → `topic_name`, an empty `pos_subtype` or `verb_type` → `null`;
  - `text.format`: `json_schema`, `strict: true`, schema from `form_generation_v3.schema.json`.
- Transient errors (rate limit, timeout, 5xx): up to 3 attempts with backoff.
- Validation errors (§5): one automatic retry, because model output varies; after that the batch is `failed`.

## 5. Validation

The label allowlist lives in a machine-readable file, `prompts/form_generation_v3.labels.json`. The validator reads it, and a test checks that it matches the labels listed in the prompt, so the two cannot drift apart.

**Errors** — the batch is not accepted:

| Check | Example |
| --- | --- |
| JSON parses and matches the schema | |
| Same `content_id`s as the input, same order; `word` matches | |
| Form spelled like the headword (case-insensitive, NFC) | `antaa` → `antaa` |
| Duplicate form within an item | |
| Duplicate label within an item, except `governed_pattern` | two `genitive_singular` |
| Label not in the allowlist (pattern labels for `itse` included) | `elative_sg` |
| `inflected_form` / `related_form` with a space | `olen puhunut` |
| Non-verb `governed_pattern` without the headword as a token | `minun kanssani` |
| Verb `governed_pattern` not exactly "headword + one word" | `pitää paljon kahvista` |
| More than 8 forms | |

**Warnings** — the batch is accepted; the warning is saved with the batch and shown in `combined.csv`:

| Check | Example |
| --- | --- |
| Form equals another headword anywhere in the vocabulary | `paljon` → `enemmän` |
| Label does not fit the part of speech | `present_1sg` on a noun; `comparative` on an adverb |
| Conjunction, particle or interjection with forms | |
| Verb with no `present_*` form | |
| Count outside the typical range for the part of speech | 7 targets for a noun |
| Characters other than letters, space, hyphen or colon | |
| Note longer than 120 characters | |

**Voikko check (implemented):** with `libvoikko` installed, each target is checked with the Finnish morphological analyser: unknown word, base form different from the headword, label not matching Voikko's analysis, or a pattern complement in the wrong case → warning (`voikko_*`). `scripts.check_form_targets` runs the same check on an existing set and writes `voikko_report.csv`. Invisible characters (e.g. soft hyphens) are a validation error.

**Corrections:** optional manual fixes for a run go in `data-generation/form_targets/corrections.json` (create it when needed; delete it once the run is imported) (`add`, `remove`, `replace` per word). They are applied when `combined.json` / `combined.csv` are built; accepted batch files are never edited. A correction that does not apply (the form is already there, or absent) is skipped. Each target in the combined files has `source`: `model` or `correction`.

## 6. Files

```text
data-generation/form_targets/
├── sets/
│   └── pilot.json
└── outputs/v3_all/                # one directory per set: v3_all, v3_pilot, v3_topic_<slug>
    ├── manifest.json              # plan and progress
    ├── inputs/<batch_id>.json     # model input, written by --dry-run only (ignored by Git)
    ├── batches/<batch_id>.json    # accepted model output (never edited)
    ├── errors/<batch_id>.<attempt>.txt   # rejected attempts (ignored by Git)
    ├── combined.json              # all accepted batches, rebuilt after every run
    └── combined.csv               # flat table for inspection, rebuilt after every run
```

After a set has been imported, its `batches/` may be deleted (done for `v3_all`): `combined.json` then is the final data, and rerunning the set leaves the combined files unchanged. New corrections no longer apply to such a set.

`combined.csv` columns: `batch_id`, `topic_slug`, `content_id`, `word`, `part_of_speech`, `display_order`, `form`, `grammatical_label`, `target_type`, `notes`, `warnings`. A word with no targets gets one row with an empty `form`, so it is visible.

## 7. Progress and resume (`manifest.json`)

```json
{
  "set": "pilot",
  "prompt_version": "form_generation_v3",
  "prompt_sha256": "…",
  "schema_sha256": "…",
  "labels_sha256": "…",
  "model": "gpt-6-luna",
  "batch_size": 15,
  "created_at": "2026-11-21T10:00:00Z",
  "batches": [
    {
      "batch_id": "ability-and-necessity__01",
      "topic_slug": "ability-and-necessity",
      "content_ids": ["…"],
      "status": "done",
      "attempts": 1,
      "warnings": 2,
      "last_error": null,
      "completed_at": "…",
      "usage": { "input_tokens": 0, "output_tokens": 0 }
    }
  ]
}
```

- Statuses: `pending`, `done`, `failed`.
- A run processes `pending` batches in order (plus `failed` with `--retry-failed`). The manifest is rewritten atomically (temporary file + rename) after each batch, so stopping the script at any point loses at most the batch in progress.
- If the prompt, schema or label file changes after a run has started, the tool stops instead of mixing versions. Use a new output directory for a new prompt version.
- If the CSV changes so that a planned batch would contain different words, the tool stops and reports the difference.
- Model, prompt version and hashes are recorded per run, so the import can fill `vocabulary_forms.source_note` later.

## 8. Code layout

| File | Content |
| --- | --- |
| `app/services/form_target_generator.py` | Reading the CSV, sets, batching, model call, manifest |
| `app/services/form_target_validator.py` | Errors and warnings (§5) |
| `scripts/generate_form_targets.py` | Command line |
| `scripts/generate_form_targets.zsh` | Key prompt wrapper |
| `data-generation/form_targets/prompts/form_generation_v3.labels.json` | Label allowlist |
| `data-generation/form_targets/sets/pilot.json` | Pilot set |
| `tests/test_form_target_generation.py`, `test_form_target_import.py` | Tests (standard-library `unittest`): validator cases, planning, resume, reuse, corrections, import |

## 9. Workflow (also for new vocabulary or a new prompt)

1. Update `vocabulary/vocabulary_classification.csv` if words were added. For a new prompt, copy the current one to a new version (`form_generation_v4.md` + `.schema.json` + `.labels.json`) and set `PROMPT_VERSION` in `form_target_generator.py`.
2. `--set pilot --dry-run` to check the plan, then `--set pilot` and look at `combined.csv` and the warnings.
3. `--set all --reuse pilot` for the rest (rerun the same command after an interruption; `--retry-failed` for failed batches).
4. Optional: `python -m scripts.check_form_targets --set all` (needs Voikko); put manual fixes in `corrections.json` and rerun the set to rebuild the combined files.
5. Back up with `export_database --output <own directory>`, then `import_form_targets` (dry run) and `--apply`.
6. After the import, delete `batches/` and `corrections.json`; keep `combined.json` and `manifest.json`.

Limitation: the import replaces all form targets and expects an entry for every word in the database; adding only new words needs an append mode.
