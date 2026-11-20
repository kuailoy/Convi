# Form Target Generation — Project Checkpoint

**Status:** Pilot reviewed; classification complete; batch tool not started
**Last updated:** 2026-11-20

## 1. Goal

Generate useful Finnish form targets for all 949 vocabulary items stored in Convi.

The generation process should select forms based on part of speech, grammatical usefulness, lexical behaviour, topic context, and learner value. Do not generate a fixed number of forms just to meet a quota.

## 2. Decisions already made

### Data model and labels
- Keep the headword in `contents`; do not duplicate it as a form target.
- A form target has an actual Finnish `form`, a `grammatical_label`, and a `target_type`.
- **Field name:** use `target_type`, matching the `vocabulary_forms` table and the API (decided 2026-11-20). Prompt v1 and the pilot output used `form_type`; they are kept unchanged as historical artifacts, and the next prompt version uses `target_type`.
- `grammatical_label` describes the grammatical role, using plain `snake_case` strings. Do not create a PostgreSQL ENUM or lookup table for it.
- `target_type` describes the relationship to the headword:
  - `inflected_form`
  - `invariant`
  - `related_form`
  - `governed_pattern`
- Do not conflate `grammatical_label` and `target_type`.
- Do not add `valid`, `verified`, `confidence`, or similar review-status fields to generated content.
- A word may have no additional useful form targets. Do not invent forms to fill a quota.

### Scope
- **Topics 1–3 are regenerated with v1** (decided 2026-11-20). Their existing v0 targets (233 targets, 93 words, legacy labels such as `N sg`, headword stored as a target) will be replaced when the approved v1 output is imported. Bulk generation therefore covers all 949 words.

### POS-specific generation policy
See [form-generation-policy.md](form-generation-policy.md). Summary:
- **Nouns:** genitive and partitive first; location cases or plural forms only when useful.
- **Verbs:** usually 3–4 present-tense person forms covering singular and plural.
- **Adjectives:** useful inflections, plus comparative/superlative when meaningful.
- **Pronouns:** common forms according to the pronoun's actual paradigm.
- **Adverbs:** usually none; comparative/superlative where natural.
- **Adpositions:** useful governed patterns.
- **Numerals:** useful case forms without a full paradigm.
- **Conjunctions, particles, interjections:** usually none.

### Special case
For `koti`, treat `kotona` and `kotoa` as lexicalized related forms:
- `kotona`: `related_location` + `related_form`
- `kotoa`: `related_source` + `related_form`
- `kotiin` remains `illative_singular` + `inflected_form`

## 3. Work completed

1. **Vocabulary classification:** completed for all 949 items, with corrections applied. Each item has `part_of_speech`, an optional `pos_subtype`, and `verb_type` for verbs (`ei` is a `negative_auxiliary` with no numbered type). The IDs match `contents.id`.
   - Data: [`backend/data-generation/vocabulary/vocabulary_classification.csv`](../../backend/data-generation/vocabulary/vocabulary_classification.csv)
   - Report: [`vocabulary_classification_report.md`](../../backend/data-generation/vocabulary/vocabulary_classification_report.md)
   - First-pass, primary-use classification; not dictionary-verified. Not imported into the database.
2. **Grammatical label standardization:** [grammatical-label-policy.md](grammatical-label-policy.md).
3. **Generation policy:** [form-generation-policy.md](form-generation-policy.md).
4. **Pilot generation:** 20 words and 82 form targets generated and reviewed, with the `koti` adjustments above. No duplicates and no headword targets.
   - Prompt: [`form_targets/prompts/form_generation_v1.md`](../../backend/data-generation/form_targets/prompts/form_generation_v1.md)
   - Output: [`form_targets/outputs/pilot/`](../../backend/data-generation/form_targets/outputs/pilot/)

Pilot sample:
- Nouns: `talo`, `koti`, `kahvi`, `ihminen`, `ystävä`
- Verbs: `puhua`, `olla`, `mennä`, `tehdä`, `saada`
- Adjectives: `hyvä`, `suuri`, `kaunis`
- Pronouns: `hän`, `tämä`, `joka`
- Adverbs: `usein`, `hyvin`
- Adposition: `ilman`
- Numeral: `yksi`

## 4. Current database state (for reference)

- `vocabulary_forms` contains the **v0** targets for topics 1–3 only (233 rows), imported by `backend/scripts/legacy_import_vocabulary_forms_v0.py` from [`legacy_v0/vocabulary_forms_topic_1_3.json`](../../backend/data-generation/legacy_v0/vocabulary_forms_topic_1_3.json). Source document: [legacy/wordforms-topic-1-3.md](legacy/wordforms-topic-1-3.md).
- 23 example sentences (words `eräs`, `hän`, `itse`) are linked to these v0 targets. Deleting the v0 targets cascades to the links and leaves the examples without targets; the plan is to remove these examples and regenerate them after the v1 import.
- Verified against a read-only database snapshot on 2026-11-20.
- The 82 pilot targets have not been imported.

## 5. Work not yet done

- Implement the batch-generation tool (prompt v2 with `target_type`).
- Implement automatic output validation.
- Generate form targets for all 949 words.
- Review generated results.
- Plan the replacement of v0 targets (including linked examples), back up the database, then import the approved v1 targets.

## 6. Generation workflow principles

- Input: `vocabulary_classification.csv`, which already contains IDs, words, topics and POS data. Reading from PostgreSQL is optional.
- Group by topic where useful, then split into small batches (default 15 words, range 10–20).
- Call the model using the reviewed generation prompt and a structured JSON schema.
- Validate every response before saving it.
- Save raw batch outputs locally and maintain a small manifest so interrupted work can resume.
- Keep generation separate from the runtime learning API. It is a data-maintenance workflow.
- Do not write generated data into PostgreSQL until it has passed review.

## 7. Current checkpoint

| Work item | Status |
|---|---|
| Vocabulary classification | Complete (first pass, corrected) |
| Grammatical label policy | Complete |
| Form generation policy | Complete (uses `target_type`) |
| Pilot generation and review | Complete |
| Decision: regenerate topics 1–3 | Made (2026-11-20) |
| Decision: field name `target_type` | Made (2026-11-20) |
| Prompt v2 | Not started |
| Batch generator | Not started |
| Bulk generation | Not started |
| Replacement of v0 targets and database import | Not started |
