# Project checklist

Tick each item when it is done and verified. Based on the course checklist "Checkliste für das Python-Projekt".

## Preparation

- [x] PostgreSQL 18 runs as a Docker container
  - [x] 1:1 relation
  - [x] 1:N relation
  - [x] Connected with a DB browser and tables checked
- [x] Git repository with incremental commits ("commit early, commit often")

## Infrastructure

- [x] `pyproject.toml` with configuration for uv, ruff and ty
- [x] uv: `uv sync` installs everything from a clean checkout
- [ ] Formatter defined in `pyproject.toml` (`[tool.ruff.format]`, run with `uv run ruff format`)
- [x] ruff: `uv run ruff check` and `uv run ruff format --check` pass
- [x] ty: `uv run ty check` passes

## App server

- [ ] FastAPI server starts and answers a simple GET request
- [ ] Database access with SQLAlchemy
  - [ ] Entities for all three tables, including both relations
  - [ ] Access only through a repository class
- [ ] Layered structure with dependency injection (`Depends`) for service and repository
- [ ] Pydantic models for responses
- [ ] GET requests
  - [ ] By path parameter (`GET /pokemon/{id}`), `404` for an unknown id
  - [ ] By query parameter (e.g. `GET /pokemon?name=...`)
  - [ ] Conditional GET: `ETag` in the response, `If-None-Match` returns `304`
- [ ] POST request
  - [ ] Validation with Pydantic, `422` for invalid data
  - [ ] `201 Created` with a `Location` header
- [ ] PUT request
  - [ ] Validation with Pydantic
  - [ ] Lost-update protection with `version` and `If-Match`
  - [ ] `428` without `If-Match`, `412` for an outdated version, `204` on success

## Testing

One of the two ways is enough: pytest integration tests **or** an API client
collection (e.g. Postman, Bruno or Thunder Client).

- [ ] GET requests tested (path, query, conditional)
- [ ] POST requests tested (valid and invalid)
- [ ] Tests can be repeated: the database is reloaded with `docker compose down -v`
      and `docker compose up -d`

## Before every commit

- [ ] `uv run ruff check` and `uv run ruff format`
- [ ] `uv run ty check`

## Before handing in

- [ ] Can demonstrate that ruff works: `uv run ruff check` and `uv run ruff format --check`
      run without errors, the type checker too
- [ ] Commit history shows the step-by-step development (many small commits)
- [ ] Fresh start works: clone, `uv sync`, `docker compose up -d`, start the server
- [ ] README describes the steps above and is up to date
- [ ] All items in this checklist are ticked or consciously dropped
- [ ] Everything is committed and pushed
