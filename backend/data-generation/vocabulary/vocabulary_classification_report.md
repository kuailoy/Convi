# Task 1 — Vocabulary Classification (Fixed)

## Result

- 949 vocabulary records retained.
- Original IDs, words, and topic references retained.
- All 949 records have a `part_of_speech`.
- 268 verbs have a numbered `verb_type`.
- `ei` remains a verb (`negative_auxiliary`) but has no numbered verb type.
- Non-verbs have a null `verb_type`.
- Duplicate IDs and duplicate words: none.

## Corrections applied

| Word | Previous value | Fixed value |
|---|---|---|
| `oma` | pronoun / indefinite_or_quantifier | adjective / pronominal_adjective |
| `usea` | pronoun / indefinite_or_quantifier | adjective |
| `idiootti` | adjective | noun |
| `viimeinen` | numeral / ordinal | adjective / ordinal_adjective |
| `mukana` | adposition / postposition_or_preposition | adverb |
| `selvitä` | verb type 5 | verb type 4 |
| `hävitä` | verb type 5 | verb type 4 |

`vanhempi`, `jopa`, and `tosi` were retained as previously classified. Their possible secondary uses do not require changing the primary classification for this dataset.

## Removed fields

The following generation/review metadata fields were removed:

- `classification_confidence`
- `classification_note`
- `classification_status`
- `verb_type_status`

The fixed CSV contains only classification data and original identifiers/topic references. No validation-status or confidence fields are included.

## Part-of-speech distribution

- noun: 324
- verb: 269
- adverb: 143
- adjective: 112
- pronoun: 29
- adposition: 25
- conjunction: 19
- particle: 15
- numeral: 12
- interjection: 1

## Numbered verb type distribution

- Type 1: 187
- Type 2: 13
- Type 3: 25
- Type 4: 37
- Type 5: 6

## Remaining limitations

- POS is a primary/common-use classification, not a complete record of every possible lexical use.
- Some words can function as more than one part of speech depending on context.
- Numbered verb types are a first-pass classification; inflection paradigms have not been exhaustively checked.
- No database was modified. This file is an updated dataset for review/import.
