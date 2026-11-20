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
| [data-generation/form-target-batch-tool.md](data-generation/form-target-batch-tool.md) | Batch generation tool: commands, validation, files |

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
│   ├── prompts/form_generation_v3.md         # Current prompt (+ .schema.json, .labels.json)
│   ├── sets/pilot.json                       # Small topic set for testing a new prompt
│   └── outputs/v3_all/                       # Final generated targets: combined.json (imported), manifest.json
└── exports/                                  # Local database exports (ignored by Git)
```

## Conventions

- Record status changes in `STATUS.md` and, for a data workstream, in its checkpoint.
- Version prompts (`form_generation_v3.md`, `v4`, …) instead of editing a prompt whose output is in use; delete old versions once their output is no longer used (Git keeps history).
- Keep raw model output unchanged; put manual fixes for a generation run in its own corrections file, and delete it once the run is imported.
