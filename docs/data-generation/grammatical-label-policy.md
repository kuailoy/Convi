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
- `essive_singular`, `essive_plural`
- `translative_singular` (e.g. `suomeksi`, `saksaksi`)
- `genitive_singular`, `genitive_plural`
- `partitive_singular`, `partitive_plural`
- `accusative_singular`: only the `-t` accusative of personal pronouns and `kuka` (`minut`, `hänet`, `kenet`); never for nouns, adjectives or numerals
- `inessive_singular`, `inessive_plural`
- `elative_singular`, `elative_plural`
- `illative_singular`, `illative_plural`
- `adessive_singular`, `adessive_plural`
- `ablative_singular`, `ablative_plural`
- `allative_singular`, `allative_plural`

`nominative_singular` (and `nominative_plural` for an inherently plural headword) is also the label of the headword target added by the import step; see *Headword targets*.

Only use a case label when the form is genuinely an instance of that case. Do not infer a case from an English gloss such as “here”, “from” or “to”.

### Verbs
- `present_1sg`, `present_2sg`, `present_3sg`
- `present_1pl`, `present_2pl`, `present_3pl`
- `imperfect_1sg` (and other person/number combinations when useful)
- `past_participle`: the active `-nut/-nyt` participle (`puhunut`)
- `conditional_1sg` (and other person/number combinations when useful)
- `imperative_singular`, `imperative_plural`
- `passive_present`
- `third_infinitive_illative` (`puhumaan`), `third_infinitive_inessive` (`puhumassa`)
- `first_infinitive`: only for the headword target of a verb, added by the import step

For the negative auxiliary `ei`, use `negative_verb_1sg`, `negative_verb_2sg`, `negative_verb_3sg`, `negative_verb_1pl`, `negative_verb_2pl`, `negative_verb_3pl`. These labels describe the person-specific negative-verb forms (`en`, `et`, `ei`, `emme`, `ette`, `eivät`). Use `negative_imperative_singular` for `älä`. The form `ei` is the headword, so generation never outputs `negative_verb_3sg`; it is the label of the headword target of `ei`.

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
- `invariant` labels the headword target of a word that does not inflect (most adverbs, conjunctions, particles, interjections and adpositions, and indeclinable adjectives such as `koko`). The import step adds it; generation never outputs it.
- Do not use `invariant` as a substitute for a missing grammatical analysis of an inflected form.

### Headword targets
The model never generates the headword. Example sentences are generated per form target, so the import step adds one headword target per vocabulary item; this gives every word at least one target, including words with no other useful forms (decided 2026-11-20).

| Headword | `grammatical_label` | `target_type` |
|---|---|---|
| Noun, adjective, pronoun or numeral that inflects | `nominative_singular` (`nominative_plural` for an inherently plural headword such as `molemmat`) | `inflected_form` |
| Verb | `first_infinitive` (`ei`: `negative_verb_3sg`) | `inflected_form` |
| Word that does not inflect | `invariant` | `invariant` |

The `form` of a headword target is the headword exactly as stored in `contents`.

### Governed patterns
Name the case that the headword requires of its complement, as `<case>_complement`. The headword can be an adposition, a verb, an adjective or a numeral.
- `genitive_complement` — e.g. `ystävän kanssa`, `työn vuoksi`.
- `partitive_complement` — e.g. `ilman kahvia`, `matkaa varten`, `auttaa ystävää`, `juoda vettä`, `kaksi kahvia`.
- `accusative_complement` — a total object of a verb, e.g. `ostaa auton`.
- `elative_complement` — e.g. `pitää kahvista`, `aamusta asti`.
- `illative_complement` — e.g. `tutustua ihmiseen`, `kotiin asti`.
- `inessive_complement`, `adessive_complement`, `ablative_complement`, `allative_complement`, `essive_complement`, `translative_complement` (e.g. `muuttua vedeksi`) — when needed.
- `case_usage_pattern` — only for a fixed construction that is not one complement in one case, such as agreement with an indeclinable word: `koko päivän`.

A pattern is one contiguous phrase without slashes or alternatives, because an example sentence must contain it. A verb pattern is the infinitive plus one complement word (`pitää kahvista`).

### Lexicalized related forms
For related directional/locative families that are useful to learn together but are not ordinary inflection of the headword, use:
- `related_location`
- `related_source`
- `related_destination`

These are semantic labels, not Finnish grammatical case names. Keep `target_type = related_form`.

For the lexicalized home expressions of `koti`, use `kotona` → `related_location` and `kotoa` → `related_source` with `target_type = related_form`. Use `kotiin` → `illative_singular` with `target_type = inflected_form`.

## Generation policy reminders
- Nouns: the headword normally represents nominative singular, so do not duplicate it as a form target. Prioritize useful forms such as genitive and partitive; add location cases and plural forms only when useful for the individual word.
- Verbs: usually select 3–4 useful present-tense person forms, covering both singular and plural; do not force the same person set for every verb. Mainly third-person verbs use third-person forms only. Give `present_3sg` even when it is spelled like the infinitive. Add common collocations, including ordinary objects (`juoda vettä`, `pitää kahvista`), and a third-infinitive form for everyday action verbs (`syömään`).
- Adjectives: prioritize useful case forms and degree forms; the base form is the headword target added by the import step.
- Pronouns: choose forms according to the pronoun's paradigm and common usage.
- Adverbs, conjunctions, particles and interjections: usually no generated targets; the import step adds the headword as an `invariant` target. Do not invent inflections.
- Every generated form target should later be covered by at least one example. One example may cover multiple targets.

## Scope
This policy is for the Finnish MVP. It is a practical learning taxonomy, not an exhaustive linguistic ontology. Add a new label only when a real learning target requires it.
