"""Generate, validate, and persist missing vocabulary examples for a topic."""

from dataclasses import dataclass
from openai import OpenAIError
from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.models import (
    Content,
    VocabularyExample,
    VocabularyExampleTarget,
    VocabularyForm,
    VocabularyTopic,
)
from app.services.content_validator import validate_example
from app.services.sentence_generator import DEFAULT_MODEL, PROMPT_VERSION, generate_example


@dataclass(frozen=True)
class GenerationSummary:
    topic_slug: str
    targets_found: int
    attempted: int
    inserted: int
    auto_valid: int
    needs_review: int
    rejected: int
    failures: int
    skipped_existing: int


def generate_missing_topic_examples(
    session_factory: sessionmaker[Session],
    topic_slug: str,
    limit: int | None = None,
    model: str = DEFAULT_MODEL,
) -> GenerationSummary:
    with session_factory() as session:
        topic = session.scalar(select(VocabularyTopic).where(VocabularyTopic.slug == topic_slug))
        if topic is None:
            raise ValueError(f"Unknown vocabulary topic: {topic_slug}")

        already_has_actionable_example = exists(
            select(VocabularyExampleTarget.example_id)
            .join(VocabularyExample, VocabularyExample.id == VocabularyExampleTarget.example_id)
            .where(
                VocabularyExampleTarget.vocabulary_form_id == VocabularyForm.id,
                VocabularyExampleTarget.role == "primary",
                VocabularyExampleTarget.target_validation_status.in_(
                    ("auto_valid", "human_approved", "needs_review")
                ),
                VocabularyExample.validation_status.in_(("auto_valid", "human_approved", "needs_review")),
            )
        )
        target_rows = session.execute(
            select(
                Content.id,
                VocabularyForm.id,
                Content.content.label("lemma"),
                VocabularyForm.form,
                VocabularyForm.grammatical_label,
                VocabularyForm.target_type,
                VocabularyForm.notes,
            )
            .join(VocabularyForm, VocabularyForm.content_id == Content.id)
            .where(
                Content.topic_id == topic.id,
                Content.content_type == "vocabulary_item",
                VocabularyForm.review_status == "reviewed",
                ~already_has_actionable_example,
            )
            .order_by(Content.topic_order, VocabularyForm.display_order, VocabularyForm.id)
        ).all()
        total_target_count = len(
            session.scalars(
                select(VocabularyForm.id)
                .join(Content, Content.id == VocabularyForm.content_id)
                .where(
                    Content.topic_id == topic.id,
                    Content.content_type == "vocabulary_item",
                    VocabularyForm.review_status == "reviewed",
                )
            ).all()
        )

    targets_found = len(target_rows)
    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        target_rows = target_rows[:limit]

    inserted = auto_valid = needs_review = rejected = failures = 0
    for content_id, form_id, lemma, form, label, target_type, notes in target_rows:
        target = {
            "lemma": lemma,
            "form": form,
            "grammatical_label": label,
            "target_type": target_type,
            "notes": notes,
        }
        try:
            candidate = generate_example(target, model=model)
        except (OpenAIError, KeyError, TypeError, ValueError) as error:
            failures += 1
            print(f"Generation failed for {lemma} / {label}: {error.__class__.__name__}")
            continue

        status, validation_notes, normalized = validate_example(target, candidate)
        try:
            with session_factory() as session, session.begin():
                # Recheck before writing so retries and concurrent requests do not link stale targets.
                target_exists = session.scalar(
                    select(VocabularyForm.id).where(VocabularyForm.id == form_id)
                )
                if target_exists is None:
                    failures += 1
                    continue
                example = session.scalar(
                    select(VocabularyExample).where(
                        VocabularyExample.content_id == content_id,
                        VocabularyExample.normalized_sentence == normalized,
                    )
                )
                if example is None:
                    example = VocabularyExample(
                        content_id=content_id,
                        finnish_sentence=candidate["finnish_sentence"],
                        normalized_sentence=normalized,
                        english_translation=candidate["english_translation"],
                        difficulty=candidate["difficulty"],
                        validation_status="rejected" if status == "rejected" else "auto_valid",
                        validation_notes=(
                            validation_notes if status == "rejected" else None
                        ),
                        generation_model=model,
                        prompt_version=PROMPT_VERSION,
                    )
                    session.add(example)
                    session.flush()
                    inserted += 1
                else:
                    # Identical sentence may intentionally reinforce several target forms.
                    pass
                linked = session.get(VocabularyExampleTarget, (example.id, form_id))
                if linked is None:
                    session.add(
                        VocabularyExampleTarget(
                            example_id=example.id,
                            vocabulary_form_id=form_id,
                            role="primary",
                            target_validation_status=status,
                            target_validation_notes=validation_notes,
                        )
                    )
                    if status in {"auto_valid", "needs_review", "human_approved"} and example.validation_status == "rejected":
                        example.validation_status = "auto_valid"
                        example.validation_notes = None
                else:
                    linked.target_validation_status = status
                    linked.target_validation_notes = validation_notes
            if status == "auto_valid":
                auto_valid += 1
            elif status == "needs_review":
                needs_review += 1
            else:
                rejected += 1
        except IntegrityError:
            # The normalized-sentence uniqueness constraint safely absorbs a concurrent duplicate.
            failures += 1
            continue

    return GenerationSummary(
        topic_slug=topic_slug,
        targets_found=targets_found,
        attempted=len(target_rows),
        inserted=inserted,
        auto_valid=auto_valid,
        needs_review=needs_review,
        rejected=rejected,
        failures=failures,
        skipped_existing=total_target_count - targets_found,
    )
