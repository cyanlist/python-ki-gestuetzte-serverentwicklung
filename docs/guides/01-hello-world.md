# 01 Hello world

**Goal:** A FastAPI server that starts with `uv run pokemon` and answers `GET /`.

**Checklist item:** App server → "FastAPI server starts and answers a simple GET
request".

## Background

- **FastAPI** is the web framework. You write Python functions and decorate them with
  the HTTP method and the path (`@app.get("/")`).
- **uvicorn** is the server that runs the app. FastAPI itself does not listen on a port.
- **uv** installs the packages and runs the commands in the project's virtual
  environment (`.venv`).
- The entry `pokemon = "pokemon:main"` under `[project.scripts]` in `pyproject.toml`
  makes `uv run pokemon` call the function `main` in `src/pokemon/__init__.py`.

## Steps

### 1. Install FastAPI and uvicorn

```shell
uv add fastapi "uvicorn[standard]"
```

This changes `pyproject.toml` and `uv.lock`.

### 2. Create the app: `src/pokemon/app.py`

```python
"""FastAPI application."""

from fastapi import FastAPI

app = FastAPI(title="Pokémon API")


@app.get("/")
def root() -> dict[str, str]:
    """Return a greeting to check that the server runs."""
    return {"message": "Hello from pokemon!"}
```

The functions are `def`, not `async def`. SQLAlchemy is used synchronously later, and
FastAPI runs normal `def` functions in a thread pool, so they do not block the server.

### 3. Start the server from `main`: `src/pokemon/__init__.py`

Replace the content of the file:

```python
"""Pokémon API."""

import uvicorn


def main() -> None:
    """Start the ASGI server. Entry point for `uv run pokemon`."""
    uvicorn.run("pokemon.app:app", host="127.0.0.1", port=8000, reload=True)
```

- `"pokemon.app:app"` is the import string: module `pokemon.app`, variable `app`.
- `reload=True` restarts the server when you save a file. That is handy while
  developing. It needs the import string instead of the app object.

## Check it

```shell
uv run pokemon
```

Open these URLs in the browser:

| URL | Expected |
|---|---|
| <http://127.0.0.1:8000/> | `{"message":"Hello from pokemon!"}` |
| <http://127.0.0.1:8000/docs> | Swagger UI with the endpoint (generated automatically) |
| <http://127.0.0.1:8000/openapi.json> | The OpenAPI description |

Stop the server with `Ctrl+C` in the terminal.

Run the quality checks:

```shell
uv run ruff format
uv run ruff check
uv run ty check
```

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| `Address already in use` or `error while attempting to bind` | Another process uses port 8000, often an old server. Stop it with `Ctrl+C`. Find the owner with `Get-NetTCPConnection -LocalPort 8000` (PowerShell). Or use another port in `main`. |
| Server runs although the terminal was closed | With `reload=True`, uvicorn starts a child process. Always stop with `Ctrl+C`, do not just close the window. |
| `uv run pokemon` says `Failed to spawn` | The entry in `[project.scripts]` or the function `main` does not exist. Check the spelling in `pyproject.toml` and `__init__.py`. |
| `ModuleNotFoundError: pokemon` | Run the command in the project folder. `uv run` installs the project itself into `.venv`. |

## Commit

```shell
git add pyproject.toml uv.lock src
git commit -m "feat: add hello world endpoint"
```

## Prompt idea

```text
Context: uv project with src layout, package "pokemon", Python 3.13.
Task: Add a FastAPI app in src/pokemon/app.py with GET / returning a JSON greeting.
Change main() in src/pokemon/__init__.py so that `uv run pokemon` starts it with
uvicorn on 127.0.0.1:8000 with reload. Plain def functions, type hints, comments in
English. Show the files and the uv command for the dependencies.
```
