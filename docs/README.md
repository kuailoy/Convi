# Convi documentation

Start here to find the right document. Each topic has one authoritative file; other files link to it instead of repeating it.

## Project

| Document | Purpose | Update when… |
| --- | --- | --- |
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | Product vision, learning methodology, architecture direction, decisions, long-term roadmap | A product or architecture decision changes |
| [STATUS.md](STATUS.md) | **Single source of truth for current status**, recent decisions, known issues and the next step | Any task is completed or a decision is made |
| [database-schema.md](database-schema.md) | Current PostgreSQL tables, fields and relationships | A migration is added |

## Data generation

| Document | Purpose |
| --- | --- |
| [data-generation/FORM_TARGET_GENERATION_CHECKPOINT.md](data-generation/FORM_TARGET_GENERATION_CHECKPOINT.md) | Progress and decisions for the form-target workstream |
| [data-generation/form-generation-policy.md](data-generation/form-generation-policy.md) | Which forms to generate for each part of speech |
| [data-generation/grammatical-label-policy.md](data-generation/grammatical-label-policy.md) | How `grammatical_label` values are named |
| [data-generation/legacy/wordforms-topic-1-3.md](data-generation/legacy/wordforms-topic-1-3.md) | Archived source of the v0 forms for topics 1–3 (to be replaced by v1 generation) |

## Component READMEs

| Document | Purpose |
| --- | --- |
| [../README.md](../README.md) | Project overview (portfolio entry point) |
| [../backend/README.md](../backend/README.md) | Backend setup, database connection, API endpoints |
| [../backend/scripts/README.md](../backend/scripts/README.md) | Import, export and generation scripts |
| [../mobile/README.md](../mobile/README.md) | Mobile app setup |
| [../mobile/AGENTS.md](../mobile/AGENTS.md) | Rules for coding agents working on the Expo app |

## Data and generation files

Generated data lives next to the backend code, not in `docs/`:

```text
backend/data-generation/
├── vocabulary/
│   ├── finnish_vocabulary.csv                # 949 words with topic assignment (import source)
│   ├── vocabulary_classification.csv         # POS, subtype and verb type for all 949 words
│   └── vocabulary_classification_report.md   # Classification summary and corrections
├── form_targets/
│   ├── prompts/form_generation_v1.md         # Pilot prompt (v1)
│   └── outputs/pilot/                        # Reviewed 20-word pilot (JSON + CSV)
├── legacy_v0/
│   └── vocabulary_forms_topic_1_3.json       # v0 forms for topics 1–3 (currently in the database)
└── exports/                                  # Local database exports (ignored by Git)
```

## Conventions

- Record status changes in `STATUS.md` and, for a data workstream, in its checkpoint.
- Version prompts (`form_generation_v1.md`, `v2`, …) instead of editing a prompt that produced reviewed output.
- Keep raw generated output separate from reviewed, importable data.
