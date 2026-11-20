"""Optional morphological check of form targets with Voikko.

Voikko is a free Finnish spell checker and morphological analyser. When the
`libvoikko` Python package and the native library with the Finnish dictionary
are installed, `VoikkoChecker.create()` returns a checker; otherwise it returns
None and the check is skipped. All findings are warnings: Voikko's dictionary
has gaps, so a finding means "look at this", not "this is wrong".

Install on macOS:  brew install libvoikko   (includes the Finnish dictionary)
                   pip install libvoikko
On Ubuntu/Debian:  apt install libvoikko1 voikko-fi python3-libvoikko
"""

from __future__ import annotations

import re
import unicodedata

CASES = {
    "nominative": "nimento",
    "genitive": "omanto",
    "partitive": "osanto",
    "accusative": "kohdanto",
    "essive": "olento",
    "translative": "tulento",
    "inessive": "sisaolento",
    "elative": "sisaeronto",
    "illative": "sisatulento",
    "adessive": "ulkoolento",
    "ablative": "ulkoeronto",
    "allative": "ulkotulento",
}
_CASE_LABEL = re.compile(r"^(" + "|".join(CASES) + r")_(singular|plural)$")
_PERSON_LABEL = re.compile(r"^(present|imperfect|conditional)_([123])(sg|pl)$")
_NEGATIVE_LABEL = re.compile(r"^negative_verb_([123])(sg|pl)$")
_COMPLEMENT_LABEL = re.compile(r"^(" + "|".join(CASES) + r")_complement$")
_TOKEN = re.compile(r"[^\W\d_]+(?:[-:][^\W\d_]+)*")


def expected_features(label: str) -> list[dict[str, str]] | None:
    """Voikko features that a form with this label must have (any one alternative), or None if not checked."""
    match = _CASE_LABEL.match(label)
    if match:
        return [{"SIJAMUOTO": CASES[match.group(1)], "NUMBER": match.group(2)}]
    match = _PERSON_LABEL.match(label)
    if match:
        tense, person, number = match.groups()
        features = {"PERSON": person, "NUMBER": "singular" if number == "sg" else "plural"}
        if tense == "present":
            features.update(MOOD="indicative", TENSE="present_simple")
        elif tense == "imperfect":
            features.update(MOOD="indicative", TENSE="past_imperfective")
        else:
            features.update(MOOD="conditional")
        return [features]
    match = _NEGATIVE_LABEL.match(label)
    if match:
        return [{"CLASS": "kieltosana", "PERSON": match.group(1),
                 "NUMBER": "singular" if match.group(2) == "sg" else "plural"}]
    return {
        "imperative_singular": [{"MOOD": "imperative", "PERSON": "2", "NUMBER": "singular"}],
        "imperative_plural": [{"MOOD": "imperative", "PERSON": "2", "NUMBER": "plural"}],
        "negative_imperative_singular": [{"CLASS": "kieltosana", "MOOD": "imperative"}],
        "passive_present": [{"PERSON": "4", "TENSE": "present_simple"}],
        "past_participle": [{"PARTICIPLE": "past_active"}],
        "third_infinitive_illative": [{"MOOD": "MA-infinitive", "SIJAMUOTO": "sisatulento"}],
        "third_infinitive_inessive": [{"MOOD": "MA-infinitive", "SIJAMUOTO": "sisaolento"}],
        "comparative": [{"COMPARISON": "comparative"}],
        "superlative": [{"COMPARISON": "superlative"}],
        # Adverb degree forms (paremmin, eniten) are not analysed for degree by Voikko: not checked.
    }.get(label)


def complement_cases(label: str) -> set[str] | None:
    if label == "accusative_complement":  # total object: -n (genitive form) or nominative form
        return {"omanto", "nimento", "kohdanto"}
    match = _COMPLEMENT_LABEL.match(label)
    return {CASES[match.group(1)]} if match else None


class VoikkoChecker:
    def __init__(self, voikko) -> None:
        self._voikko = voikko
        self._cache: dict[str, list[dict]] = {}

    @classmethod
    def create(cls) -> "VoikkoChecker | None":
        try:
            import libvoikko

            return cls(libvoikko.Voikko("fi"))
        except Exception:  # package, native library or dictionary missing
            return None

    def analyze(self, word: str) -> list[dict]:
        if word not in self._cache:
            self._cache[word] = [dict(a) for a in self._voikko.analyze(word)]
        return self._cache[word]

    def known(self, word: str) -> bool:
        return bool(self._voikko.spell(word)) and bool(self.analyze(word))

    def check(self, word: str, pos: str, form: str, label: str, target_type: str) -> list[tuple[str, str]]:
        """Return (code, message) findings for one target."""
        if any(unicodedata.category(ch) == "Cf" for ch in form):
            return [("voikko_unknown", "Form contains an invisible character.")]
        if target_type == "governed_pattern":
            return self._check_pattern(word, form, label)

        analyses = self.analyze(form)
        if not self._voikko.spell(form) or not analyses:
            return [("voikko_unknown", "Voikko does not recognise this form.")]
        if target_type == "related_form":
            return []

        # Accept the headword and whatever Voikko gives as its base form (paras -> hyvä).
        bases = {word.casefold()} | {a.get("BASEFORM", "").casefold() for a in self.analyze(word)}
        # Voikko gives participles (ollut) and some pronoun forms (nämä) their own base form.
        check_base = pos not in ("pronoun", "adverb") and not label.endswith("_adverb") and label != "past_participle"
        candidates = [a for a in analyses if a.get("BASEFORM", "").casefold() in bases] if check_base else analyses
        if not candidates:
            found = ", ".join(sorted({a.get("BASEFORM", "?") for a in analyses}))
            return [("voikko_baseform", f"Voikko reads this as a form of '{found}', not '{word}'.")]

        expected = expected_features(label)
        if expected and not any(all(a.get(k) == v for k, v in alt.items()) for a in candidates for alt in expected):
            return [("voikko_label", f"Voikko does not analyse this as '{label}'.")]
        return []

    def _check_pattern(self, word: str, form: str, label: str) -> list[tuple[str, str]]:
        tokens = _TOKEN.findall(form)
        unknown = [t for t in tokens if t.casefold() != word.casefold() and not self.known(t)]
        if unknown:
            return [("voikko_unknown", f"Voikko does not recognise: {', '.join(unknown)}.")]
        cases = complement_cases(label)
        if cases is None:
            return []
        complements = [t for t in tokens if t.casefold() != word.casefold()]
        if complements and not any(a.get("SIJAMUOTO") in cases for t in complements for a in self.analyze(t)):
            return [("voikko_complement", f"No complement word is analysed in the case required by '{label}'.")]
        return []
