# 11 Finishing and handing in

**Goal:** The project works from a clean start, the documentation is up to date, the
checklist is complete and you can demonstrate every criterion.

**Checklist items:** Before handing in (all of them).

## 1. Quality checks

Run everything once, from the project root:

```shell
uv run ruff format --check
uv run ruff check
uv run ty check
uv run pytest
```

All four must pass without errors. The course asks to **show that ruff works**, so keep
the output (or a screenshot) at hand.

If `ruff format --check` fails, run `uv run ruff format` and commit the result
(`style: format code with ruff`).

## 2. Clean up the project metadata

Open `pyproject.toml` and replace the placeholder:

```toml
description = "Add your description here"
```

with a real description, for example:

```toml
description = "REST API for Pokémon of the 5th generation with FastAPI and PostgreSQL"
```

Check the `authors` entry as well.

## 3. Check the seed data

The values in `02-seed.sql` were typed from memory. Compare a few of them (height,
weight, catch rate, move power) with a reliable source such as PokeAPI or Bulbapedia.
Correct mistakes in `02-seed.sql` and reload the database. Then run the tests again,
because `test_get.py` expects the current values (names, types and counts).

## 4. Update the README

The README must describe how someone else starts the project. Check these points:

- [ ] The "Project status" table shows the finished steps as `done`.
- [ ] The setup lists `.env`: copy `.env.example` to `.env` and set the password.
- [ ] How to start the server: `uv run pokemon`.
- [ ] A table of the endpoints:

  | Method | Path | Description | Status codes |
  |---|---|---|---|
  | GET | `/pokemon/{id}` | One Pokémon, supports `If-None-Match` | 200, 304, 404, 422 |
  | GET | `/pokemon` | Search with `name`, `typ`, `legendaer`, `page`, `size` | 200, 422 |
  | POST | `/pokemon` | Create a Pokémon | 201, 409, 422 |
  | PUT | `/pokemon/{id}` | Replace a Pokémon, needs `If-Match` | 204, 404, 409, 412, 422, 428 |

- [ ] How to run the tests: `uv run pytest` (database container must run).
- [ ] The project structure matches the real folders (`tests/`, the new modules).
- [ ] The link to the Swagger UI: <http://127.0.0.1:8000/docs>.

## 5. Tick the checklist

Go through [CHECKLIST.md](../../CHECKLIST.md) line by line. Tick an item only if you
have **seen it work**. If you dropped something on purpose, write it down at the
bottom of the file so the reader knows it was a decision.

## 6. Test a fresh start

This is the most valuable check. It finds everything that only works on your machine.

```shell
# 1. Clone the repository into a new folder (use your own repository URL or path)
git clone <repository> pokemon-fresh
cd pokemon-fresh

# 2. Create the settings
copy .env.example .env
# edit .env and set DB_PASSWORD to the value in extras/compose/postgres/compose.yml

# 3. Start the database from scratch (no old volume)
cd extras/compose/postgres
docker compose down -v
docker compose up -d
cd ../../..

# 4. Install and run
uv sync
uv run pytest
uv run pokemon
```

Stop your normal database container first if both use port 5432
(`docker compose down` in the original folder).

If a step fails, fix the cause in the **original** project, commit, and repeat.
Typical findings: a missing file in Git (check `git status` for untracked files that
the project needs), a missing dependency in `pyproject.toml`, or a README step that
is wrong.

## 7. Check the Git history

```shell
git log --oneline
git status
```

- [ ] Many small commits, each with a Conventional Commit message
      (`type(scope): description`, in English).
- [ ] No commit contains `.env`, passwords or the `.venv` folder.
      Check with `git log --all --oneline -- .env` (it must print nothing).
- [ ] Working tree is clean, everything is pushed.

Do not rewrite commits that are already pushed unless you are sure nobody else uses
them. A small "fix:" commit is better than a forced push.

The password for the local database is in `compose.yml` and therefore in Git. That is
acceptable for a local development database, but name it as such in the README (it
already does). If you want to avoid it, use the `.env` variant for the compose file:
`POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}` and a `.env` next to `compose.yml`.

## 8. Ask an AI for a code review

The professor recommends a review at the end of the project. Give the assistant the
code and ask specific questions:

```text
Review the code in src/pokemon and tests/ of this FastAPI project.
Look for: bugs, missing error handling, wrong HTTP status codes, SQL problems
(N+1 queries, missing transactions), inconsistencies between the Pydantic models
and the database schema, unclear names, missing docstrings.
Rank the findings by importance. Do not change code, only report.
```

Decide for each finding whether to fix it. Not every suggestion is an improvement.
Commit the fixes in small commits (`fix:` or `refactor:`).

## 9. Prepare the demonstration

A short script, in the order of the checklist. Use Swagger UI at `/docs` or your saved
requests.

| Step | Show | Say |
|---|---|---|
| 1 | `docker compose ps`, DB browser with the three tables | "PostgreSQL 18 in Docker, 1:1 and 1:N relation, seed data via init scripts" |
| 2 | `pyproject.toml`, `uv run ruff check`, `uv run ty check` | "uv manages the project, ruff and ty are configured and pass" |
| 3 | `GET /pokemon/644` | "Path parameter, Pydantic response with nested detail and moves" |
| 4 | `GET /pokemon?typ=Feuer&size=2` | "Query parameters validated by a Pydantic model, paging" |
| 5 | `GET /pokemon/644` twice with `If-None-Match` | "Conditional GET: ETag is the version, answer 304" |
| 6 | `POST /pokemon` valid, then with an invalid body | "201 with Location, 422 from Pydantic, 409 for duplicates" |
| 7 | `PUT` without header, with the current ETag, then again with the old one | "Optimistic locking: 428, 204, 412, so no lost update" |
| 8 | Code: `router.py` → `service.py` → `repository.py` | "Layers and dependency injection with `Depends`, SQLAlchemy only in the repository" |
| 9 | `uv run pytest` or the API client collection | "Integration tests for GET and POST" |
| 10 | `git log --oneline` | "Incremental development, one commit per step" |

Practice the sequence once, including a database reset before it
(`docker compose down -v` and `docker compose up -d`).

Questions you may get, with short answers:

- *Why a repository?* Only one place knows SQL. The service is easier to read and test.
- *Why `version` and not a timestamp?* A counter is exact. Timestamps can be equal
  for two quick changes.
- *Why `selectinload` for the moves?* A `JOIN` would multiply the rows, and lazy
  loading would send one query per Pokémon.
- *Why is `ETag` in quotes?* The HTTP standard defines the quotes as part of the value.
- *What is missing?* Authentication, `DELETE`, logging, TLS. They were not required.

## 10. If time is left (optional)

Only after everything above is done.

- `DELETE /pokemon/{id}` with `204`. The cascade in the entity removes detail and moves.
- Logging with the standard `logging` module: one line per request or per error.
- A health endpoint `GET /health` that checks the database connection.
- A second database for the tests (see guide 09).
- GitHub Actions workflow that runs `ruff`, `ty` and `pytest` with a PostgreSQL
  service container.
- Export these guides as PDF, for example with a Markdown to PDF extension in VS Code.

## Final checklist

- [ ] ruff, ty and pytest pass
- [ ] `pyproject.toml` has a real description
- [ ] Seed data checked
- [ ] README up to date, including `.env` and the endpoint table
- [ ] `CHECKLIST.md` ticked and honest
- [ ] Fresh start works from a new clone
- [ ] Git history is clean and pushed, no secrets in it
- [ ] Demonstration practised

## Commit

```shell
git add README.md CHECKLIST.md pyproject.toml
git commit -m "docs: update README and checklist"
```
