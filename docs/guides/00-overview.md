# Implementation guides: overview

These guides walk through the remaining tasks of the project, one step at a time.
Every guide has the same structure: goal, background, steps with code, how to check
the result, common pitfalls, a commit message and an idea for an AI prompt.

> **Status of the code.** The code in steps 1 to 9 was run against a PostgreSQL 18
> container that was created from the init scripts in this repository. `ruff`, `ty`
> and 30 pytest tests passed. The guides themselves were not followed on your machine
> yet, so small differences (paths, versions) are possible. If something does not
> work, read the error message first, then compare with the "Common pitfalls" part.

## The guides

| # | Guide | Checklist item | Suggested commit |
|---|---|---|---|
| 01 | [Hello world](01-hello-world.md) | FastAPI server starts | `feat: add hello world endpoint` |
| 02 | [Configuration and database](02-configuration-and-database.md) | Database access | `feat(db): add settings and database connection` |
| 03 | [Entities](03-entities.md) | SQLAlchemy entities with both relations | `feat(db): add SQLAlchemy entities` |
| 04 | [Layers and first endpoint](04-layers-and-first-endpoint.md) | Dependency injection, Pydantic response, GET by id | several, see the guide |
| 05 | [GET with query parameters](05-get-with-query-parameters.md) | GET by query parameter | `feat(api): add GET with query parameters` |
| 06 | [Conditional GET](06-conditional-get.md) | `ETag` and `If-None-Match` | `feat(api): add conditional GET with ETag` |
| 07 | [POST](07-post.md) | POST with validation | `feat(api): add POST with validation` |
| 08 | [PUT](08-put.md) | PUT with lost-update protection | `feat(api): add PUT with optimistic locking` |
| 09 | [pytest](09-pytest-integration-tests.md) | Tests for GET and POST | `test: add integration tests` |
| 10 | [API client](10-api-client-testing.md) | Alternative to pytest (optional) | `test: add API client requests` |
| 11 | [Finishing](11-finishing-and-hand-in.md) | Before handing in | `docs: update README and checklist` |

The course only asks for one way of testing: pytest **or** an API client. Do guide 09
or guide 10, or both if time is left.

## Final project structure

```text
.
├── .env                         # not committed, contains the DB password
├── .env.example                 # committed, shows which variables exist
├── extras/compose/postgres/     # compose.yml and init/ (already there)
├── src/pokemon/
│   ├── __init__.py              # main(): starts the server
│   ├── app.py                   # FastAPI app and exception handlers
│   ├── config.py                # settings from .env
│   ├── database.py              # engine and session factory
│   ├── dependencies.py          # factory functions for Depends
│   ├── entity.py                # SQLAlchemy entities
│   ├── exceptions.py            # NotFoundError, ConflictError, ...
│   ├── repository.py            # SQL queries
│   ├── router.py                # REST endpoints
│   ├── schemas.py               # Pydantic models
│   └── service.py               # business logic
└── tests/
    ├── conftest.py              # fixtures: database reset, client
    ├── test_get.py
    ├── test_post.py
    └── test_put.py
```

Request flow: `router` (HTTP) calls `service` (rules), which calls `repository`
(SQL), which uses the `entity` classes. Each layer only talks to the one below it.

## Work loop for every step

1. Read the goal and the background of the guide.
2. Write the code yourself or give the prompt idea to your AI assistant. Read the
   result before you accept it.
3. Run the server or the tests and check the result with the "Check it" part.
4. Run the quality checks:
   ```shell
   uv run ruff format
   uv run ruff check
   uv run ty check
   ```
5. Commit with a Conventional Commit message. One step, one commit.

## Tips for working with an AI assistant

- **Small prompts.** One prompt per step, not "build the whole server". Small steps
  are easy to review and give you a clean commit history.
- **Give context.** Tell it the file layout, the Python version (3.13), the libraries
  (FastAPI, SQLAlchemy 2, Pydantic 2, psycopg 3) and the table definitions in
  `extras/compose/postgres/init/01-schema.sql`.
- **Ask for the reason.** "Why this and not that?" helps you to explain the code when
  you present the project.
- **Paste the full error message** instead of describing it.
- **Check the result against the rules.** Comments and docstrings in English,
  commit messages in Conventional Commits format, no secrets in Git.
- **Do not accept code you cannot explain.** Ask for a simpler version instead.

A prompt template that works well:

```text
Context: FastAPI project, Python 3.13, SQLAlchemy 2, Pydantic 2, psycopg 3, uv.
Files: <list the relevant files>.
Task: <one small step>.
Rules: comments in English, type hints everywhere, code passes ruff and ty.
Show only the changed files.
```

## Versions used for the guides

| Package | Version |
|---|---|
| Python | 3.13 |
| FastAPI | 0.159 |
| SQLAlchemy | 2.1 |
| Pydantic | 2.14 |
| psycopg | 3.3 |
| pytest | 9.1 |

Newer versions should work as well. If an API changed, the error message and the
official documentation are the first places to look.
