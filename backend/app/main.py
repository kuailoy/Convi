from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database import create_database_engine
from app.models.content import Content


engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()


class ContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    meaning: str | None
    content_type: str
    language_code: str
    practice_mode: str
    practice_method: str
    cefr_level: str | None
    context: str | None
    register: str | None


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
    )

    if mode is not None:
        statement = statement.where(Content.practice_mode == mode)

    if method is not None:
        statement = statement.where(Content.practice_method == method)

    if level is not None:
        statement = statement.where(Content.cefr_level == level)

    statement = statement.order_by(Content.created_at.asc())

    return db.scalars(statement).all()