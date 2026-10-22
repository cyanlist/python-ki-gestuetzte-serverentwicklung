"""Engine and session factory for SQLAlchemy."""

from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pokemon.config.db import db_log_statements, db_url

__all__ = ["SessionFactory", "engine"]

engine: Final = create_engine(db_url, pool_pre_ping=True, echo=db_log_statements)
"""Engine with a connection pool to PostgreSQL."""

SessionFactory: Final = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)
"""Factory for sessions. One session is used per request."""
