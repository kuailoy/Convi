"""Coverage and readiness calculations for vocabulary topics."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Content,
    VocabularyExample,
    VocabularyExampleTarget,
    VocabularyForm,
    VocabularyTopic,
)


VALID_EXAMPLE_STATUSES = ("auto_valid", "human_approved")
COVERAGE_TYPES = ("inflected_form", "related_form", "invariant", "governed_pattern")


@dataclass(frozen=True)
class Coverage:
    total: int
    covered: int

    @property
    def percent(self) -> float:
        return round((self.covered / self.total) * 100, 1) if self.total else 0.0


@dataclass(frozen=True)
class TopicReadiness:
    topic_slug: str
    vocabulary_items: Coverage
    targets_by_type: dict[str, Coverage]
    total_targets: Coverage


def calculate_topic_readiness(session: Session, topic_slug: str) -> TopicReadiness:
    topic = session.scalar(select(VocabularyTopic).where(VocabularyTopic.slug == topic_slug))
    if topic is None:
        raise ValueError(f"Unknown vocabulary topic: {topic_slug}")

    rows = session.execute(
        select(
            Content.id,
            VocabularyForm.id,
            VocabularyForm.target_type,
            func.count(VocabularyExample.id).label("valid_examples"),
        )
        .join(VocabularyForm, VocabularyForm.content_id == Content.id)
        .outerjoin(
            VocabularyExampleTarget,
            (VocabularyExampleTarget.vocabulary_form_id == VocabularyForm.id)
            & (VocabularyExampleTarget.role == "primary")
            & (VocabularyExampleTarget.target_validation_status.in_(VALID_EXAMPLE_STATUSES)),
        )
        .outerjoin(
            VocabularyExample,
            (VocabularyExample.id == VocabularyExampleTarget.example_id)
            & (VocabularyExample.validation_status.in_(VALID_EXAMPLE_STATUSES)),
        )
        .where(Content.topic_id == topic.id, Content.content_type == "vocabulary_item")
        .group_by(Content.id, VocabularyForm.id, VocabularyForm.target_type)
    ).all()

    # Use distinct example counts because an outer join can retain a target with no valid example.
    totals = {target_type: 0 for target_type in COVERAGE_TYPES}
    covered = {target_type: 0 for target_type in COVERAGE_TYPES}
    covered_content_ids: set[UUID] = set()
    for content_id, _form_id, target_type, valid_examples in rows:
        totals[target_type] += 1
        if valid_examples:
            covered[target_type] += 1
            covered_content_ids.add(content_id)

    vocabulary_total = session.scalar(
        select(func.count(Content.id)).where(
            Content.topic_id == topic.id,
            Content.content_type == "vocabulary_item",
        )
    ) or 0
    target_total = sum(totals.values())
    target_covered = sum(covered.values())
    return TopicReadiness(
        topic_slug=topic_slug,
        vocabulary_items=Coverage(total=vocabulary_total, covered=len(covered_content_ids)),
        targets_by_type={
            kind: Coverage(total=totals[kind], covered=covered[kind]) for kind in COVERAGE_TYPES
        },
        total_targets=Coverage(total=target_total, covered=target_covered),
    )
