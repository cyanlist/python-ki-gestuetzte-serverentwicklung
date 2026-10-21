# 05 GET with query parameters

**Goal:** `GET /pokemon` searches Pokémon, for example
`/pokemon?typ=Feuer&name=ri&legendaer=false&page=0&size=5`, and returns one page.

**Checklist item:** GET requests → "By query parameter".

## Background

- **Path parameter** (`/pokemon/644`): identifies **one** resource.
- **Query parameter** (`/pokemon?typ=Feuer`): filters or controls a **collection**.
  All parameters are optional.
- **Validation:** FastAPI can read all query parameters into one Pydantic model
  (`Annotated[PokemonQuery, Query()]`). The rules (maximum page size, allowed types)
  are then defined in one place.
- **Paging:** Never return all rows. The client sends `page` (starting at 0) and
  `size`. The response contains the content and information about the page
  (`total_elements`, `total_pages`).
- **No result is not an error:** a search without matches returns `200` and an empty
  list. (`404` is for a single resource that does not exist. Some projects, including
  the example of the professor, use `404` here as well. Decide and stay consistent.)

## Steps

### 1. Schemas: extend `src/pokemon/schemas.py`

Change the imports at the top and add the enum `Typ` below them:

```python
"""Pydantic models for requests and responses."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Typ(StrEnum):
    """The types of Pokémon and moves in generation 5."""

    NORMAL = "Normal"
    FEUER = "Feuer"
    WASSER = "Wasser"
    PFLANZE = "Pflanze"
    ELEKTRO = "Elektro"
    EIS = "Eis"
    KAMPF = "Kampf"
    GIFT = "Gift"
    BODEN = "Boden"
    FLUG = "Flug"
    PSYCHO = "Psycho"
    KAEFER = "Käfer"
    GESTEIN = "Gestein"
    GEIST = "Geist"
    DRACHE = "Drache"
    UNLICHT = "Unlicht"
    STAHL = "Stahl"
```

Add at the end of the file:

```python
class PageInfo(BaseModel):
    """Information about the returned page."""

    size: int
    number: int
    total_elements: int
    total_pages: int


class PokemonPage(BaseModel):
    """One page of search results."""

    content: list[PokemonResponse]
    page: PageInfo


class PokemonQuery(BaseModel):
    """Search and paging parameters of `GET /pokemon`."""

    # unknown query parameters lead to 422 instead of being ignored silently
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=50)
    """Part of the name, case-insensitive."""

    typ: Typ | None = None
    """Matches `typ1` or `typ2`."""

    legendaer: bool | None = None
    page: int = Field(default=0, ge=0)
    """Page number, starting at 0."""

    size: int = Field(default=10, ge=1, le=100)
    """Number of Pokémon per page."""
```

`Typ` is a `StrEnum`: the allowed values are the strings, and Pydantic answers `422`
with a list of the valid values for anything else.

### 2. Repository: extend `src/pokemon/repository.py`

Change the import and add the method `find` to the class:

```python
from sqlalchemy import func, or_, select
```

```python
    def find(
        self,
        *,
        name: str | None,
        typ: str | None,
        legendaer: bool | None,
        page: int,
        size: int,
    ) -> tuple[list[Pokemon], int]:
        """Search Pokémon. Return one page and the total number of matches."""
        conditions = []
        if name is not None:
            # autoescape: a "%" or "_" typed by the user is not a wildcard
            conditions.append(Pokemon.name.icontains(name, autoescape=True))
        if typ is not None:
            conditions.append(or_(Pokemon.typ1 == typ, Pokemon.typ2 == typ))
        if legendaer is not None:
            conditions.append(Pokemon.legendaer == legendaer)

        total = self.session.scalar(
            select(func.count()).select_from(Pokemon).where(*conditions)
        )
        statement = (
            select(Pokemon)
            .where(*conditions)
            .options(joinedload(Pokemon.detail), selectinload(Pokemon.attacken))
            .order_by(Pokemon.id)
            .limit(size)
            .offset(page * size)
        )
        return list(self.session.scalars(statement).all()), total or 0
```

