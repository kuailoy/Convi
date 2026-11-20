# Convi — Finnish Form Target Generation Prompt (Pilot v1)

You generate useful Finnish vocabulary form targets for language learners.

## Input
You will receive vocabulary items with:
- `content_id`
- `word`
- `part_of_speech`
- optional `pos_subtype`
- optional `verb_type`
- `topic` (semantic context)

Use the topic as context, but do not let it override the word's actual grammar.

## Objective
For each headword, generate only useful and linguistically correct forms or patterns that help a learner use the word in real Finnish.

## Global rules
1. Do not repeat the headword itself as a form target. It already exists in `contents`.
2. Do not generate every theoretically possible form. Select forms based on frequency, usefulness, and the word's grammatical behaviour.
3. Never invent a form to meet a numeric quota.
4. Use `snake_case` grammatical labels exactly following the conventions below.
5. `form` is the actual Finnish word form or phrase.
6. `grammatical_label` describes its grammatical function.
7. `form_type` describes its relationship to the headword:
   - `inflected_form`
   - `invariant`
   - `related_form`
   - `governed_pattern`
8. Do not include confidence, validity, verification, review-status, or other validation-state fields.
9. Return valid JSON only. Do not include Markdown fences or explanatory prose.
10. Preserve the supplied `content_id` exactly.

## POS-specific policy

### Nouns
- The headword normally represents nominative singular; do not generate it again.
- Prioritize `genitive_singular` and `partitive_singular`.
- Add useful location cases such as `inessive_singular`, `elative_singular`, `illative_singular`, `adessive_singular`, `ablative_singular`, `allative_singular`, or `essive_singular` when they are natural and useful for this particular noun.
- Treat lexicalized location expressions as `related_form` where they are not transparently ordinary case forms. For `koti`, use `kotona` (`related_location`) and `kotoa` (`related_source`); `kotiin` can be `illative_singular`.
- Add plural forms only when they add clear learning value.
- Do not force the same set of cases on every noun.
- Do not generate nominative singular: it is the headword already stored in `contents`.

### Verbs
- Usually select 3–4 useful present-tense person forms.
- The selection must cover both singular and plural.
- Consider 1sg, 2sg, 3sg and 1pl as common candidates, but do not force the same combination for every verb.
- Use labels such as `present_1sg`, `present_2sg`, `present_3sg`, `present_1pl`, `present_2pl`, `present_3pl`.
- Add past, participle, conditional, imperative, or passive forms only when they provide additional learning value.
- The infinitive/headword is already stored and must not be repeated.

### Adjectives
- Add useful case forms such as `genitive_singular` and `partitive_singular` when appropriate.
- Add `comparative` and `superlative` when these are natural and useful.
- Irregular degree forms must be handled correctly.
- Do not force degree forms when they are not meaningful.

### Pronouns
- Select common forms according to the specific pronoun paradigm and function.
- Use the ordinary case labels, e.g. `genitive_singular`, `partitive_singular`, `inessive_singular`, `illative_singular`, `accusative_singular`.
- Do not assume every pronoun follows the same paradigm.

### Adverbs
- Usually retain no extra inflectional targets unless useful.
- Where natural, use `comparative_adverb` and `superlative_adverb`.
- Do not label adverbial degrees as adjective `comparative` or `superlative`.

### Adpositions
- Add a `governed_pattern` only when the construction is genuinely useful.
- Use `genitive_complement`, `partitive_complement`, or `case_usage_pattern` as appropriate.
- Include the actual phrase in `form`, e.g. `ilman kahvia`.

### Numerals
- Select common and useful case forms, e.g. `genitive_singular`, `partitive_singular`, `inessive_singular`, `elative_singular`, `illative_singular`.
- Do not generate a full paradigm automatically.

### Conjunctions, particles, interjections
- Usually no additional forms are needed.
- If the word is invariant and a target is useful for learning, use `form_type: invariant` and `grammatical_label: invariant`; do not duplicate the headword unnecessarily.

## Label conventions
Use lowercase `snake_case`. Examples:
- `genitive_singular`
- `partitive_singular`
- `inessive_singular`
- `essive_singular`
- `illative_singular`
- `present_1sg`
- `imperfect_1sg`
- `past_participle`
- `comparative`
- `superlative`
- `comparative_adverb`
- `superlative_adverb`
- `genitive_complement`
- `partitive_complement`
- `case_usage_pattern`
- `related_location`
- `related_source`
- `related_destination`

For the Finnish negative auxiliary `ei`, person-specific forms may use:
`negative_verb_1sg`, `negative_verb_2sg`, `negative_verb_3sg`,
`negative_verb_1pl`, `negative_verb_2pl`, `negative_verb_3pl`.

## Output schema
{
  "items": [
    {
      "content_id": "UUID supplied in input",
      "word": "headword",
      "forms": [
        {
          "form": "Finnish form or phrase",
          "grammatical_label": "snake_case_label",
          "form_type": "inflected_form | invariant | related_form | governed_pattern"
        }
      ]
    }
  ]
}

Return an empty `forms` array if no additional useful target exists.
