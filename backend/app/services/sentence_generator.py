"""Generate one short Finnish example sentence for a vocabulary target."""

import json

from openai import OpenAI


DEFAULT_MODEL = "gpt-6-luna"
PROMPT_VERSION = "fi-example-v4-register-aware"
_CASE_NAMES = {
    "N sg": "nominative singular",
    "G sg": "genitive singular",
    "P sg": "partitive singular",
    "N pl": "nominative plural",
    "G pl": "genitive plural",
    "P pl": "partitive plural",
}


def generate_example(target: dict[str, str | None], model: str = DEFAULT_MODEL) -> dict[str, str]:
    schema = {
        "type": "object",
        "properties": {
            "spoken_finnish_sentence": {"type": "string"},
            "written_finnish_sentence": {"type": "string"},
            "english_translation": {"type": "string"},
            "difficulty": {"type": "string", "enum": ["A1", "A2"]},
        },
        "required": [
            "spoken_finnish_sentence",
            "written_finnish_sentence",
            "english_translation",
            "difficulty",
        ],
        "additionalProperties": False,
    }

    if target["target_type"] == "governed_pattern":
        target_instruction = (
            "For this case/usage target, include the vocabulary lemma as a separate token and "
            "follow the stated case requirement and example."
        )
    else:
        target_instruction = (
            "Include the exact requested target form as a separate Finnish word token, "
            "preserving its spelling."
        )

    client = OpenAI()
    response = client.responses.create(
        model=model,
        instructions=(
            "Create a pair of equivalent, short Finnish sentences for a beginner: one natural "
            "everyday spoken Finnish version (common puhekieli, without regional slang), and one "
            "standard written Finnish version. The target lemma, specific form, or grammatical use may "
            "itself be formal or mainly written: do not force it into colloquial speech. In that case, "
            "use a natural sentence appropriate to the target's register; use identical wording in both "
            "fields when no natural spoken alternative fits. Use simple A1-A2 grammar and familiar words. "
            "The main learning objective is the supplied vocabulary target. Choose its most common "
            "everyday meaning and use the most typical natural expression. Keep other words very "
            "common, concrete, and easy; ideally the target is the only unfamiliar or abstract item. "
            "Prefer one simple main clause, usually about four to eight words. Prefer present tense, "
            "basic past, or simple negation. Avoid abstract nouns, nominalizations, subordinate clauses, "
            "participles, passive constructions, idioms, technical terms, and rare supporting words. "
            "Do not make the sentence artificially complex just to force the form into it. "
            "If the target vocabulary is mainly formal or written, or if there is no meaningful "
            "register difference, return the same sentence in both fields. The pair must preserve "
            "the same meaning and demonstrate the target in its intended grammatical use. "
            + target_instruction
            + " Provide an accurate, natural English translation. "
            "Do not explain grammar or add alternatives."
        ),
        input=(
            f"Vocabulary lemma: {target['lemma']}\n"
            f"Target form or usage: {target['form']}\n"
            f"Grammatical label: {_CASE_NAMES.get(target['grammatical_label'], target['grammatical_label'])}\n"
            f"Target type: {target['target_type']}\n"
            f"Notes: {target.get('notes') or 'None'}"
        ),
        text={
            "format": {
                "type": "json_schema",
                "name": "finnish_vocabulary_example",
                "strict": True,
                "schema": schema,
            }
        },
    )
    result = json.loads(response.output_text)
    return {
        "spoken_finnish_sentence": result["spoken_finnish_sentence"].strip(),
        "written_finnish_sentence": result["written_finnish_sentence"].strip(),
        "english_translation": result["english_translation"].strip(),
        "difficulty": result["difficulty"],
    }
