# 04 Layers, dependency injection and the first endpoint

**Goal:** `GET /pokemon/{id}` returns a Pokémon with its detail and moves as JSON.
The request goes through router, service and repository, which are connected with
dependency injection.

**Checklist items:**

- Layered structure with dependency injection (`Depends`) for service and repository
- Pydantic models for responses
- GET by path parameter, `404` for an unknown id
- Access only through a repository class

## Background

### The layers

```text
HTTP request
    │
    ▼
router.py        HTTP only: parameters, status codes, headers
    │ calls
    ▼
service.py       business rules: "does it exist?", "is the name free?"
    │ calls
    ▼
repository.py    SQL only: select, insert, commit
    │ uses
    ▼
entity.py        the SQLAlchemy classes
```

Why separate them? You can read, test and change each part alone. The service does not
know HTTP (it raises `NotFoundError`, not an HTTP `404`). The router does not know SQL.

### Dependency injection (DI)

DI means: a function **declares** what it needs, and the framework **provides** it.

```python
def get_by_id(pokemon_id: int, service: ServiceDep) -> PokemonResponse: ...
```

The router does not create a `PokemonService`. FastAPI calls `get_service`, which needs
a repository, which needs a session. For one request FastAPI builds the whole chain
once and shares the objects. After the response the session is closed, because
`get_session` uses `yield`:

```text
get_session ──▶ get_repository ──▶ get_service ──▶ router function
 (opens/closes   (gets session)     (gets repo)
  the session)
```

The benefit: in tests you can replace one link, for example with a fake repository.

### Pydantic response models

An entity is a database object. The response model describes what the client
**receives**. It hides internal fields (for example `version`, `aktualisiert`) and
makes the OpenAPI documentation precise. `from_attributes=True` lets Pydantic read the
values directly from an entity.

### Loading the relations

`Pokemon.detail` and `Pokemon.attacken` are loaded lazily by default: each access is
another query. For a list of 10 Pokémon that would be 21 queries (the "N+1 problem").
The repository loads them together with the Pokémon:

- `joinedload(Pokemon.detail)`: one `JOIN` (fine for 1:1)
- `selectinload(Pokemon.attacken)`: one extra `SELECT ... WHERE pokemon_id IN (...)`
  (better than a `JOIN` for 1:N, because the result rows are not multiplied)

## Steps

Do the steps one by one. The commits are listed at the end of the guide.

### 1. Exceptions: `src/pokemon/exceptions.py`

```python
"""Exceptions of the business logic. The app turns them into HTTP responses."""


class NotFoundError(Exception):
    """No Pokémon exists for the requested id."""

    def __init__(self, pokemon_id: int) -> None:
        """Remember the id that was not found."""
        super().__init__(f"No Pokémon with id {pokemon_id}")
        self.pokemon_id = pokemon_id
```

### 2. Response models: `src/pokemon/schemas.py`

```python
"""Pydantic models for requests and responses."""

from pydantic import BaseModel, ConfigDict


class AttackeResponse(BaseModel):
    """A move of a Pokémon."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    typ: str
    staerke: int | None
    genauigkeit: int | None


class DetailResponse(BaseModel):
    """The details of a Pokémon (1:1)."""

    model_config = ConfigDict(from_attributes=True)

    fangrate: int
    basis_erfahrung: int


class PokemonResponse(BaseModel):
    """A Pokémon including its details and moves."""

    # from_attributes: build the model directly from an SQLAlchemy entity
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    typ1: str
    typ2: str | None
    groesse_m: float
    gewicht_kg: float
    legendaer: bool
    detail: DetailResponse | None
    attacken: list[AttackeResponse]
```

### 3. Repository: `src/pokemon/repository.py`

```python
"""Database access for Pokémon. Only this layer knows SQLAlchemy queries."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from pokemon.entity import Pokemon


class PokemonRepository:
    """Reads and writes Pokémon with a session."""

    def __init__(self, session: Session) -> None:
        """Use the given session for all queries."""
        self.session = session

    def find_by_id(self, pokemon_id: int) -> Pokemon | None:
        """Find a Pokémon with its detail and moves, or return None."""
        statement = (
            select(Pokemon)
            .where(Pokemon.id == pokemon_id)
            # one extra query for the 1:N relation, a JOIN for the 1:1 relation
            .options(joinedload(Pokemon.detail), selectinload(Pokemon.attacken))
        )
        return self.session.scalars(statement).one_or_none()
```

### 4. Service: `src/pokemon/service.py`

```python
"""Business logic. It does not know HTTP and does not write SQL."""

from pokemon.entity import Pokemon
from pokemon.exceptions import NotFoundError
from pokemon.repository import PokemonRepository


class PokemonService:
    """Business logic for Pokémon."""

    def __init__(self, repository: PokemonRepository) -> None:
        """Use the given repository for database access."""
        self.repository = repository

    def find_by_id(self, pokemon_id: int) -> Pokemon:
        """Return the Pokémon with the given id.

        Raises:
            NotFoundError: if no Pokémon has this id.
        """
        pokemon = self.repository.find_by_id(pokemon_id)
        if pokemon is None:
            raise NotFoundError(pokemon_id)
        return pokemon
```

