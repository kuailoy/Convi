# Convi — Current Status

**Last updated:** 2026-11-20
**Basis:** repository inspection and a read-only database snapshot (`scripts/export_database`, 2026-11-20 15:37 UTC, Azure `convi_dev`, Entra authentication).

This file is the single source of truth for project status. Background and long-term plans are in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

---

## 1. Summary

The vocabulary foundation, the example-sentence pipeline, a read API and a mobile study flow are working. The current focus is **Phase 1 — stabilise data generation**: building a batch tool that generates v1 form targets for all 949 words.

---

## 2. Status by workstream

| Workstream | Status | Notes |
| --- | --- | --- |
| Vocabulary list | ✅ Done | 949 words, 41 topics, imported into `contents` / `vocabulary_topics`. English meanings are still empty. |
| POS classification | ✅ Done (first pass) | All 949 words; [vocabulary_classification.csv](../backend/data-generation/vocabulary/vocabulary_classification.csv). Not imported into the database. |
| Form targets — v0 (topics 1–3) | ✅ In database, to be replaced | 233 targets for 93 words, legacy labels (`N sg`, `G sg`, …). Will be regenerated with v1. |
| Form targets — v1 policy and prompt | ✅ Done | Generation and label policies; prompt v1. |
| Form targets — v1 pilot | ✅ Reviewed | 20 words, 82 targets; not imported. |
| Form targets — batch tool | ⏳ Next | Not started. |
| Form targets — bulk generation and import | ⬜ Not started | Covers all 949 words, including topics 1–3. |
| Example sentence generation | ✅ Working, little content | Script and protected API endpoint; spoken + written Finnish + translation; automatic validation. Database: 23 examples for 3 words (see §3). |
| Example review workflow | ⬜ Not started | `needs_review` items (e.g. governed patterns) have no review tool. |
| Backend API | ✅ Partial | Health, contents, vocabulary topics, topic contents, example generation. No progress or exercise endpoints. |
| Mobile app | ✅ Partial | Home, Learn, Progress, Settings, example session with TTS. Progress stored locally only. Pattern Drill screen is a placeholder. |
| Drill engine | ⬜ Not started | Legacy English substitution prototype: `backend/app/core/learning.py`, `scripts/legacy_try_pattern_drill_en.py`. |
| Answer evaluation and AI feedback | ⬜ Not started | |
| Material import and pattern extraction | ⬜ Not started | |
| Web frontend | ⬜ Not started | No web project in the repository. |
| Speech (ASR, pronunciation) | ⬜ Future | Only text-to-speech is used. |
| Automated tests | ⬜ Not started | |

---

## 3. Database snapshot (2026-11-20)

| Table | Rows | Notes |
| --- | ---: | --- |
| `alembic_version` | 1 | `0009_order_itse_reflexive_forms` (latest migration) |
| `vocabulary_topics` | 41 | IDs match `vocabulary_classification.csv` |
| `contents` | 949 | All `vocabulary_item`, `fi`, `active`; matches `finnish_vocabulary.csv`; all IDs match `vocabulary_classification.csv`; `meaning` and `cefr_level` empty |
| `vocabulary_forms` | 233 | v0 only, topics 1–3 (146 / 60 / 27); matches `legacy_v0` JSON; all `reviewed`; v1 pilot not imported |
| `vocabulary_examples` | 23 | Only `eräs`, `hän`, `itse` (topic 1); generated 2026-11-06 with prompts `fi-example-v1` (10) and `fi-example-v3-common-everyday` (13); none with the current `fi-example-v4-register-aware`; 12 `auto_valid`, 11 `needs_review` |
| `vocabulary_example_targets` | 23 | One primary link per example |
| `exercise_sets` | 0 | |
| `content_progress` | 0 | |

Example coverage (form targets with a valid primary example): **12 of 233 targets, 3 of 93 words**. Topics 2–3 have no examples.

Because `vocabulary_example_targets` cascades on delete, replacing the v0 forms removes these links and leaves the 23 examples without targets. With so few examples, regenerating them after the v1 import is simpler than migrating them.

---

## 4. Decisions log

| Date | Decision |
| --- | --- |
| 2026-11-20 | **Regenerate topics 1–3 with the v1 policy.** The v0 forms (legacy labels, headword stored as a target) will be replaced instead of kept alongside v1 output. |
| 2026-11-20 | **Use `target_type` as the field name** in generation output, matching the database and API. Policy documents now use `target_type`; prompt v1 and the pilot keep `form_type` as historical artifacts. The next prompt version will use `target_type`. |
| 2026-11-20 | Documentation consolidated under `docs/`; datasets under `backend/data-generation/`. |
| 2026-11-11 | Pilot of 20 words / 82 targets accepted; `koti` uses `related_form` for `kotona` and `kotoa`. |
| earlier | Validate generated data locally before database import; topic-based batches (default 15 words); generated content is saved and reused. |

Earlier product and architecture decisions: [PROJECT_CONTEXT.md §14](PROJECT_CONTEXT.md#14-important-product-and-architecture-decisions).

---

## 5. Known issues

1. **Unreviewed examples reach the app.** The topic contents API returns examples of every validation status, including `rejected` and `needs_review`, and the mobile session does not filter them.
2. **Two label systems.** The database uses v0 labels; v1 uses `snake_case` labels without the headword. The mobile label formatter (`mobile/src/utils/grammaticalLabel.ts`) and the example prompt (`backend/app/services/sentence_generator.py`) only know v0 labels. Resolved by the v1 regeneration and import.
3. **Example generation writes directly to the database**, using validation statuses instead of a local review step.
4. **No CORS configuration** in the API. Native apps work; Expo web would be blocked.
5. **Backend served over plain HTTP** on a public IP.
6. **No automated tests.**
7. Migrations 0008–0009 contain data fixes specific to the v0 `itse` forms.
8. **Example quality.** The 11 `needs_review` examples are older pairs marked for regeneration, and the app shows them next to newer examples for the same target. Some `auto_valid` examples are weak: `Itsen kuva näkyy peilissä` is unnatural, and in `hänen` → spoken `Sen auto on uus` the target form appears only in the written version. The validator accepts the target in either version and checks no grammar beyond the token.

---

## 6. Next step

Build an independent, resumable **batch form-target generation tool** that:

- reads `vocabulary_classification.csv` (with topic context);
- splits by topic into batches of 15 words (configurable, 10–20);
- uses a v2 prompt with `target_type`;
- validates JSON, schema, labels and duplicates;
- writes JSON and CSV per batch plus an error report under `backend/data-generation/form_targets/outputs/`;
- does **not** write to PostgreSQL.

Afterwards: validate a few batches, review, then plan the database replacement of the v0 forms (back up first).
