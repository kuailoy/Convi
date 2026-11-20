# Form Target Generation Policy — Finnish MVP

## 1. Purpose

Define which additional Finnish forms Convi should generate for a vocabulary headword.

The goal is to help learners use words in real sentences. Generate forms according to grammatical usefulness, lexical behaviour, frequency, topic context, and learner value.

Do not generate a fixed number of forms for every word. Do not create forms merely to fill a quota.

## 2. Core concepts

Each generated form target should contain:

- `form`: the actual Finnish word form or useful phrase.
- `grammatical_label`: the grammatical role, expressed as a plain `snake_case` string. Follow `grammatical-label-policy.md`.
- `target_type`: the relationship between the target and its headword.

Allowed `target_type` values:

| Value | Meaning |
|---|---|
| `inflected_form` | A grammatical inflection of the headword |
| `invariant` | An unchanged form included because it has a useful learning role |
| `related_form` | A lexicalized or closely related expression useful to learn with the headword |
| `governed_pattern` | A useful phrase or pattern governed by the headword, such as an adposition plus its complement |

Do not confuse `grammatical_label` with `target_type`.

The headword is already stored in `contents`. Do not repeat it as a form target. If a word has no useful additional forms, return an empty list.

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

### Numerals

- Generate useful case forms without requiring a full paradigm.
- Example: `yksi` → `yhden`, `yhtä`, `yhdessä`, `yhdestä`, `yhteen`

### Conjunctions, particles, and interjections

- Usually do not need additional inflected forms.
- Do not duplicate the headword as an `invariant` target.
- Add an invariant target only when there is a clear learning reason.

## 5. Output constraints

- Return only forms that are useful and grammatically appropriate.
- Every target must refer to the correct source `content_id`.
- Every target must have a non-empty `form`, `grammatical_label`, and allowed `target_type`.
- Do not include the headword itself as a target.
- Do not duplicate the same form within one headword.
- Do not add review metadata such as `valid`, `verified`, or `confidence`.
- Follow the output JSON Schema and the generation prompt used for the batch.

## 6. Related policy

- Label naming and allowed label conventions: [grammatical-label-policy.md](grammatical-label-policy.md)
- Exact model instructions and output format: [`backend/data-generation/form_targets/prompts/form_generation_v1.md`](../../backend/data-generation/form_targets/prompts/form_generation_v1.md) (pilot prompt v1, which still uses the earlier field name `form_type`; the next prompt version uses `target_type`)
- Current progress and next steps: [FORM_TARGET_GENERATION_CHECKPOINT.md](FORM_TARGET_GENERATION_CHECKPOINT.md)

This policy describes the selection logic. The grammatical label policy defines how individual labels are named.
