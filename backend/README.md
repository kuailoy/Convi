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
