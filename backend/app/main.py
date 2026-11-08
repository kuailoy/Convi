from collections.abc import Generator
from dataclasses import asdict
import hmac
import os
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, contains_eager, sessionmaker

from app.database import create_database_engine
from app.models.content import (
    Content,
    VocabularyExample,
    VocabularyExampleTarget,
    VocabularyForm,
    VocabularyTopic,
)
from app.services.content_generator import generate_missing_topic_examples
from app.services.content_readiness import calculate_topic_readiness


engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()


class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    name_en: str
    name_fi: str
    sort_order: int


class ContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    meaning: str | None
    content_type: str
    language_code: str
    practice_mode: str
    practice_method: str
    topic_order: int | None
    topic: TopicResponse | None
    cefr_level: str | None
    context: str | None
    register_: str | None = Field(default=None, alias="register")


class VocabularyTopicListItem(BaseModel):
    slug: str
    name_en: str
    name_fi: str
    sort_order: int
    word_count: int


class VocabularyExampleResponse(BaseModel):
    id: UUID
    finnish_sentence: str
    written_finnish_sentence: str
    english_translation: str
    difficulty: str
    role: str
    validation_status: str
    target_validation_status: str


class VocabularyFormResponse(BaseModel):
    id: UUID
    form: str
    grammatical_label: str
    target_type: str
    display_order: int
    notes: str | None
    examples: list[VocabularyExampleResponse]


class VocabularyItemResponse(BaseModel):
    id: UUID
    word: str
    meaning: str | None
    language_code: str
    meaning_language_code: str
    topic_order: int
    cefr_level: str | None
    context: str | None
    register_: str | None = Field(default=None, alias="register")
    forms: list[VocabularyFormResponse]


class VocabularyTopicContentsResponse(BaseModel):
    topic: TopicResponse
    vocabulary: list[VocabularyItemResponse]


class GenerateExamplesRequest(BaseModel):
    # Keep each HTTP request bounded; callers can repeat it until coverage is sufficient.
    limit: int = Field(default=10, ge=1, le=20)


class CoverageResponse(BaseModel):
    total: int
    covered: int
    percent: float


class TopicReadinessResponse(BaseModel):
    topic_slug: str
    vocabulary_items: CoverageResponse
    targets_by_type: dict[str, CoverageResponse]
    total_targets: CoverageResponse


class GenerationSummaryResponse(BaseModel):
    topic_slug: str
    targets_found: int
    attempted: int
    inserted: int
    auto_valid: int
    needs_review: int
    rejected: int
    failures: int
    skipped_existing: int


class GenerateExamplesResponse(BaseModel):
    generation: GenerationSummaryResponse
    readiness: TopicReadinessResponse


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/contents", response_model=list[ContentResponse])
def list_contents(
    language: str,
    mode: str | None = None,
    method: str | None = None,
    level: str | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Content).where(
        Content.language_code == language,
        Content.status == "active",
    ).outerjoin(Content.topic).options(contains_eager(Content.topic))

    if mode is not None:
        statement = statement.where(Content.practice_mode == mode)

    if method is not None:
        statement = statement.where(Content.practice_method == method)

    if level is not None:
        statement = statement.where(Content.cefr_level == level)

    statement = statement.order_by(
        VocabularyTopic.sort_order.asc().nulls_last(),
        Content.topic_order.asc().nulls_last(),
        Content.created_at.asc(),
    )

    return db.scalars(statement).all()


@app.get("/api/v1/vocabulary/topics", response_model=list[VocabularyTopicListItem])
def list_vocabulary_topics(
    language: str = Query(default="fi", min_length=2, max_length=10),
    db: Session = Depends(get_db),
):
    word_count = func.count(Content.id).label("word_count")
    rows = db.execute(
        select(VocabularyTopic, word_count)
        .outerjoin(
            Content,
            (Content.topic_id == VocabularyTopic.id)
            & (Content.content_type == "vocabulary_item")
            & (Content.language_code == language)
            & (Content.status == "active"),
        )
        .group_by(VocabularyTopic.id)
        .order_by(VocabularyTopic.sort_order, VocabularyTopic.slug)
    ).all()
    return [
        VocabularyTopicListItem(
            slug=topic.slug,
            name_en=topic.name_en,
            name_fi=topic.name_fi,
            sort_order=topic.sort_order,
            word_count=count,
        )
        for topic, count in rows
    ]


