from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager, sessionmaker

from app.database import create_database_engine
from app.models.content import Content, VocabularyTopic


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
