# Form Target Generation — Checkpoint

**Status:** Done for all 949 words and imported into the database (2026-11-20). Next: example sentences.
**Last updated:** 2026-11-20

## 1. Goal

Give every Convi vocabulary item the Finnish forms and short patterns a learner needs most in common, everyday use. Common use matters more than grammatical coverage; simple, regular forms are valuable.

## 2. Decisions

- **Form target** = `form` (Finnish word or short phrase) + `grammatical_label` (plain `snake_case` string, no ENUM; [label policy](grammatical-label-policy.md)) + `target_type` (`inflected_form`, `related_form`, `governed_pattern`, `invariant`). No review or confidence fields in generated data.
- **Headword targets (option A):** the model never outputs the base form; the import adds one headword target per word (`nominative_singular`, `first_infinitive`, `invariant`; `ei` → `negative_verb_3sg`), so every word can get examples. A different form spelled like the headword is allowed (`antaa` as `present_3sg`).
- **Verbs:** present forms (3sg always), a few common extra forms, third infinitive for everyday action verbs (`syömään`), and 1–3 common collocations including ordinary objects (`juoda vettä`, `pitää kahvista`), labelled `<case>_complement` (also used for adpositions; `accusative_complement` for a total object).
- **No separate manual review:** automatic validation (and an optional Voikko check) is the gate. Imported rows are `active`; a row reported from the app becomes `needs_review` until fixed.
- `koti`: `kotona` / `kotoa` are `related_form` (`related_location` / `related_source`); `kotiin` is `illative_singular`.

Selection rules per part of speech: [form-generation-policy.md](form-generation-policy.md). Exact model instructions: [`form_generation_v3.md`](../../backend/data-generation/form_targets/prompts/form_generation_v3.md).

## 3. Result

| Item | Value |
| --- | --- |
| Input | [`vocabulary_classification.csv`](../../backend/data-generation/vocabulary/vocabulary_classification.csv) (POS, subtype, verb type; first-pass, not dictionary-verified) |
| Prompt / model | `form_generation_v3` / `gpt-6-luna` |
| Generated | 3,330 targets for 949 words in 73 topic batches ([`outputs/v3_all/`](../../backend/data-generation/form_targets/outputs/v3_all/)); 6 batches retried automatically after validation errors |
| Checks | Validator (schema, labels, duplicates, patterns, invisible characters); Voikko: 3 real errors fixed, 6 remaining findings are Voikko gaps |
| Corrections | 9 manual corrections, applied in `combined.json`. After the import, the per-batch model output and the corrections file were deleted: `combined.json` is the final data; later fixes go through app reports or a new generation run. |
| Imported | 4,279 rows in `vocabulary_forms` (949 headword + 3,330 generated), all `active`; the v0 targets and the 23 old examples were removed |

Tools: [batch tool design](form-target-batch-tool.md); commands in [`backend/scripts/README.md`](../../backend/scripts/README.md) (`generate_form_targets`, `check_form_targets`, `import_form_targets`).

## 4. Next

- Redeploy the backend (the deployed API only returns `reviewed` forms).
- Update the example validator: for a verb `governed_pattern`, check the complement word instead of the infinitive; then regenerate examples topic by topic.
- Optional: install Voikko on the Mac (`brew install libvoikko`, `pip install libvoikko`) so generation runs check forms automatically.
