import os

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL, Engine

load_dotenv()

_POSTGRES_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"


def get_database_url() -> URL:
    """Build the PostgreSQL URL from environment variables."""
    auth_mode = os.getenv("DB_AUTH_MODE", "entra").lower()
    password = os.getenv("DB_PASSWORD") if auth_mode == "password" else None

    return URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=password,
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "convi_dev"),
        query={"sslmode": "require"},
    )


def create_database_engine() -> Engine:
    """Create an engine that supports Entra tokens or PostgreSQL passwords."""
    auth_mode = os.getenv("DB_AUTH_MODE", "entra").lower()
    engine = create_engine(get_database_url(), pool_pre_ping=True)

    if auth_mode == "entra":
        credential = DefaultAzureCredential()

        @event.listens_for(engine, "do_connect")
        def add_entra_token(dialect, connection_record, cargs, cparams):
            token = credential.get_token(_POSTGRES_SCOPE).token
            cparams["password"] = token

    elif auth_mode != "password":
        raise ValueError("DB_AUTH_MODE must be 'entra' or 'password'.")

    if auth_mode == "password" and not os.getenv("DB_PASSWORD"):
        raise ValueError("DB_PASSWORD is required when DB_AUTH_MODE=password.")

    return engine
