# 06 Conditional GET

**Goal:** `GET /pokemon/{id}` sends an `ETag` header. If the client repeats the request
with `If-None-Match` and nothing changed, the server answers `304 Not Modified`
without a body.

**Checklist item:** GET requests → "Conditional GET: `ETag` in the response,
`If-None-Match` returns `304`".

## Background

A conditional request saves bandwidth. The client says "I already have version X.
Send the resource only if it is different."

```text
1st request:  GET /pokemon/644
              → 200, body, header  ETag: "0"

2nd request:  GET /pokemon/644
              If-None-Match: "0"
              → 304, no body            (nothing changed)

after a PUT:  GET /pokemon/644
              If-None-Match: "0"
              → 200, new body, ETag: "1"  (version changed)
```

- The **ETag** is an identifier for a version of a resource. Here it is the `version`
  column. That is why the version counter is useful twice: for conditional GET and for
  optimistic locking (guide 08).
- The **quotes are part of the value**: `"0"`, not `0`.
- `If-None-Match` can contain several values (`"1", "2"`), weak ETags (`W/"1"`) and `*`.
  The helper below handles these cases.
- `304` has **no body**.

## Steps

### Router: `src/pokemon/router.py`

Change the import line and add the two helper functions below `router = ...`:

```python
from fastapi import APIRouter, Query, Request, Response, status
```

```python
def _etag(version: int) -> str:
    """Build the ETag header value. The quotes are part of the value."""
    return f'"{version}"'


def _matches(if_none_match: str | None, etag: str) -> bool:
    """Check whether the client already has the current version of the resource."""
    if if_none_match is None:
        return False
    candidates = [
        value.strip().removeprefix("W/") for value in if_none_match.split(",")
    ]
    return etag in candidates or "*" in candidates
```

Replace the function `get_by_id`:

```python
@router.get("/{pokemon_id}", response_model=PokemonResponse)
def get_by_id(
    pokemon_id: int,
    request: Request,
    response: Response,
    service: ServiceDep,
) -> PokemonResponse | Response:
    """Find a Pokémon by its Pokédex number.

    The response contains the header `ETag` with the version. If the request has the
    header `If-None-Match` with the current version, the answer is `304` without body.
    """
    pokemon = service.find_by_id(pokemon_id)
    etag = _etag(pokemon.version)
    if _matches(request.headers.get("If-None-Match"), etag):
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED, headers={"ETag": etag}
        )
    response.headers["ETag"] = etag
    return PokemonResponse.model_validate(pokemon)
```

How it works:

- `request: Request` gives access to the request headers.
- `response: Response` is a "template" response from FastAPI. Headers you set on it are
  added to the normal `200` response, while FastAPI still serializes the model.
- For `304` you return your own `Response` object. FastAPI sends it unchanged.
- The `304` answer should contain the `ETag` header as well.

## Check it

Start the server and run (note the escaped quotes `\"` for PowerShell and `curl.exe`):

```shell
curl.exe -i http://127.0.0.1:8000/pokemon/644
curl.exe -i -H 'If-None-Match: \"0\"' http://127.0.0.1:8000/pokemon/644
curl.exe -i -H 'If-None-Match: \"99\"' http://127.0.0.1:8000/pokemon/644
```

| Request | Expected |
|---|---|
| first | `200`, header `etag: "0"`, JSON body |
| with `\"0\"` | `304`, no body |
| with `\"99\"` | `200` with body (the version differs) |

Without the backslashes, PowerShell 5.1 removes the quotes before `curl.exe` receives
them, and the server then sees `If-None-Match: 0`. That does not match `"0"` and you
get `200`. In Bruno, Postman or an `.http` file (guide 10) you write the quotes
normally.

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| Always `200`, never `304` | The quotes are missing in the header (see above), or the ETag format differs. Compare the exact strings. |
| No `ETag` header in the `200` response | You returned `JSONResponse` or set the header on a different object. Use the injected `response` parameter. |
| `304` with a body | Use `Response(status_code=304)`, not a model. A `304` must not have a body. |
| Browser shows the cached page | Browsers handle `ETag` themselves. For testing use `curl.exe`, Bruno or Swagger UI. |
| `ETag` stays `"0"` after a change | The version is only increased by the ORM `UPDATE` (guide 08). A `psql` update does not change it unless you do it yourself. |

## Commit

```shell
git add src
git commit -m "feat(api): add conditional GET with ETag"
```

## Prompt idea

```text
Context: FastAPI router in src/pokemon/router.py, GET /pokemon/{pokemon_id}. The entity
has an integer column "version".
Task: Add the header ETag (the version in double quotes) to the response. If the
request has If-None-Match with the same value (also accept W/ prefix, comma lists and
*), return 304 without body and with the ETag header. Use the injected Response
object to set the header. Comments in English.
```