- The conditions are collected in a list, so every filter is optional.
- `where()` with no arguments simply has no condition.
- `order_by` is **required** for stable paging. Without an order, the database may
  return the rows in any order, and pages can overlap.
- Never build SQL by concatenating strings with user input (SQL injection). SQLAlchemy
  sends the values as parameters.

### 3. Service: extend `src/pokemon/service.py`

Add the import and the method:

```python
from pokemon.schemas import PokemonQuery
```

```python
    def find(self, query: PokemonQuery) -> tuple[list[Pokemon], int]:
        """Search Pokémon. Return one page and the total number of matches."""
        return self.repository.find(
            name=query.name,
            typ=query.typ,
            legendaer=query.legendaer,
            page=query.page,
            size=query.size,
        )
```

### 4. Router: `src/pokemon/router.py`

Change the imports and add the function **above** `get_by_id`:

```python
from typing import Annotated

from fastapi import APIRouter, Query

from pokemon.dependencies import ServiceDep
from pokemon.schemas import PageInfo, PokemonPage, PokemonQuery, PokemonResponse
```

```python
@router.get("", response_model=PokemonPage)
def get(query: Annotated[PokemonQuery, Query()], service: ServiceDep) -> PokemonPage:
    """Search Pokémon with query parameters, e.g. `?typ=Feuer&page=0&size=5`."""
    pokemon_list, total = service.find(query)
    return PokemonPage(
        content=[PokemonResponse.model_validate(p) for p in pokemon_list],
        page=PageInfo(
            size=query.size,
            number=query.page,
            total_elements=total,
            total_pages=-(-total // query.size),  # ceiling division
        ),
    )
```

`-(-total // query.size)` is a ceiling division without importing `math`:
12 elements with size 10 give 2 pages.

## Check it

Start the server (`uv run pokemon`) and try:

```shell
curl.exe "http://127.0.0.1:8000/pokemon"
curl.exe "http://127.0.0.1:8000/pokemon?typ=Feuer"
curl.exe "http://127.0.0.1:8000/pokemon?name=zo"
curl.exe "http://127.0.0.1:8000/pokemon?legendaer=true&size=2&page=1"
curl.exe "http://127.0.0.1:8000/pokemon?name=does-not-exist"
curl.exe "http://127.0.0.1:8000/pokemon?size=0"
curl.exe "http://127.0.0.1:8000/pokemon?foo=1"
```

Expected with the seed data:

| Request | Expected |
|---|---|
| no parameter | 10 Pokémon, `total_elements` 12, `total_pages` 2 |
| `typ=Feuer` | Victini, Floink, Skelabra, Reshiram |
| `name=zo` | Zorua, Zoroark |
| `legendaer=true&size=2&page=1` | Zekrom, Kyurem |
| `name=does-not-exist` | `200`, `content` is `[]` |
| `size=0` or `foo=1` | `422` |

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| Route `/pokemon` returns `404` or `405` | The path of the new function must be `""` (empty), not `"/"`. With the prefix `/pokemon` the empty string gives `/pokemon`. |
| The filter does nothing | The parameter name in the URL must match the field name exactly (`legendaer`, not `legendary`). |
| `422` for `typ=feuer` | Enum values are case-sensitive. Send `Feuer`. |
| Special characters in a URL | Encode them (`%25` for `%`). `curl.exe` with `-G --data-urlencode "name=%"` does this for you. |
| Duplicate rows or wrong `total_pages` | Do not `joinedload` the 1:N relation (it multiplies the rows). Use `selectinload`, as in the guide. |

## Commit

```shell
git add src
git commit -m "feat(api): add GET with query parameters"
```

## Prompt idea

```text
Context: FastAPI project with layers router, service, repository (see src/pokemon).
Task: Add GET /pokemon with optional query parameters name (contains, case-insensitive),
typ (enum, matches typ1 or typ2), legendaer (bool), page (>=0) and size (1-100).
Read the parameters into a Pydantic model with extra="forbid" via
Annotated[Model, Query()]. The repository returns the page and the total count,
ordered by id. The response is a Pydantic model with "content" and a "page" object.
Comments in English.
```
