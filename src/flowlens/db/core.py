"""Lazy SQLAlchemy engine, session, and connectivity infrastructure."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.elements import TextClause

from flowlens.config import Settings

type SessionFactory = sessionmaker[Session]


class DatabaseUnavailableError(RuntimeError):
    """Raised when a database infrastructure check cannot complete."""


def create_database_engine(settings: Settings) -> Engine:
    """Create a pooled SQLAlchemy engine without opening a database connection."""

    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
    )


def create_session_factory(engine: Engine) -> SessionFactory:
    """Create the canonical SQLAlchemy session factory for an engine."""

    return sessionmaker(
        bind=engine,
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )


@contextmanager
def session_scope(session_factory: SessionFactory) -> Iterator[Session]:
    """Provide a session lifecycle suitable for later dependency injection."""

    session = session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database_connectivity(engine: Engine) -> bool:
    """Execute SELECT 1 and return True, or raise a clear infrastructure error."""

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar_one()
    except SQLAlchemyError as exc:
        raise DatabaseUnavailableError("Database connectivity check failed") from exc

    if result != 1:
        raise DatabaseUnavailableError("Database connectivity check returned an invalid result")

    return True


def is_pgvector_available(engine: Engine) -> bool:
    """Return whether the PostgreSQL server makes the vector extension available."""

    statement = text(
        "SELECT EXISTS ("
        "SELECT 1 FROM pg_available_extensions WHERE name = 'vector'"
        ")"
    )
    return _execute_boolean_check(engine, statement)


def is_pgvector_enabled(engine: Engine) -> bool:
    """Return whether the vector extension is enabled in the configured database."""

    statement = text(
        "SELECT EXISTS ("
        "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
        ")"
    )
    return _execute_boolean_check(engine, statement)


def _execute_boolean_check(engine: Engine, statement: TextClause) -> bool:
    try:
        with engine.connect() as connection:
            result = connection.execute(statement).scalar_one()
    except SQLAlchemyError as exc:
        raise DatabaseUnavailableError("Database infrastructure check failed") from exc

    return bool(result)
