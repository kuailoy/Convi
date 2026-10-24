"""Generate a Pattern Drill set with the OpenAI API."""

import json

from openai import OpenAI


def generate_exercises(pattern, exercise_count):
    """Ask the model to choose substitutions for a sentence pattern."""
    if pattern.count("{place}") != 1:
        raise ValueError("The pattern must contain exactly one {place} slot.")

    if exercise_count < 1:
        raise ValueError("Exercise count must be at least 1.")

    schema = {
        "type": "object",
        "properties": {
            "substitutions": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "required": ["substitutions"],
        "additionalProperties": False,
    }

    client = OpenAI()
    response = client.responses.create(
        model="gpt-6-luna",
        instructions=(
            "Create English Pattern Drill substitutions. A Pattern Drill helps a learner "
            "internalize one reusable sentence pattern by repeating it with different words "
            "or phrases in one slot. Choose natural, common, everyday English phrases that "
            "fit the meaning and grammar of the {place} slot in the supplied pattern. "
            "Choose distinct substitutions. Return only the substitutions, with exactly "
            "the requested number of items. Do not explain or complete the sentences."
        ),
        input=(
            "Sentence pattern: "
            + pattern
            + "\nThe {place} slot represents a destination."
            + "\nGenerate this many different substitutions: "
            + str(exercise_count)
        ),
        text={
            "format": {
                "type": "json_schema",
                "name": "pattern_drill_substitutions",
                "strict": True,
                "schema": schema,
            }
        },
    )

    result = json.loads(response.output_text)
    substitutions = result["substitutions"]

    if len(substitutions) != exercise_count:
        raise ValueError(
            "The model returned "
            + str(len(substitutions))
            + " substitutions; expected "
            + str(exercise_count)
            + ". Please try again."
        )

    exercises = []
    for index, substitution in enumerate(substitutions):
        answer = pattern.replace("{place}", substitution)
        exercise = {
            "number": index + 1,
            "prompt": "Replace {place} with: " + substitution,
            "substitution": substitution,
            "answer": answer,
        }
        exercises.append(exercise)

    return exercises
