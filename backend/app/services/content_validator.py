"""Basic deterministic checks for generated Finnish example sentences."""

import re
import unicodedata


_WORD = re.compile(r"[\wÅÄÖåäö]+", re.UNICODE)


def normalize_sentence(sentence: str) -> str:
    normalized = unicodedata.normalize("NFKC", sentence).casefold()
    return " ".join(_WORD.findall(normalized))


def validate_example(target: dict[str, str | None], candidate: dict[str, str]) -> tuple[str, str | None, str]:
    spoken = candidate["spoken_finnish_sentence"].strip()
    written = candidate["written_finnish_sentence"].strip()
    translation = candidate["english_translation"].strip()
    spoken_tokens = set(_WORD.findall(unicodedata.normalize("NFKC", spoken).casefold()))
    written_tokens = set(_WORD.findall(unicodedata.normalize("NFKC", written).casefold()))
    lemma = target["lemma"]

    normalized = normalize_sentence(spoken)
    if not spoken or not written or not translation:
        return "rejected", "Spoken sentence, written sentence, or translation is empty.", normalized
    if candidate["difficulty"] not in {"A1", "A2"}:
        return "rejected", "Difficulty must be A1 or A2.", normalized
    if len(_WORD.findall(spoken)) > 14 or len(_WORD.findall(written)) > 14:
        return "rejected", "A sentence exceeds the 14-word pilot limit.", normalized

    if target["target_type"] == "governed_pattern":
        if lemma.casefold() not in spoken_tokens | written_tokens:
            return "rejected", f"Required relational word '{lemma}' does not appear as a token.", normalized
        return (
            "needs_review",
            "Case government and naturalness need manual review; no Finnish morphology analyzer is configured.",
            normalized,
        )

    target_form = target["form"]
    if target_form.casefold() not in spoken_tokens | written_tokens:
        return (
            "rejected",
            f"Required target form '{target_form}' does not appear as a separate token in either version.",
            normalized,
        )
    return "auto_valid", None, normalized
