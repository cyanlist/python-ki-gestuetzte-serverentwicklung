# 08 PUT with lost-update protection

**Goal:** `PUT /pokemon/{id}` replaces a Pokémon. The client must send the version it
has read in the header `If-Match`. If someone else changed the Pokémon in the
meantime, the update is rejected with `412`.

**Checklist item:** PUT request → "Validation with Pydantic", "Lost-update protection
with `version` and `If-Match`", "`428` without `If-Match`, `412` for an outdated
version, `204` on success".

## Background

### The lost update

```text
Alice reads Zekrom (version 0)      Bob reads Zekrom (version 0)
Alice changes the weight, PUT  ───▶ saved, version 1
                                     Bob changes the height, PUT ───▶ ???
```

Without protection, Bob's request overwrites Alice's change without notice. This is the
**lost update**.

### Optimistic locking

"Optimistic" means: no locks while the user works. Instead, every row has a **version
number**. A change is only accepted if the client knows the **current** version.

1. `GET` returns the version in the `ETag` header.
2. `PUT` sends it back in `If-Match`.
3. If the versions differ, the server answers `412 Precondition Failed`.

The check is done twice:

- **In the service** (`pokemon.version != version`): gives a clear error early.
- **In the database update** (`version_id_col`): SQLAlchemy sends
  `UPDATE ... WHERE id = ? AND version = <old>`. If no row matches, because another
  request was faster between the check and the update, it raises `StaleDataError`.
  This second check closes the small gap in which two requests pass the first one.

### Status codes

| Situation | Code |
|---|---|
| success | `204 No Content`, header `ETag` with the new version |
| header `If-Match` missing | `428 Precondition Required` |
| `If-Match` malformed or the version is outdated | `412 Precondition Failed` |
| id does not exist | `404` |
| invalid body | `422` |
| new name belongs to another Pokémon | `409` |

### What PUT changes

`PUT` **replaces** the resource, so the body contains all fields of the Pokémon itself
(except `typ2`, which may be `null`). Detail and moves are not part of this `PUT`, to
keep it simple.

## Steps

### 1. Exception: extend `src/pokemon/exceptions.py`

```python
class VersionOutdatedError(Exception):
    """The client works with an outdated version of the Pokémon."""

    def __init__(self, version: int) -> None:
        """Remember the version the client sent."""
        super().__init__(f"The version {version} is outdated")
        self.version = version
```

### 2. Request model: extend `src/pokemon/schemas.py`

Add the class **above** `PokemonCreate`:

```python
class PokemonUpdate(PokemonBase):
    """Request body of PUT: all fields of the Pokémon itself.

    PUT replaces the whole resource, so no field is optional (except `typ2`).
    Detail and moves are not changed by PUT.
    """
```

It has no own fields: it uses the fields of `PokemonBase` from guide 07. Having its
own class keeps the OpenAPI documentation clear and lets the two models change
independently later.

### 3. Repository: change `exists_by_name` in `src/pokemon/repository.py`

A Pokémon may keep its own name during `PUT`, so the check needs a way to ignore one
id:

```python
    def exists_by_name(self, name: str, *, exclude_id: int | None = None) -> bool:
        """Check whether a Pokémon with this name exists.

        With `exclude_id`, the Pokémon with this id is ignored. This is needed for
        PUT, where a Pokémon may keep its own name.
        """
        statement = (
            select(func.count()).select_from(Pokemon).where(Pokemon.name == name)
        )
        if exclude_id is not None:
            statement = statement.where(Pokemon.id != exclude_id)
        return bool(self.session.scalar(statement))
```

The call in `create` (`exists_by_name(data.name)`) still works.

### 4. Service: extend `src/pokemon/service.py`

Change the imports at the top:

```python
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from pokemon.entity import Attacke, Pokemon, PokemonDetail
from pokemon.exceptions import ConflictError, NotFoundError, VersionOutdatedError
from pokemon.repository import PokemonRepository
from pokemon.schemas import PokemonCreate, PokemonQuery, PokemonUpdate
```

Add the method to the class:

```python
    def update(self, pokemon_id: int, version: int, data: PokemonUpdate) -> Pokemon:
        """Replace the data of a Pokémon if the client knows the current version.

        Raises:
            NotFoundError: if no Pokémon has this id.
            VersionOutdatedError: if the version is not the current one.
            ConflictError: if the new name belongs to another Pokémon.
        """
        pokemon = self.find_by_id(pokemon_id)
        if pokemon.version != version:
            raise VersionOutdatedError(version)
        if self.repository.exists_by_name(data.name, exclude_id=pokemon_id):
            raise ConflictError(f"A Pokémon with name {data.name} already exists")

        pokemon.name = data.name
        pokemon.typ1 = data.typ1.value
        pokemon.typ2 = data.typ2.value if data.typ2 is not None else None
        pokemon.groesse_m = data.groesse_m
        pokemon.gewicht_kg = data.gewicht_kg
        pokemon.legendaer = data.legendaer
        try:
            self.repository.commit()
        except StaleDataError as error:
            # Someone changed the row between our check and the UPDATE
            self.repository.rollback()
            raise VersionOutdatedError(version) from error
        except IntegrityError as error:
            self.repository.rollback()
            raise ConflictError("The name already exists") from error
        return pokemon
```

