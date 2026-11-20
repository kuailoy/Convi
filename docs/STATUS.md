# Convi — Current Status

**Last updated:** 2026-11-20
**Basis:** repository inspection and a read-only database snapshot (`scripts/export_database`, 2026-11-20 15:37 UTC, Azure `convi_dev`, Entra authentication).

This file is the single source of truth for project status. Background and long-term plans are in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

---

## 1. Summary

The vocabulary foundation, form targets for all 949 words, the example-sentence pipeline, a read API and a mobile study flow with a Report button exist. Form targets were generated, checked and imported on 2026-11-20. The current focus is **example sentences** for the new targets.

---

## 2. Status by workstream

| Workstream | Status | Notes |
| --- | --- | --- |
| Vocabulary list | ✅ Done | 949 words, 41 topics, imported into `contents` / `vocabulary_topics`. English meanings are still empty. |
| POS classification | ✅ Done (first pass) | All 949 words; [vocabulary_classification.csv](../backend/data-generation/vocabulary/vocabulary_classification.csv). Not imported into the database. |
| Form targets — v0 (topics 1–3) | ✅ In database, to be replaced | 233 targets for 93 words, legacy labels (`N sg`, `G sg`, …). Will be regenerated with v1. |
| Form targets — v1 policy and prompt | ✅ Done | Generation and label policies; prompt v1. |
| Form targets — prompt v3 | ✅ Pilot run | [form_generation_v3.md](../backend/data-generation/form_targets/prompts/form_generation_v3.md): common-use goal, `present_3sg` allowed when spelled like the infinitive, verb collocations incl. ordinary objects (`accusative_complement` added), more third infinitives, max 10 targets. Pilot rerun pending. |
| Form targets — batch tool | ✅ Implemented | `python -m scripts.generate_form_targets --set <set>`; [design](data-generation/form-target-batch-tool.md). Not yet run against the model. |
| Form targets — bulk generation | ✅ Done (2026-11-20) | Prompt v3, all 949 words: 3,330 targets in `outputs/v3_all/` (73 batches, 6 retried automatically). Voikko check: 3 real errors fixed (9 manual corrections in total, applied before import); 6 remaining findings are Voikko gaps. |
| Form targets — import | ✅ Done (2026-11-20) | 4,279 rows in `vocabulary_forms` (949 headword + 3,330 generated, all `active`); v0 rows and the 23 old examples removed. Migration `0010` applied. Backend not yet redeployed. |
| Example sentence generation | ✅ Working, little content | Script and protected API endpoint; spoken + written Finnish + translation; automatic validation. Database: 23 examples for 3 words (see §3). |
| Example review workflow | 🟡 Report button | Report button in the learning session → `content_reports` (migration `0010`, not yet applied/deployed). No tool yet for fixing reported items. |
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
| `vocabulary_forms` | 233 → 4,279 after the import | Before: v0 only, topics 1–3, all `reviewed`. After (2026-11-20): all 949 words, headword + v3 targets, all `active` |
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
| 2026-11-20 | **Headword targets are added by the import step (option A).** The model never outputs the headword; import adds one target per word (`nominative_singular`, `first_infinitive` or `invariant`) so that every word, including words with no other forms, can get example sentences. |
| 2026-11-20 | **Verb government is generated** as `governed_pattern` with `<case>_complement` labels (`pitää kahvista` → `elative_complement`). Adpositions use the same labels; `case_usage_pattern` remains only for constructions without a single complement case. |
| 2026-11-20 | **Third infinitive allowed**, at most one form per verb (`third_infinitive_illative`, `third_infinitive_inessive`). |
| 2026-11-20 | Prompt v2 drafted with a closed label list and a JSON Schema; prompt v1 unchanged. |
| 2026-11-20 | **No separate manual review of generated data.** Automatic validation is the gate; generated rows are imported as `active` (normal). Only a row reported from the app (planned report button) becomes `needs_review` until it is fixed. Provenance (model, prompt version) is kept in `source_note`. |
| 2026-11-20 | **Report button** in the learning session (small "Report" link under the example card). Reports go to `content_reports` with a snapshot; the reported form or example becomes `needs_review`. `vocabulary_forms.review_status` defaults to `active`; the API shows `active`, `needs_review` and `reviewed` forms. |
| 2026-11-20 | **Prompt v3 after the v2 pilot:** the goal is common everyday Finnish, not grammatical coverage; simple forms are valuable. Forms spelled like the headword are allowed when they are a different form (`antaa` `present_3sg`); verb collocations include ordinary objects; third infinitives for everyday action verbs. |
| 2026-11-20 | Batch tool implemented (`scripts.generate_form_targets`, resumable via a manifest, 15 tests). First run: `topic:food-and-drink`, then the pilot set. |
| 2026-11-20 | **Regenerate topics 1–3 with the v1 policy.** The v0 forms (legacy labels, headword stored as a target) will be replaced instead of kept alongside v1 output. |
| 2026-11-20 | **Use `target_type` as the field name** in generation output, matching the database and API. Policy documents now use `target_type`; prompt v1 and the pilot keep `form_type` as historical artifacts. The next prompt version will use `target_type`. |
| 2026-11-20 | Cleanup: removed prompts v1/v2, the v1/v2/v3 pilot outputs, the v0 forms (`legacy_v0`, its import script and source document); dry-run inputs and rejected attempts are not kept in Git. History stays in Git. |
| 2026-11-20 | Documentation consolidated under `docs/`; datasets under `backend/data-generation/`. |
| 2026-11-11 | Pilot of 20 words / 82 targets accepted; `koti` uses `related_form` for `kotona` and `kotoa`. |
| earlier | Validate generated data locally before database import; topic-based batches (default 15 words); generated content is saved and reused. |

