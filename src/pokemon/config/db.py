"""Database settings from the TOML file and the SQLAlchemy URL."""

import os
from typing import Final

from sqlalchemy.engine import URL

from pokemon.config.config import app_config

__all__ = ["db_log_statements", "db_url"]

_db_toml: Final = app_config.get("db", {})

# Environment variables override the TOML file. The TOML defaults target local
# development (`localhost`); the Docker image sets DB_HOST=postgres instead,
# since "localhost" inside a container means the container itself.
_host: Final[str] = os.environ.get("DB_HOST", _db_toml.get("host", "localhost"))
_port: Final[int] = int(os.environ.get("DB_PORT", _db_toml.get("port", 5432)))
_dbname: Final[str] = os.environ.get("DB_NAME", _db_toml.get("name", "pokemon"))
_username: Final[str] = os.environ.get("DB_USER", _db_toml.get("username", "admin"))
_password: Final[str] = os.environ.get(
    "DB_PASSWORD", _db_toml.get("password", "Change Me!")
)

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
