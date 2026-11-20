"""Validate model output for Finnish form-target generation (prompt v3).

Errors reject a batch. Warnings are kept with the accepted output so that
problems can be found later; they never block a batch.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

MAX_FORMS = 10
MAX_NOTE_LENGTH = 120
TARGET_TYPES = {"inflected_form", "related_form", "governed_pattern"}
CLOSED_CLASSES = {"conjunction", "particle", "interjection"}
NOMINAL_POS = {"noun", "adjective", "pronoun", "numeral"}

# Typical number of generated targets per part of speech (prompt v3, rule 10).
TYPICAL_COUNTS = {
    "noun": (2, 5),
    "verb": (4, 8),
    "adjective": (2, 4),
    "pronoun": (3, 6),
    "numeral": (2, 4),
    "adposition": (1, 2),
    "adverb": (0, 2),
    "conjunction": (0, 0),
    "particle": (0, 0),
    "interjection": (0, 0),
}

_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_FORM_CHARS = re.compile(r"^[a-zåäöšž]+(?:[ :-][a-zåäöšž]+)*$", re.IGNORECASE)
_VERB_LABEL = re.compile(
    r"^(present|imperfect|conditional|imperative|negative|passive|past_participle|third_infinitive)"
)
_CASE_LABEL = re.compile(r"_(singular|plural)$|^accusative_singular")
_PRONOUN_ONLY = re.compile(r"^reflexive_|_possessive_")


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold()


@dataclass
class LabelSet:
    labels: set[str]
    patterns: list[re.Pattern[str]]
    governed: set[str]
    related: set[str]

    @classmethod
    def load(cls, path: Path) -> "LabelSet":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            labels=set(data["labels"]),
            patterns=[re.compile(p) for p in data.get("label_patterns", [])],
            governed=set(data["governed_pattern_labels"]),
            related=set(data["related_form_labels"]),
        )

    def allows(self, label: str) -> bool:
        return label in self.labels or any(p.match(label) for p in self.patterns)

    def expected_target_type(self, label: str) -> str:
        if label in self.governed:
            return "governed_pattern"
        if label in self.related:
            return "related_form"
        return "inflected_form"


@dataclass
class Issue:
    code: str
    message: str
    content_id: str | None = None
    form: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {"code": self.code, "message": self.message, "content_id": self.content_id, "form": self.form}


@dataclass
class ValidationResult:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_batch(
    input_items: list[dict],
    output: object,
    labels: LabelSet,
    all_headwords: set[str] | None = None,
    voikko=None,
) -> ValidationResult:
    """Check one batch of model output against its input items.

    `input_items` are the items sent to the model (with `content_id`, `word`,
    `part_of_speech`, `pos_subtype`). `all_headwords` contains the normalized
    headwords of the whole vocabulary, for cross-headword warnings. `voikko` is an
    optional `VoikkoChecker`; its findings are added as warnings.
    """
    result = ValidationResult()
    err = lambda code, msg, cid=None, form=None: result.errors.append(Issue(code, msg, cid, form))
    warn = lambda code, msg, cid=None, form=None: result.warnings.append(Issue(code, msg, cid, form))

    if not isinstance(output, dict) or set(output) != {"items"} or not isinstance(output["items"], list):
        err("structure", "Top level must be an object with only an 'items' array.")
        return result
    items = output["items"]

    expected_ids = [item["content_id"] for item in input_items]
    received_ids = [item.get("content_id") if isinstance(item, dict) else None for item in items]
    if received_ids != expected_ids:
        missing = [cid for cid in expected_ids if cid not in received_ids]
        extra = [cid for cid in received_ids if cid not in expected_ids]
        err(
            "items_mismatch",
            f"Items must match the input in number and order (missing {len(missing)}, extra {len(extra)}).",
        )
        return result

    headwords = all_headwords or set()
    for source, item in zip(input_items, items):
        _validate_item(source, item, labels, headwords, err, warn, voikko)
    return result


def _validate_item(source, item, labels, headwords, err, warn, voikko=None) -> None:
    cid = source["content_id"]
    word = source["word"]
    pos = source["part_of_speech"]
    subtype = source.get("pos_subtype")

    if not isinstance(item, dict) or set(item) != {"content_id", "word", "forms"}:
        err("structure", "Item must have exactly content_id, word and forms.", cid)
        return
    if not _UUID.match(str(item["content_id"])):
        err("structure", "content_id is not a UUID.", cid)
    if item["word"] != word:
        err("word_mismatch", f"word is '{item['word']}', expected '{word}'.", cid)
    forms = item["forms"]
    if not isinstance(forms, list):
        err("structure", "forms must be an array.", cid)
        return
    if len(forms) > MAX_FORMS:
        err("too_many_forms", f"{len(forms)} forms; the maximum is {MAX_FORMS}.", cid)

    seen_forms: set[str] = set()
    seen_labels: set[str] = set()
    word_norm = normalize(word)
    has_present = False

    for target in forms:
        if not isinstance(target, dict) or set(target) != {"form", "grammatical_label", "target_type", "notes"}:
            err("structure", "Target must have exactly form, grammatical_label, target_type and notes.", cid)
            continue
        form, label, ttype, notes = (target[k] for k in ("form", "grammatical_label", "target_type", "notes"))
        if not all(isinstance(v, str) for v in (form, label, ttype, notes)):
            err("structure", "Target fields must be strings.", cid)
            continue
        if not form.strip() or form != form.strip():
            err("structure", "form is empty or has surrounding whitespace.", cid, form)
            continue

        if any(unicodedata.category(ch) == "Cf" for ch in form):
            err("invisible_character", "Form contains an invisible character (e.g. a soft hyphen).", cid, form)
            continue
        form_norm = normalize(form)
        tokens = form_norm.split()

        if ttype not in TARGET_TYPES:
            err("target_type", f"target_type '{ttype}' is not allowed.", cid, form)
        # A different grammatical form may be spelled like the headword (antaa -> antaa, present_3sg).
        # Not allowed: ei -> ei (stored as the headword target), or a pattern/related form equal to it.
        if form_norm == word_norm and (subtype == "negative_auxiliary" or ttype != "inflected_form"):
            err("headword", "Form duplicates the headword target.", cid, form)
        if form_norm in seen_forms:
            err("duplicate_form", "Form appears twice in this item.", cid, form)
        seen_forms.add(form_norm)

        if not labels.allows(label):
            err("label", f"Label '{label}' is not in the allowlist.", cid, form)
        else:
            expected = labels.expected_target_type(label)
            if ttype in TARGET_TYPES and ttype != expected:
                err("label_type", f"Label '{label}' requires target_type '{expected}', got '{ttype}'.", cid, form)
        if ttype != "governed_pattern":
            if label in seen_labels:
                err("duplicate_label", f"Label '{label}' appears twice in this item.", cid, form)
            seen_labels.add(label)

        if ttype in ("inflected_form", "related_form") and len(tokens) != 1:
            err("multiword", f"{ttype} must be a single word.", cid, form)
        if ttype == "governed_pattern":
            if pos == "verb":
                if len(tokens) != 2 or tokens[0] != word_norm:
                    err("verb_pattern", "Verb pattern must be the infinitive followed by one complement word.", cid, form)
            elif word_norm not in tokens:
                err("pattern_headword", "Pattern must contain the headword unchanged as a separate word.", cid, form)

        # Warnings
        if form_norm in headwords and form_norm != word_norm:
            warn("other_headword", "Form is also a separate headword in the vocabulary.", cid, form)
        if not _FORM_CHARS.match(form):
            warn("characters", "Form contains unexpected characters.", cid, form)
        if word == word.lower() and form != form.lower():
            warn("capitalization", "Form has capital letters but the headword does not.", cid, form)
        if len(notes) > MAX_NOTE_LENGTH:
            warn("long_note", f"Note is longer than {MAX_NOTE_LENGTH} characters.", cid, form)
        mismatch = _label_pos_mismatch(label, pos, subtype)
        if mismatch:
            warn("label_pos", mismatch, cid, form)
        if label.startswith("present_"):
            has_present = True
        if voikko is not None and ttype in TARGET_TYPES:
            for code, message in voikko.check(word, pos, form, label, ttype):
                warn(code, message, cid, form)

    count = len(forms)
    if pos in CLOSED_CLASSES and count:
        warn("closed_class_forms", f"{pos} usually has no targets; got {count}.", cid)
    elif pos in TYPICAL_COUNTS:
        low, high = TYPICAL_COUNTS[pos]
        if not low <= count <= high:
            warn("count", f"{count} targets; typical for {pos} is {low}-{high}.", cid)
    if pos == "verb" and subtype != "negative_auxiliary" and not has_present:
        warn("verb_no_present", "Verb has no present-tense form.", cid)


def _label_pos_mismatch(label: str, pos: str, subtype: str | None) -> str | None:
    if _VERB_LABEL.match(label) and pos != "verb":
        return f"Verb label '{label}' on a {pos}."
    if label.startswith("negative_") and subtype != "negative_auxiliary":
        return f"Label '{label}' is only for the negative auxiliary."
    if label in ("comparative", "superlative") and pos != "adjective":
        return f"Adjective degree label '{label}' on a {pos}."
    if label in ("comparative_adverb", "superlative_adverb") and pos != "adverb":
        return f"Adverb degree label '{label}' on a {pos}."
    if _PRONOUN_ONLY.search(label) and pos != "pronoun":
        return f"Label '{label}' is only for pronouns."
    if label == "accusative_singular" and pos != "pronoun":
        return "accusative_singular is only for pronouns."
    if _CASE_LABEL.search(label) and not _VERB_LABEL.match(label) and pos not in NOMINAL_POS:
        return f"Case label '{label}' on a {pos}."
    return None
