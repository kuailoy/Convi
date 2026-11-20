# Form Target Generation Policy — Finnish MVP

## 1. Purpose

Define which additional Finnish forms Convi should generate for a vocabulary headword.

The goal is to help learners use words in real sentences. Generate forms according to grammatical usefulness, lexical behaviour, frequency, topic context, and learner value.

Do not generate a fixed number of forms for every word. Do not create forms merely to fill a quota.

The aim is common, everyday Finnish, not full grammatical coverage. Simple, regular forms are valuable; include a common form even when it is easy or predictable (decided 2026-11-20).

## 2. Core concepts

Each generated form target should contain:

- `form`: the actual Finnish word form or useful phrase.
- `grammatical_label`: the grammatical role, expressed as a plain `snake_case` string. Follow `grammatical-label-policy.md`.
- `target_type`: the relationship between the target and its headword.

Allowed `target_type` values:

| Value | Meaning |
|---|---|
| `inflected_form` | A grammatical inflection of the headword |
| `invariant` | The headword target of a word that does not inflect; added by the import step, never generated |
| `related_form` | A lexicalized or closely related expression useful to learn with the headword |
| `governed_pattern` | A useful phrase or pattern governed by the headword, such as an adposition or a verb plus its complement (`ilman kahvia`, `pitää kahvista`) |

Do not confuse `grammatical_label` with `target_type`.

The headword is already stored in `contents`, and the model never generates it as a form target. The import step adds one headword target per word (see *Headword targets* in [grammatical-label-policy.md](grammatical-label-policy.md)), so every word has at least one target for example generation. If a word has no useful additional forms, the model returns an empty list.

## 3. Selection principles

For every headword:

1. Use its part of speech and relevant lexical properties.
2. Consider its topic as semantic context, not as a reason to override Finnish grammar.
3. Prefer common, useful forms that help learners build sentences.
4. Include irregular or especially useful forms when relevant.
5. Avoid obscure, rare, redundant, or unnatural forms.
6. Do not force every possible case, person, tense, or degree.
7. Do not invent a form when its grammatical or lexical status is uncertain.

## 4. Part-of-speech rules

### Nouns

- The headword normally represents nominative singular; do not duplicate it.
- Prioritize useful forms such as `genitive_singular` and `partitive_singular`.
- Add location cases (for example inessive, elative, illative, adessive, ablative, allative, or essive) when they are useful for the individual word.
- Add plural forms only when they provide meaningful learning value.
- Do not generate all Finnish cases for every noun.

Examples:
- `talo` → `talon`, `taloa`, optionally `talossa`, `talosta`, `taloon`
- `kahvi` → `kahvin`, `kahvia`, optionally `kahvissa`, `kahvista`, `kahviin`

Special handling:
- For `koti`, `kotona` and `kotoa` are treated as lexicalized related forms, not ordinary case inflections:
  - `kotona`: `related_location` + `related_form`
  - `kotoa`: `related_source` + `related_form`
  - `kotiin`: `illative_singular` + `inflected_form`

### Verbs

- Normally generate 3–4 useful present-tense person forms.
- Cover both singular and plural; a typical set may include 1st/2nd/3rd person singular and 1st person plural, but the model may choose a more useful combination.
- Add imperfect (simple past), participle, conditional, imperative, or passive forms only when useful.
- Keep a participle such as `puhunut` separate from a compound tense such as `olen puhunut`.
- Do not store a compound tense as though it were one inflected word form.
- Handle the negative auxiliary `ei` according to its special person forms; do not assign it an ordinary verb type if the lexical data marks it as a negative auxiliary.
- Mainly third-person verbs (`täytyä`, `kannattaa`, `tapahtua`) use third-person forms only; the singular-and-plural rule does not apply.
- Give `present_3sg` even when it is spelled like the infinitive (`antaa` → `antaa`); the label distinguishes it from the headword target.
- Give a third-infinitive form for everyday action verbs often used after `mennä`, `tulla`, `lähteä`, `käydä`, `oppia` or `joutua` (`syömään` = `third_infinitive_illative`; `käydä uimassa` = `third_infinitive_inessive` when very common).
- Add 1–3 common collocations (`governed_pattern`) for most verbs with an object or complement: ordinary objects (`juoda vettä`, `ostaa leipää` → `partitive_complement`; total object `ostaa auton` → `accusative_complement`) and complements in a case the learner has to memorize (`pitää kahvista` → `elative_complement`, `tutustua ihmiseen` → `illative_complement`).

Example:
- `puhua` → `puhun`, `puhut`, `puhuu`, `puhumme`

### Adjectives

- Include useful case forms where they help learners use the adjective.
- Add comparative and superlative forms when meaningful and commonly used.
- Examples:
  - `hyvä` → `hyvän`, `hyvää`, `parempi`, `paras`
  - `suuri` → `suuren`, `suurta`, `suurempi`, `suurin`
- Examples should demonstrate agreement with the noun where relevant.

### Pronouns

- Select common forms according to the actual paradigm of each pronoun.
- Do not assume all pronouns follow the same pattern.
- Example: `hän` → `hänet`, `häntä`, `hänen`, `hänelle`, `häneltä`

### Adverbs

- Usually generate no extra forms.
- Add comparative or superlative adverbs when natural and useful.
- Examples:
  - `usein` → `useammin`, `useimmin`
  - `hyvin` → `paremmin`, `parhaiten`

### Adpositions

- Generate useful governed patterns when they help learners use the adposition correctly.
- Example: `ilman` → `ilman kahvia`, with `target_type=governed_pattern` and an appropriate complement label such as `partitive_complement`.
- Name the complement case with `<case>_complement` (`kotiin asti` → `illative_complement`).

### Numerals

- Generate useful case forms without requiring a full paradigm.
- Example: `yksi` → `yhden`, `yhtä`, `yhdessä`, `yhdestä`, `yhteen`

### Conjunctions, particles, and interjections

- Usually do not need additional inflected forms.
- Generate no targets; the import step adds the headword as an `invariant` target.

## 5. Output constraints

- Return only forms that are useful and grammatically appropriate.
- Every target must refer to the correct source `content_id`.
- Every target must have a non-empty `form`, `grammatical_label`, and allowed `target_type`.
- Do not output the base form itself (it is added by the import step). A different grammatical form spelled like the headword is allowed (`antaa` → `antaa` as `present_3sg`), except `ei` → `ei`.
- Do not duplicate the same form within one headword.
- Do not add review metadata such as `valid`, `verified`, or `confidence`.
- Follow the output JSON Schema and the generation prompt used for the batch.

## 6. Related policy

- Label naming and allowed label conventions: [grammatical-label-policy.md](grammatical-label-policy.md)
- Exact model instructions and output format: [`form_generation_v3.md`](../../backend/data-generation/form_targets/prompts/form_generation_v3.md), with its JSON Schema and label list.
- Current progress and next steps: [FORM_TARGET_GENERATION_CHECKPOINT.md](FORM_TARGET_GENERATION_CHECKPOINT.md)

This policy describes the selection logic. The grammatical label policy defines how individual labels are named.
