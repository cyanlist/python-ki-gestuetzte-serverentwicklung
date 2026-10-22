"""Base class of all entities."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

__all__ = ["Base"]


class Base(DeclarativeBase):
    """Base class of all entities. All tables live in the schema `pokemon`."""

    metadata = MetaData(schema="pokemon")
