# 07 POST with validation

**Goal:** `POST /pokemon` creates a new Pokémon with its detail and moves. Invalid
data is rejected with `422`, duplicates with `409`. Success is `201 Created` with a
`Location` header.

**Checklist item:** POST request → "Validation with Pydantic, `422` for invalid data"
and "`201 Created` with a `Location` header".

## Background

### Validation with Pydantic

The request body is described by a Pydantic model. FastAPI parses the JSON, checks it
and calls your function **only if everything is valid**. Otherwise it answers `422`
with a list of the errors. You write no `if` for this, you declare the rules:

| Rule | Example |
|---|---|
| number range | `Field(ge=494, le=649)` for the Pokédex number of generation 5 |
| text length | `Field(min_length=1, max_length=50)` |
| allowed values | `Typ` enum |
| positive numbers | `Field(gt=0)` |
| nested objects | `detail: DetailCreate`, `attacken: list[AttackeCreate]` |
| unknown fields | `ConfigDict(extra="forbid")` rejects typos in field names |

Keep the rules in line with the database. For example `groesse_m` is limited to
`99.9` because the column is `NUMERIC(4, 1)`. A value that the database cannot store
should be a `422`, not a `500`.

### Status codes

| Situation | Code |
|---|---|
| created | `201 Created`, header `Location` with the URL of the new resource |
| invalid data | `422 Unprocessable Content` (automatic) |
| id or name already exists | `409 Conflict` |

The response of `POST` has no body here. The client follows the `Location` header
to read the resource. (The example of the professor does the same.)

### Two checks for duplicates

The service first asks the database ("does this id exist?") to give a clear error
message. Two requests at the same time can still both pass this check. The database
constraints (`PRIMARY KEY`, `UNIQUE`) catch this, and the service turns the resulting
`IntegrityError` into the same `409`. A check **and** a constraint is the safe
combination.

### Who commits?

The repository owns the session, so it also offers `commit()` and `rollback()`. The
service decides **when** to commit, because only the service knows what belongs to one
business operation.

## Steps

### 1. Exception: extend `src/pokemon/exceptions.py`

```python
class ConflictError(Exception):
    """The request conflicts with existing data, e.g. a duplicate id or name."""
```

### 2. Request models: extend `src/pokemon/schemas.py`

Add these classes **above** `PageInfo`:

```python
class AttackeCreate(BaseModel):
    """A move in the request body of POST."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=50)
    typ: Typ
    staerke: int | None = Field(default=None, gt=0)
    genauigkeit: int | None = Field(default=None, ge=1, le=100)


class DetailCreate(BaseModel):
    """The details in the request body of POST."""

    model_config = ConfigDict(extra="forbid")

    fangrate: int = Field(ge=1, le=255)
    basis_erfahrung: int = Field(gt=0)


class PokemonBase(BaseModel):
    """Fields that POST and PUT have in common."""

    # extra="forbid": a typo in a field name leads to 422 instead of being ignored
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=50)
    typ1: Typ
    typ2: Typ | None = None
    groesse_m: float = Field(gt=0, le=99.9)
    gewicht_kg: float = Field(gt=0, le=9999.9)
    legendaer: bool


class PokemonCreate(PokemonBase):
    """Request body of POST: a new Pokémon with its detail and moves."""

    id: int = Field(ge=494, le=649)
    """The Pokédex number. Generation 5 covers the numbers 494 to 649."""

    detail: DetailCreate
    attacken: list[AttackeCreate] = Field(default_factory=list, max_length=4)
```

`PokemonBase` exists because PUT (guide 08) uses the same fields without `id`, `detail`
and `attacken`.

### 3. Repository: extend `src/pokemon/repository.py`

Add the methods to the class:

```python
    def exists_by_id(self, pokemon_id: int) -> bool:
        """Check whether a Pokémon with this id exists."""
        statement = (
            select(func.count()).select_from(Pokemon).where(Pokemon.id == pokemon_id)
        )
        return bool(self.session.scalar(statement))

    def exists_by_name(self, name: str) -> bool:
        """Check whether a Pokémon with this name exists."""
        statement = (
            select(func.count()).select_from(Pokemon).where(Pokemon.name == name)
        )
        return bool(self.session.scalar(statement))

    def add(self, pokemon: Pokemon) -> None:
        """Mark a new Pokémon (with its detail and moves) for INSERT."""
        self.session.add(pokemon)

    def commit(self) -> None:
        """Commit the transaction. The repository owns the session."""
        self.session.commit()

    def rollback(self) -> None:
        """Roll back the transaction."""
        self.session.rollback()
```

`session.add()` only marks the object. The `INSERT` statements (for the Pokémon, the
detail and each move) are sent at `commit()`, in the right order, because of the
cascade in the entity.

### 4. Service: extend `src/pokemon/service.py`

Change the imports at the top:

```python
from sqlalchemy.exc import IntegrityError

from pokemon.entity import Attacke, Pokemon, PokemonDetail
from pokemon.exceptions import ConflictError, NotFoundError
from pokemon.repository import PokemonRepository
from pokemon.schemas import PokemonCreate, PokemonQuery
```

Add the method to the class:

