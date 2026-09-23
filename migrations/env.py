"""Alembic environment configured from the canonical FlowLens settings."""

from alembic import context
from sqlalchemy import create_engine, pool

from flowlens.config import get_settings
from flowlens.data import Base
from flowlens.data.models import register_models

register_models()
target_metadata = Base.metadata


def _database_url() -> str:
    return get_settings().database_url.get_secret_value()


def run_migrations_offline() -> None:
    """Run migrations without creating an Engine."""

    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the configured PostgreSQL database."""

    connectable = create_engine(_database_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