Earlier product and architecture decisions: [PROJECT_CONTEXT.md §14](PROJECT_CONTEXT.md#14-important-product-and-architecture-decisions).

---

## 5. Known issues

1. **Rejected examples can reach the app.** The topic contents API returns examples of every validation status and the mobile session does not filter them. Showing `needs_review` (reported) items is intended; `rejected` should be filtered.
2. **Label display.** The database now uses v3 `snake_case` labels. The mobile formatter (`mobile/src/utils/grammaticalLabel.ts`) only has names for v0 labels and falls back to Title Case ("Partitive Complement"); the example prompt (`sentence_generator.py`) passes v3 labels through unchanged.
3. **Example generation writes directly to the database**, using validation statuses instead of a local review step.
4. **The example validator does not support verb patterns.** For a `governed_pattern` it requires the headword as a token, but a verb is conjugated in the sentence; for verb patterns it must check the complement word.
5. **No CORS configuration** in the API. Native apps work; Expo web would be blocked.
6. **Backend served over plain HTTP** on a public IP.
7. **Tests cover only the data tools and reports** (`backend/tests/`); no API or mobile tests.
8. Migrations 0008–0009 contain data fixes specific to the old v0 `itse` forms.

---

## 6. Next step

1. **Redeploy the backend.** The deployed API only returns `reviewed` forms, so the app shows nothing until the new code (which shows `active`, `needs_review` and `reviewed`) is deployed. This also enables the Report endpoint (migration `0010` is applied).
2. **Example sentences for the new targets.** Decide whether example generation also writes local files first (like the form-target tool) or keeps writing to the database; fix the validator for verb patterns (known issue 4); then generate topic by topic.
3. Later: readable names for v3 labels in the app; an append mode for `import_form_targets` when new vocabulary is added (it currently replaces all targets).

How to run the data tools: [`backend/scripts/README.md`](../backend/scripts/README.md). Form-target details: [checkpoint](data-generation/FORM_TARGET_GENERATION_CHECKPOINT.md).
