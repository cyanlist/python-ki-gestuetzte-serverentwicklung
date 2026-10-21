# 02 Configuration and database connection

**Goal:** The app reads its database settings from a `.env` file and can open a
connection to the PostgreSQL container.

**Checklist item:** App server → "Database access with SQLAlchemy" (first part).

## Background

- **Settings outside the code.** Host, port and password change between machines and
  must not be committed. They live in a `.env` file, which `.gitignore` already
  ignores. A `.env.example` without the real password **is** committed, so others
  see which variables exist.
- **pydantic-settings** reads environment variables and the `.env` file and validates
  them. A missing password stops the app at startup with a clear error.
- **SQLAlchemy** is the object-relational mapper. The **engine** manages a pool of
  database connections. A **session** is a unit of work on one connection. You create
  one session per request.
- **psycopg 3** is the driver that talks to PostgreSQL. The URL prefix
  `postgresql+psycopg://` selects it.

## Steps

### 1. Start the database

```shell
cd extras/compose/postgres
docker compose up -d
docker compose ps
cd ../../..
```

Wait until the status is `healthy`.

### 2. Install the packages

```shell
uv add sqlalchemy "psycopg[binary]" pydantic-settings
```

### 3. Create `.env` and `.env.example`

`.env.example` (committed):

```text
# Copy this file to .env and adjust the values. The real .env is not committed.
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pokemon
DB_USER=admin
DB_PASSWORD=change-me
```

`.env` (not committed): the same lines with the real values from
`extras/compose/postgres/compose.yml`. The password is the value of
`POSTGRES_PASSWORD` there.

Check that Git ignores `.env`:

```shell
git status --short
```

`.env.example` must show up as a new file, `.env` must not.

### 4. Settings: `src/pokemon/config.py`

```python
"""Application settings, read from environment variables or from a `.env` file."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    """Settings of the application.

    Every field can be set as an environment variable in upper case, e.g. `DB_HOST`.
    A `.env` file in the working directory is read as well.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "pokemon"
    db_user: str = "admin"
    # No default: the password must come from the environment or from `.env`
    db_password: SecretStr

    @property
    def database_url(self) -> URL:
        """Build the SQLAlchemy URL for PostgreSQL with psycopg."""
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


@lru_cache
def get_settings() -> Settings:
    """Return the settings. The object is created once and then reused."""
    return Settings()
```

Notes:

- `SecretStr` hides the password when the object is printed or logged.
- `URL.create` escapes special characters in the password. Building the URL with an
  f-string would break for passwords with `@` or `/`.
- `@lru_cache` makes `get_settings()` return the same object every time.

### 5. Engine and session factory: `src/pokemon/database.py`

```python
"""Database engine and session factory."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pokemon.config import get_settings

engine = create_engine(get_settings().database_url, pool_pre_ping=True)
"""Engine with a connection pool to PostgreSQL."""

SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)
"""Factory for sessions. One session is used per request."""
```

- `pool_pre_ping=True` tests a connection before it is used. This avoids errors after
  the database restarted.
- `expire_on_commit=False` keeps the loaded objects usable after `commit()`. Without
  it, every attribute access after a commit would trigger a new query.

## Check it

The schema `pokemon` is set in the entities (guide 03). For now, check the connection
with a one-line query:

```shell
uv run python -c "from sqlalchemy import text; from pokemon.database import engine; print(engine.connect().execute(text('select count(*) from pokemon.pokemon')).scalar_one())"
```

Expected output: `12` (the seed data). Then run:

```shell
uv run ruff format
uv run ruff check
uv run ty check
```

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| `ValidationError ... db_password Field required` | `.env` is missing or not in the folder where you start the app. Start from the project root. |
| `connection refused` | The container does not run. `docker compose ps` in `extras/compose/postgres`. Docker Desktop must be started. |
| `password authentication failed` | The password in `.env` differs from `POSTGRES_PASSWORD` in `compose.yml`. The password is only set on the first start. After a change run `docker compose down -v` and `docker compose up -d`. |
| `relation "pokemon.pokemon" does not exist` | The init scripts did not run (the volume was not empty). `docker compose down -v` and `docker compose up -d` in `extras/compose/postgres`. |
| `ModuleNotFoundError: psycopg` | `uv add "psycopg[binary]"`. The quotes are needed in PowerShell. |
| Port 5432 is taken | Another PostgreSQL runs on your machine. Change the published port in `compose.yml` (for example `"5433:5432"`) and set `DB_PORT=5433`. |

## Commit

```shell
git add pyproject.toml uv.lock .env.example src
git commit -m "feat(db): add settings and database connection"
```

Do not add `.env`. Check with `git status` before you commit.

## Prompt idea

```text
Context: FastAPI project, SQLAlchemy 2, psycopg 3, PostgreSQL in Docker (see
extras/compose/postgres/compose.yml), package "pokemon" in src/.
Task: Add src/pokemon/config.py with a pydantic-settings class that reads DB_HOST,
DB_PORT, DB_NAME, DB_USER and DB_PASSWORD from .env (password as SecretStr, no
default) and builds a SQLAlchemy URL. Add src/pokemon/database.py with the engine and
a sessionmaker (expire_on_commit=False). Add .env.example. Comments in English.
```
