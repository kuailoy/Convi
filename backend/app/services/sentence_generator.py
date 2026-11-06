"""Generate one short Finnish example sentence for a vocabulary target."""

import json

from openai import OpenAI


DEFAULT_MODEL = "gpt-6-luna"
PROMPT_VERSION = "fi-example-v1"
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
            "finnish_sentence": {"type": "string"},
            "english_translation": {"type": "string"},
            "difficulty": {"type": "string", "enum": ["A1", "A2"]},
        },
        "required": ["finnish_sentence", "english_translation", "difficulty"],
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
            "Create exactly one natural, short, everyday Finnish example sentence for a beginner. "
            "Use simple A1-A2 grammar and familiar words. The sentence must demonstrate the target "
            "in its intended grammatical use. "
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
        "finnish_sentence": result["finnish_sentence"].strip(),
        "english_translation": result["english_translation"].strip(),
        "difficulty": result["difficulty"],
    }