There is no `session.add()`. The object was loaded by this session, so SQLAlchemy
notices the changed attributes and sends the `UPDATE` at `commit()`. After the commit
the object has the **new** version, so `pokemon.version` can go into the `ETag`.

### 5. Router: extend `src/pokemon/router.py`

Change the imports:

```python
from fastapi import APIRouter, Header, HTTPException, Query, Request, Response, status

from pokemon.dependencies import ServiceDep
from pokemon.schemas import (
    PageInfo,
    PokemonCreate,
    PokemonPage,
    PokemonQuery,
    PokemonResponse,
    PokemonUpdate,
)
```

Add the helper next to `_etag`:

```python
def _parse_version(if_match: str) -> int | None:
    """Extract the version from `If-Match: "3"`. Return None if it is malformed."""
    if len(if_match) < 3 or not (if_match.startswith('"') and if_match.endswith('"')):
        return None
    try:
        return int(if_match[1:-1])
    except ValueError:
        return None
```

Add the endpoint at the end of the file:

```python
@router.put("/{pokemon_id}")
def put(
    pokemon_id: int,
    data: PokemonUpdate,
    service: ServiceDep,
    if_match: Annotated[str | None, Header()] = None,
) -> Response:
    """Replace a Pokémon. The header `If-Match` with the version is required."""
    if if_match is None:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="The header If-Match is required",
        )
    version = _parse_version(if_match)
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail='The header If-Match must look like "3"',
        )
    pokemon = service.update(pokemon_id, version, data)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": _etag(pokemon.version)},
    )
```

`Header()` reads the request header. The parameter name `if_match` is converted to
`If-Match` automatically (underscores become hyphens). It is optional (`None`) so the
function can answer `428` itself.

### 6. App: add the handler in `src/pokemon/app.py`

Change the import and add the function:

```python
from pokemon.exceptions import ConflictError, NotFoundError, VersionOutdatedError
```

```python
@app.exception_handler(VersionOutdatedError)
def handle_version_outdated(
    _request: Request, error: VersionOutdatedError
) -> JSONResponse:
    """Turn a VersionOutdatedError into the status code 412."""
    return JSONResponse(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        content={"detail": str(error)},
    )
```

## Check it

Create `update-zekrom.json` outside of Git:

```json
{
  "name": "Zekrom",
  "typ1": "Drache",
  "typ2": "Elektro",
  "groesse_m": 3.0,
  "gewicht_kg": 345.0,
  "legendaer": true
}
```

In PowerShell, `curl.exe` needs `\"` for the quotes in the header:

```shell
curl.exe -i http://127.0.0.1:8000/pokemon/644
curl.exe -i -X PUT -H "Content-Type: application/json" --data "@update-zekrom.json" http://127.0.0.1:8000/pokemon/644
curl.exe -i -X PUT -H "Content-Type: application/json" -H 'If-Match: \"0\"' --data "@update-zekrom.json" http://127.0.0.1:8000/pokemon/644
curl.exe -i -X PUT -H "Content-Type: application/json" -H 'If-Match: \"0\"' --data "@update-zekrom.json" http://127.0.0.1:8000/pokemon/644
curl.exe -i http://127.0.0.1:8000/pokemon/644
```

| Request | Expected |
|---|---|
| `GET` | `etag: "0"` (with fresh seed data) |
| `PUT` without `If-Match` | `428` |
| `PUT` with `\"0\"` | `204`, header `etag: "1"` |
| the same `PUT` again | `412` (the version `0` is outdated now: lost update prevented) |
| `GET` again | `etag: "1"` and the changed height |
| `PUT` with `If-Match: abc` | `412` |
| `PUT /pokemon/999999` with a valid header | `404` |
| `PUT` with `"groesse_m": -1` | `422` |
| `PUT` with `"name": "Reshiram"` | `409` |

You can combine this with guide 06: a `GET` with `If-None-Match: "0"` answers `304`
before the `PUT` and `200` with the new version after it.

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| Always `412` | The quotes are missing in `If-Match` (see above), or you use an old version. Read the `ETag` of a fresh `GET`. |
| `428` although you sent the header | The header name is misspelled, or a proxy removed it. |
| Version is not increased | `version_id_col` is missing in the entity (guide 03). |
| `StaleDataError` as a `500` | The `except StaleDataError` is missing in the service. |
| Changed row, but the second `PUT` with the new version fails | You sent the **old** `ETag` again. Take the one from the `PUT` response (or a new `GET`). |
| Only the first request works after a test | The data stays in the database. Reload it: `docker compose down -v` and `docker compose up -d`. |
| `422` for fields you did not want to change | PUT replaces everything. Send all fields. (A `PATCH` would allow partial changes. That is not required.) |

## Commit

```shell
git add src
git commit -m "feat(api): add PUT with optimistic locking"
```

## Prompt idea

```text
Context: FastAPI project with layers router, service, repository. The entity Pokemon has
an integer column "version" mapped with version_id_col. GET already sends the ETag.
Task: Add PUT /pokemon/{pokemon_id}. The request model has the Pokémon's own fields
(no id, detail or attacken). The header If-Match must contain the version in double
quotes: missing header gives 428, malformed header gives 412. The service loads the
Pokémon (404 if missing), compares the version (VersionOutdatedError gives 412), checks
that the name is not used by another Pokémon (409), changes the fields and commits.
Catch StaleDataError and turn it into VersionOutdatedError. The response is 204 with the
new ETag. Comments in English.
```