### 5. Factory functions for DI: `src/pokemon/dependencies.py`

```python
"""Factory functions for dependency injection with `Depends`."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from pokemon.database import SessionFactory
from pokemon.repository import PokemonRepository
from pokemon.service import PokemonService


def get_session() -> Iterator[Session]:
    """Open a session for the request and close it afterwards."""
    with SessionFactory() as session:
        yield session


def get_repository(
    session: Annotated[Session, Depends(get_session)],
) -> PokemonRepository:
    """Create the repository for the request's session."""
    return PokemonRepository(session)


def get_service(
    repository: Annotated[PokemonRepository, Depends(get_repository)],
) -> PokemonService:
    """Create the service for the request."""
    return PokemonService(repository)


ServiceDep = Annotated[PokemonService, Depends(get_service)]
"""Short form for a service parameter: `service: ServiceDep`."""
```

### 6. Router: `src/pokemon/router.py`

```python
"""REST endpoints for Pokémon."""

from fastapi import APIRouter

from pokemon.dependencies import ServiceDep
from pokemon.schemas import PokemonResponse

router = APIRouter(prefix="/pokemon", tags=["Pokémon"])


@router.get("/{pokemon_id}", response_model=PokemonResponse)
def get_by_id(pokemon_id: int, service: ServiceDep) -> PokemonResponse:
    """Find a Pokémon by its Pokédex number."""
    pokemon = service.find_by_id(pokemon_id)
    return PokemonResponse.model_validate(pokemon)
```

`prefix="/pokemon"` is added to every path of this router. `pokemon_id: int` is a
**path parameter**: FastAPI converts it and answers `422` if it is not a number.

### 7. Connect everything in `src/pokemon/app.py`

```python
"""FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from pokemon.exceptions import NotFoundError
from pokemon.router import router

app = FastAPI(title="Pokémon API")
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    """Return a greeting to check that the server runs."""
    return {"message": "Hello from pokemon!"}


@app.exception_handler(NotFoundError)
def handle_not_found(_request: Request, error: NotFoundError) -> JSONResponse:
    """Turn a NotFoundError into the status code 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(error)},
    )
```

The exception handler is the glue between the layers: the service raises
`NotFoundError`, and the app turns it into HTTP `404`.

## Check it

```shell
uv run pokemon
```

In a second terminal (`curl.exe`, not `curl`, because `curl` is an alias in PowerShell):

```shell
curl.exe -i http://127.0.0.1:8000/pokemon/644
curl.exe -i http://127.0.0.1:8000/pokemon/999999
curl.exe -i http://127.0.0.1:8000/pokemon/abc
```

| Request | Expected |
|---|---|
| `/pokemon/644` | `200` with Zekrom, its `detail` and two entries in `attacken` |
| `/pokemon/999999` | `404` and `{"detail":"No Pokémon with id 999999"}` |
| `/pokemon/abc` | `422` |

You can also try it in the browser at <http://127.0.0.1:8000/docs> with "Try it out".

Then run:

```shell
uv run ruff format
uv run ruff check
uv run ty check
```

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| `ResponseValidationError` | A field in the response model has no matching attribute on the entity, or `from_attributes=True` is missing. |
| `DetachedInstanceError` | A relation was read after the session was closed. Load it in the query (`selectinload`, `joinedload`). |
| `404` for an id you know | The database was reset or the id is not one of the seed data. Check with `docker compose exec postgres psql --username=admin --dbname=pokemon -c "select id, name from pokemon.pokemon"`. |
| Circular import | `service` imports `repository`, `dependencies` imports `service`. If a lower layer imports from a higher one, restructure. |
| Server shows old behaviour | With `reload=True` it restarts on save. If you edited a file outside `src`, restart manually. |

## Commits

```shell
# after step 1 to 4
git add src
git commit -m "feat(api): add repository and service for Pokémon"

# after step 5
git add src
git commit -m "feat(api): add dependency injection for session, repository and service"

# after step 6 and 7
git add src
git commit -m "feat(api): add GET by id with Pydantic response model"
```

If you wrote everything first and want smaller commits afterwards, use
`git add -p` to stage parts of a file.

## Prompt idea

```text
Context: FastAPI project, SQLAlchemy 2 entities in src/pokemon/entity.py (Pokemon with
detail 1:1 and attacken 1:N), sessionmaker in src/pokemon/database.py.
Task: Add the layers exceptions.py, schemas.py (Pydantic response models with
from_attributes), repository.py (find_by_id with joinedload for detail and
selectinload for attacken), service.py (raises NotFoundError), dependencies.py
(get_session with yield, get_repository, get_service, Annotated alias ServiceDep),
router.py (GET /pokemon/{pokemon_id}) and an exception handler in app.py that turns
NotFoundError into 404. Sync def functions, type hints, comments in English.
```
