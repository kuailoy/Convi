# Backend Database Setup

The backend uses SQLAlchemy models and Alembic migrations to manage the PostgreSQL schema.

## Configure the connection

From this directory, create a local environment file:

```bash
cp .env.example .env
```

Set `DB_HOST`, `DB_NAME`, and `DB_USER` in `.env`. For Microsoft Entra authentication, set `DB_AUTH_MODE=entra`, use the Entra administrator's user principal name for `DB_USER`, and sign in with Azure CLI:

```bash
az login
```

For PostgreSQL password authentication, set `DB_AUTH_MODE=password` and `DB_PASSWORD` instead. Keep `.env` private; it is ignored by Git.

## Install and create the schema

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
alembic upgrade head
```

The first migration creates `contents`, `exercise_sets`, and `content_progress` in the database selected by `DB_NAME`. Review the migration before applying it to any database containing valuable data.

To see the current migration revision:

```bash
alembic current
```

## Generate topic examples through the API

`POST /api/v1/topics/{topic_slug}/examples/generate` calls the existing Finnish
example generator for missing vocabulary-form targets, saves its results, and
returns generation counts plus updated topic coverage. Each request generates
up to 10 targets by default; pass `{"limit": 20}` to generate up to 20. The
limit is capped at 20 so one request stays bounded.

The endpoint requires both `OPENAI_API_KEY` and `GENERATOR_API_KEY` in the
backend environment. Send the latter in the `x-generator-api-key` header. Keep
that key on trusted server-side callers; do not embed it in the Expo app. The
app should call this endpoint only after an appropriate user-authentication
mechanism is in place.

The endpoint returns HTTP 404 for an unknown topic, 401 for a missing or
incorrect generator key, and 503 if generation is not configured. Individual
model-call failures are reported in the successful response's `generation.failures`
count so callers can display the resulting coverage and retry if needed.

## Read vocabulary for the mobile app

`GET /api/v1/vocabulary/topics?language=fi` returns the ordered topic list with
the active vocabulary-item count for that language. Topics with no active
items are included with `word_count: 0`.

`GET /api/v1/vocabulary/topics/{topic_slug}/contents?language=fi` returns one
topic and its active vocabulary items, with reviewed forms nested under each
item and all linked examples nested under each form. Example and target
validation statuses are included in the response for review. A form's
`examples` value is always a list and can contain multiple examples.

The general `GET /api/v1/contents` endpoint remains available for flat content
queries and does not accept a `limit` parameter.
