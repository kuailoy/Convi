"""Problem reports sent from the app.

A report records what the learner saw and flags the reported row so it can be
fixed later: a word-form report marks the form `needs_review`; a sentence,
translation or other report about an example marks the example `needs_review`.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.content import Content, ContentReport, VocabularyExample, VocabularyForm

REPORT_REASONS = ("finnish_sentence", "translation", "word_form", "other")
# Form statuses shown in the app. Reported forms stay visible until they are fixed.
VISIBLE_FORM_STATUSES = ("active", "needs_review", "reviewed")
MAX_NOTE_LENGTH = 1000


class ReportNotFound(LookupError):
    pass


class ReportInvalid(ValueError):
    pass


def create_report(
    session: Session,
    *,
    content_id: UUID,
    reason: str,
    vocabulary_form_id: UUID | None = None,
    example_id: UUID | None = None,
    note: str | None = None,
) -> ContentReport:
    if reason not in REPORT_REASONS:
        raise ReportInvalid(f"Unknown reason '{reason}'.")

    content = session.get(Content, content_id)
    if content is None or content.content_type != "vocabulary_item":
        raise ReportNotFound("Vocabulary item not found.")

    form = None
    if vocabulary_form_id is not None:
        form = session.get(VocabularyForm, vocabulary_form_id)
        if form is None or form.content_id != content_id:
            raise ReportNotFound("Form target not found for this vocabulary item.")

    example = None
    if example_id is not None:
        example = session.get(VocabularyExample, example_id)
        if example is None or example.content_id != content_id:
            raise ReportNotFound("Example not found for this vocabulary item.")

    if reason == "word_form" and form is None:
        raise ReportInvalid("A word-form report needs vocabulary_form_id.")
    if reason in ("finnish_sentence", "translation") and example is None:
        raise ReportInvalid("A sentence or translation report needs example_id.")

    note = (note or "").strip()[:MAX_NOTE_LENGTH] or None
    snapshot: dict[str, str | None] = {"word": content.content}
    if form is not None:
        snapshot.update(
            form=form.form,
            grammatical_label=form.grammatical_label,
            target_type=form.target_type,
        )
    if example is not None:
        snapshot.update(
            finnish_sentence=example.finnish_sentence,
            written_finnish_sentence=example.written_finnish_sentence,
            english_translation=example.english_translation,
        )

    report = ContentReport(
        content_id=content_id,
        vocabulary_form_id=form.id if form is not None else None,
        example_id=example.id if example is not None else None,
        reason=reason,
        note=note,
        snapshot=snapshot,
        status="open",
    )
    session.add(report)
    if reason == "word_form":
        form.review_status = "needs_review"
    elif example is not None:
        example.validation_status = "needs_review"
    session.commit()
    session.refresh(report)
    return report
