"""Basic deterministic checks for generated Finnish example sentences."""

import re
import unicodedata


_WORD = re.compile(r"[\wÅÄÖåäö]+", re.UNICODE)


def normalize_sentence(sentence: str) -> str:
    normalized = unicodedata.normalize("NFKC", sentence).casefold()
    return " ".join(_WORD.findall(normalized))


def validate_example(target: dict[str, str | None], candidate: dict[str, str]) -> tuple[str, str | None, str]:
    sentence = candidate["finnish_sentence"].strip()
    translation = candidate["english_translation"].strip()
    tokens = set(_WORD.findall(unicodedata.normalize("NFKC", sentence).casefold()))
    lemma = target["lemma"]

    if not sentence or not translation:
        return "rejected", "Finnish sentence or English translation is empty.", ""
    if candidate["difficulty"] not in {"A1", "A2"}:
        return "rejected", "Difficulty must be A1 or A2.", normalize_sentence(sentence)
    if len(_WORD.findall(sentence)) > 14:
        return "rejected", "Sentence exceeds the 14-word pilot limit.", normalize_sentence(sentence)

    if target["target_type"] == "governed_pattern":
        if lemma.casefold() not in tokens:
            return "rejected", f"Required relational word '{lemma}' does not appear as a token.", normalize_sentence(sentence)
        return (
            "needs_review",
            "Case government and naturalness need manual review; no Finnish morphology analyzer is configured.",
            normalize_sentence(sentence),
        )

    target_form = target["form"]
    if target_form.casefold() not in tokens:
        return (
            "rejected",
            f"Required target form '{target_form}' does not appear as a separate token.",
            normalize_sentence(sentence),
        )
    return "auto_valid", None, normalize_sentence(sentence)
