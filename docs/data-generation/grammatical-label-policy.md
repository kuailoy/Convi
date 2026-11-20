# Convi — Finnish grammatical_label policy (MVP)

## Purpose
`grammatical_label` names the grammatical function of a vocabulary form. It is a plain string in `snake_case`; it is not a database ENUM and does not require a lookup table.

- `form` stores the actual Finnish word or phrase.
- `grammatical_label` identifies the grammatical form or usage represented.
- `target_type` continues to identify the relationship to the headword: `inflected_form`, `invariant`, `related_form`, or `governed_pattern`.

Do not mix these three concepts.

## Naming rules
1. Use lowercase `snake_case`.
2. Use full grammatical names for case, number, tense and person where relevant.
3. Use `1sg`, `2sg`, `3sg`, `1pl`, `2pl`, `3pl` for person/number shorthand.
4. Use a singular/plural suffix for case labels: e.g. `genitive_singular`, `inessive_plural`.
5. Do not encode the surface form in the label.
6. Do not create a target just to populate a label. If a word has no useful inflection or pattern, it can have no extra form target.
7. Keep `grammatical_label` as a string. New labels can be introduced when genuinely needed, following these conventions.

## Core label vocabulary

### Nominal cases
- `nominative_singular`, `nominative_plural`
- `essive_singular`
- `genitive_singular`, `genitive_plural`
- `partitive_singular`, `partitive_plural`
- `accusative_singular`
- `inessive_singular`, `inessive_plural`
- `elative_singular`, `elative_plural`
- `illative_singular`
- `adessive_singular`
- `ablative_singular`
- `allative_singular`

Only use a case label when the form is genuinely an instance of that case. Do not infer a case from an English gloss such as “here”, “from” or “to”.

### Verbs
- `present_1sg`, `present_2sg`, `present_3sg`
- `present_1pl`, `present_2pl`, `present_3pl`
- `imperfect_1sg` (and other person/number combinations when useful)
- `past_participle`
- `conditional_1sg` (and other person/number combinations when useful)
- `imperative_singular`
- `passive_present`

For the negative auxiliary `ei`, use `negative_verb_1sg`, `negative_verb_2sg`, `negative_verb_3sg`, `negative_verb_1pl`, `negative_verb_2pl`, `negative_verb_3pl`. These labels describe the person-specific negative-verb forms (`en`, `et`, `ei`, `emme`, `ette`, `eivät`).

### Adjectives and degree
- `comparative`
- `superlative`
- `comparative_adverb`
- `superlative_adverb`

When an adjective is inflected for a case, use the relevant nominal case label, e.g. `genitive_singular`.

### Pronouns and reflexive forms
Use the ordinary case labels for pronoun case forms where they fit (`genitive_singular`, `partitive_singular`, `inessive_singular`, etc.).
- `reflexive_3sg` for a third-person reflexive form such as `itsensä`.
- Possessive-suffix combinations may be made explicit when they are important: `accusative_singular_possessive_1sg`, `partitive_singular_possessive_1sg`.

### Invariant words
- `invariant` for an unchanged word whose useful learning target is its invariant usage.
- Do not use `invariant` as a substitute for a missing grammatical analysis of an inflected form.

### Governed patterns
Use a label that describes the complement or pattern:
- `genitive_complement` — e.g. `ystävän kanssa`, `työn vuoksi`.
- `partitive_complement` — e.g. `ilman kahvia`, `matkaa varten`.
- `case_usage_pattern` — a phrase showing a broader case/usage alternation or agreement pattern, e.g. `koko päivä / koko päivän / koko päivää`.

### Lexicalized related forms
For related directional/locative families that are useful to learn together but are not ordinary inflection of the headword, use:
- `related_location`
- `related_source`
- `related_destination`

These are semantic labels, not Finnish grammatical case names. Keep `target_type = related_form`.

For the lexicalized home expressions of `koti`, use `kotona` → `related_location` and `kotoa` → `related_source` with `target_type = related_form`. Use `kotiin` → `illative_singular` with `target_type = inflected_form`.

## Generation policy reminders
- Nouns: the headword normally represents nominative singular, so do not duplicate it as a form target. Prioritize useful forms such as genitive and partitive; add location cases and plural forms only when useful for the individual word.
- Verbs: usually select 3–4 useful present-tense person forms, covering both singular and plural; do not force the same person set for every verb.
- Adjectives: prioritize the base form and useful degree forms; add case forms when they have learning value.
- Pronouns: choose forms according to the pronoun's paradigm and common usage.
- Adverbs, conjunctions, particles and interjections: usually keep only the invariant target when useful; do not invent inflections.
- Every generated form target should later be covered by at least one example. One example may cover multiple targets.

## Scope
This policy is for the Finnish MVP. It is a practical learning taxonomy, not an exhaustive linguistic ontology. Add a new label only when a real learning target requires it.