```python
    def create(self, data: PokemonCreate) -> Pokemon:
        """Create a new Pokémon.

        Raises:
            ConflictError: if the id or the name already exists.
        """
        if self.repository.exists_by_id(data.id):
            raise ConflictError(f"A Pokémon with id {data.id} already exists")
        if self.repository.exists_by_name(data.name):
            raise ConflictError(f"A Pokémon with name {data.name} already exists")

        pokemon = Pokemon(
            id=data.id,
            name=data.name,
            typ1=data.typ1.value,
            typ2=data.typ2.value if data.typ2 is not None else None,
            groesse_m=data.groesse_m,
            gewicht_kg=data.gewicht_kg,
            legendaer=data.legendaer,
            detail=PokemonDetail(
                fangrate=data.detail.fangrate,
                basis_erfahrung=data.detail.basis_erfahrung,
            ),
            attacken=[
                Attacke(
                    name=attacke.name,
                    typ=attacke.typ.value,
                    staerke=attacke.staerke,
                    genauigkeit=attacke.genauigkeit,
                )
                for attacke in data.attacken
            ],
        )
        self.repository.add(pokemon)
        try:
            self.repository.commit()
        except IntegrityError as error:
            # Another request was faster than the checks above (race condition)
            self.repository.rollback()
            raise ConflictError("The Pokémon already exists") from error
        return pokemon
```

`.value` turns the enum member into a plain string, so the entity holds the same type
that it reads from the database. (PostgreSQL would accept the enum member as well, but
the attribute would then hold an enum object until the row is read again.)

### 5. Router: extend `src/pokemon/router.py`

Change the imports:

```python
from pokemon.schemas import (
    PageInfo,
    PokemonCreate,
    PokemonPage,
    PokemonQuery,
    PokemonResponse,
)
```

Add at the end of the file:

```python
@router.post("", status_code=status.HTTP_201_CREATED)
def post(data: PokemonCreate, request: Request, service: ServiceDep) -> Response:
    """Create a new Pokémon. The response has no body, only the header `Location`."""
    pokemon = service.create(data)
    location = str(request.url_for("get_by_id", pokemon_id=pokemon.id))
    return Response(status_code=status.HTTP_201_CREATED, headers={"Location": location})
```

`request.url_for("get_by_id", ...)` builds the URL from the **name of the route
function**. It stays correct if you change the prefix or the host.

### 6. App: add the handler in `src/pokemon/app.py`

Change the import and add the function:

```python
from pokemon.exceptions import ConflictError, NotFoundError
```

```python
@app.exception_handler(ConflictError)
def handle_conflict(_request: Request, error: ConflictError) -> JSONResponse:
    """Turn a ConflictError into the status code 409."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(error)},
    )
```

## Check it

Create a file `new-pokemon.json` **outside of Git** (or in your temp folder):

```json
{
  "id": 600,
  "name": "Testmon",
  "typ1": "Feuer",
  "typ2": null,
  "groesse_m": 1.2,
  "gewicht_kg": 30.5,
  "legendaer": false,
  "detail": { "fangrate": 100, "basis_erfahrung": 150 },
  "attacken": [
    { "name": "Glut", "typ": "Feuer", "staerke": 40, "genauigkeit": 100 }
  ]
}
```

```shell
curl.exe -i -X POST -H "Content-Type: application/json" --data "@new-pokemon.json" http://127.0.0.1:8000/pokemon
curl.exe -i http://127.0.0.1:8000/pokemon/600
```

`--data "@file"` sends the content of the file. This avoids the quoting problems of
JSON on the PowerShell command line.

| Request | Expected |
|---|---|
| POST valid | `201`, header `location: http://127.0.0.1:8000/pokemon/600`, empty body |
| GET the `Location` | `200` with Testmon, detail and the move |
| POST again | `409` (the id exists) |
| POST with `"id": 100` | `422` (outside 494 to 649) |
| POST with `"typ1": "Quatsch"` | `422` |
| POST with `"detail": {"fangrate": 0, ...}` | `422` |
| POST with an unknown field | `422` |

The Swagger UI at <http://127.0.0.1:8000/docs> shows the model and lets you try
requests. Remember that the new Pokémon stays in the database. To start clean again:
`docker compose down -v` and `docker compose up -d` in `extras/compose/postgres`.

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| `422` for valid-looking JSON | Read the `loc` and `msg` in the response. They name the field. Common: a `null` for a required field, a number as text, a wrong enum value. |
| `500` with `IntegrityError` | A rule exists in the database but not in the model. Add the rule to the Pydantic model. |
| `500` with `DataError` or `numeric field overflow` | A value is too large for the column. Limit it in the model. |
| `Location` shows `localhost` or an unexpected host | It comes from the request's `Host` header. That is correct. |
| Float rounding (`1.55` becomes `1.6`) | The column has one decimal place. Pydantic does not check decimals of a `float`. Document it or use `Decimal`. |

## Commit

```shell
git add src
git commit -m "feat(api): add POST with validation"
```

## Prompt idea

```text
Context: FastAPI project with layers router, service, repository. Schema in
extras/compose/postgres/init/01-schema.sql, entities in src/pokemon/entity.py.
Task: Add POST /pokemon. Request model with Pydantic validation (id 494-649, name 1-50
characters, typ as StrEnum, positive size and weight within the column limits, nested
detail and up to 4 attacken, extra="forbid"). The service checks that id and name do
not exist (ConflictError), saves the Pokémon with detail and moves in one transaction
and turns IntegrityError into ConflictError. ConflictError becomes 409. Success is 201
with a Location header built with request.url_for. Comments in English.
```
