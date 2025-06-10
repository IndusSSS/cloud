
# File: backend/alembic/env.py

import os
import sys
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

# —————————————————————————————————————————————
# 1. Make sure Alembic can import your app package
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

# 2. Import your Base metadata from models.py
from app.models import Base  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values in alembic.ini
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# —————————————————————————————————————————————
# 3. Set target_metadata for ‘autogenerate’
target_metadata = Base.metadata

# 4. Override sqlalchemy.url from env var so you don’t hard-code it
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://ssc:ChangeMeToAStrongPass!@localhost:5432/sensordb"
)
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Actually run migrations with the given connection."""
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode with AsyncEngine."""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
