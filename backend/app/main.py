from collections.abc import Generator
from dataclasses import asdict
import hmac
import os
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager, sessionmaker

from app.database import create_database_engine
from app.models.content import Content, VocabularyTopic
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