@app.get(
    "/api/v1/vocabulary/topics/{topic_slug}/contents",
    response_model=VocabularyTopicContentsResponse,
)
def get_vocabulary_topic_contents(
    topic_slug: str,
    language: str = Query(default="fi", min_length=2, max_length=10),
    db: Session = Depends(get_db),
):
    topic = db.scalar(select(VocabularyTopic).where(VocabularyTopic.slug == topic_slug))
    if topic is None:
        raise HTTPException(status_code=404, detail="Vocabulary topic not found.")

    vocabulary_items = db.scalars(
        select(Content)
        .where(
            Content.topic_id == topic.id,
            Content.content_type == "vocabulary_item",
            Content.language_code == language,
            Content.status == "active",
        )
        .order_by(Content.topic_order, Content.id)
    ).all()
    content_ids = [item.id for item in vocabulary_items]

    forms_by_content: dict[UUID, list[VocabularyFormResponse]] = {
        content_id: [] for content_id in content_ids
    }
    if content_ids:
        form_rows = db.execute(
            select(VocabularyForm)
            .where(
                VocabularyForm.content_id.in_(content_ids),
                VocabularyForm.review_status == "reviewed",
            )
            .order_by(VocabularyForm.content_id, VocabularyForm.display_order, VocabularyForm.id)
        ).scalars().all()
        form_ids = [form.id for form in form_rows]
        examples_by_form: dict[UUID, list[VocabularyExampleResponse]] = {
            form_id: [] for form_id in form_ids
        }
        if form_ids:
            example_rows = db.execute(
                select(VocabularyExampleTarget, VocabularyExample)
                .join(VocabularyExample, VocabularyExample.id == VocabularyExampleTarget.example_id)
                .where(
                    VocabularyExampleTarget.vocabulary_form_id.in_(form_ids),
                )
                .order_by(
                    VocabularyExampleTarget.vocabulary_form_id,
                    VocabularyExample.created_at,
                    VocabularyExample.id,
                )
            ).all()
            for target, example in example_rows:
                examples_by_form[target.vocabulary_form_id].append(
                    VocabularyExampleResponse(
                        id=example.id,
                        finnish_sentence=example.finnish_sentence,
                        written_finnish_sentence=example.written_finnish_sentence,
                        english_translation=example.english_translation,
                        difficulty=example.difficulty,
                        role=target.role,
                        validation_status=example.validation_status,
                        target_validation_status=target.target_validation_status,
                    )
                )

        for form in form_rows:
            forms_by_content[form.content_id].append(
                VocabularyFormResponse(
                    id=form.id,
                    form=form.form,
                    grammatical_label=form.grammatical_label,
                    target_type=form.target_type,
                    display_order=form.display_order,
                    notes=form.notes,
                    examples=examples_by_form[form.id],
                )
            )

    return VocabularyTopicContentsResponse(
        topic=TopicResponse.model_validate(topic),
        vocabulary=[
            VocabularyItemResponse(
                id=item.id,
                word=item.content,
                meaning=item.meaning,
                language_code=item.language_code,
                meaning_language_code=item.meaning_language_code,
                topic_order=item.topic_order,
                cefr_level=item.cefr_level,
                context=item.context,
                register_=item.register,
                forms=forms_by_content[item.id],
            )
            for item in vocabulary_items
        ],
    )


@app.post(
    "/api/v1/topics/{topic_slug}/examples/generate",
    response_model=GenerateExamplesResponse,
)
def generate_topic_examples(
    topic_slug: str,
    request: GenerateExamplesRequest,
    db: Session = Depends(get_db),
    x_generator_api_key: str | None = Header(default=None),
):
    """Generate and save a bounded batch of missing Finnish examples for a topic."""
    expected_api_key = os.getenv("GENERATOR_API_KEY")
    if not expected_api_key:
        raise HTTPException(
            status_code=503,
            detail="Topic example generation is not configured on this server.",
        )
    if x_generator_api_key is None or not hmac.compare_digest(
        x_generator_api_key, expected_api_key
    ):
        raise HTTPException(status_code=401, detail="Invalid generator API key.")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OpenAI API is not configured on this server.",
        )

    if db.scalar(select(VocabularyTopic.id).where(VocabularyTopic.slug == topic_slug)) is None:
        raise HTTPException(status_code=404, detail="Vocabulary topic not found.")

    try:
        summary = generate_missing_topic_examples(
            SessionLocal,
            topic_slug=topic_slug,
            limit=request.limit,
        )
        readiness = calculate_topic_readiness(db, topic_slug)
    except ValueError as error:
        # The generator can also report a missing topic if it is removed concurrently.
        raise HTTPException(status_code=404, detail="Vocabulary topic not found.") from error

    def coverage_payload(coverage):
        return {
            "total": coverage.total,
            "covered": coverage.covered,
            "percent": coverage.percent,
        }

    return {
        "generation": asdict(summary),
        "readiness": {
            "topic_slug": readiness.topic_slug,
            "vocabulary_items": coverage_payload(readiness.vocabulary_items),
            "targets_by_type": {
                target_type: coverage_payload(coverage)
                for target_type, coverage in readiness.targets_by_type.items()
            },
            "total_targets": coverage_payload(readiness.total_targets),
        },
    }
