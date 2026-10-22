"""Database settings from the TOML file and the SQLAlchemy URL."""

from typing import Final

from sqlalchemy.engine import URL

from pokemon.config.config import app_config

__all__ = ["db_log_statements", "db_url"]

_db_toml: Final = app_config.get("db", {})

_host: Final[str] = _db_toml.get("host", "localhost")
_port: Final[int] = _db_toml.get("port", 5432)
_dbname: Final[str] = _db_toml.get("name", "pokemon")
_username: Final[str] = _db_toml.get("username", "admin")
_password: Final[str] = _db_toml.get("password", "Change Me!")

db_log_statements: Final[bool] = bool(_db_toml.get("log-statements", False))
"""True, if SQLAlchemy should print the generated SQL statements."""

db_url: Final[URL] = URL.create(
    drivername="postgresql+psycopg",
    username=_username,
    password=_password,
    host=_host,
    port=_port,
    database=_dbname,
)
"""URL of the database for SQLAlchemy."""
