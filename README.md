# Pokémon API

A small REST server for Pokémon of the 5th generation (Unova, Pokédex no. 494-649),
built for the course "KI-gestützte Serverentwicklung" at Hochschule Karlsruhe.

## Tech stack

| Area | Tool |
|---|---|
| Language | Python 3.13+ |
| Project and package manager | [uv](https://docs.astral.sh/uv/) |
| Web framework | FastAPI with Pydantic |
| Database | PostgreSQL 18 (Docker container) |
| ORM | SQLAlchemy |
| Linter and formatter | [ruff](https://docs.astral.sh/ruff/) |
| Type checker | [ty](https://docs.astral.sh/ty/) |
| Tests | pytest |

## Project status

| Step | Status |
|---|---|
| Project skeleton with uv, ruff, ty and pytest | done |
| PostgreSQL container with schema and seed data | done |
| FastAPI server, SQLAlchemy entities, REST endpoints | planned |
| Tests for GET and POST | planned |

The detailed list of requirements is in [CHECKLIST.md](CHECKLIST.md).

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

## Getting started

### 1. Install the dependencies

```shell
uv sync
```

This creates the virtual environment `.venv` and installs all packages from
`pyproject.toml` and `uv.lock`.

### 2. Start the database

```shell
cd extras/compose/postgres
docker compose up -d
docker compose ps
```

On the first start (empty data volume), PostgreSQL runs the scripts in
`extras/compose/postgres/init/` in alphabetical order:

1. `01-schema.sql` creates the schema `pokemon` and its tables.
2. `02-seed.sql` inserts the test data.

Connection details for a DB browser (e.g. DBeaver or pgAdmin):

| Setting | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `pokemon` |
| User and password | see `extras/compose/postgres/compose.yml` |
| Schema | `pokemon` |

Open a SQL shell inside the container:

```shell
docker compose exec postgres psql --username=admin --dbname=pokemon
```

### 3. Reload or stop the database

```shell
# Stop the container, the data is kept
docker compose stop

# Remove container and data, then start again with fresh seed data.
# The init scripts only run when the data volume is empty.
docker compose down -v
docker compose up -d
```

If port 5432 is already in use, change `"5432:5432"` in `compose.yml` to
`"5433:5432"` and connect to port 5433.

> The credentials in `compose.yml` are for local development only.
> Do not reuse them anywhere else.

## Data model

```text
pokemon 1 ──── 1 pokemon_detail
   │
   └────── 1:N  attacke
```

| Table | Relation | Content |
|---|---|---|
| `pokemon` | main table | Pokédex number (primary key), name, types, height, weight, legendary flag, `version` for optimistic locking |
| `pokemon_detail` | 1:1 to `pokemon` | catch rate, base experience |
| `attacke` | 1:N to `pokemon` | name, type, power, accuracy |

The seed data contains a selection of 12 Pokémon of the 5th generation.

## Development

```shell
# Lint and format
uv run ruff check
uv run ruff format

# Type check
uv run ty check

# Tests
uv run pytest
```

Run linter and type checker before every commit.

## Project structure

```text
.
├── extras/
│   └── compose/
│       └── postgres/        # compose.yml and init/ with schema and seed data
├── src/
│   └── pokemon/             # application package
├── tests/                   # tests (to be added)
├── pyproject.toml           # dependencies and tool configuration
└── uv.lock                  # locked dependency versions
```

## Commit convention

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
`type(scope): description`, in English and in the imperative mood.

| Type | Use for |
|---|---|
| `feat` | new functionality |
| `fix` | bug fixes |
| `build` | dependencies and build setup |
| `chore` | configuration and maintenance |
| `docs` | documentation |
| `test` | tests |
| `refactor` | code changes without behavior change |

Examples: `chore: initialize project skeleton with uv`,
`feat(api): add GET endpoint by id`.
