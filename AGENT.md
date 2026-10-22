# AGENT.md

Ground rules for AI coding agents (and anyone else) working in this repository.
This complements `README.md` (setup, data model) and `CHECKLIST.md` (hand-in
requirements) — it does not replace them.

## Tooling

| Tool                                 | Purpose                     | Primary commands                                                |
| ------------------------------------ | --------------------------- | --------------------------------------------------------------- |
| [uv](https://docs.astral.sh/uv/)     | Package and project manager | `uv sync`, `uv run <cmd>`, `uv add [--dev] <pkg>`               |
| [ruff](https://docs.astral.sh/ruff/) | Linter and formatter        | `uv run ruff check`, `uv run ruff format`                       |
| [ty](https://docs.astral.sh/ty/)     | Type checker                | `uv run ty check`                                               |
| pytest                               | Integration tests           | `uv run pytest` (needs the DB container running)                |
| Docker / Compose                     | PostgreSQL 18 for local dev | `docker compose up -d` / `down -v` in `extras/compose/postgres` |
| GitHub CLI (`gh`)                    | PRs and merges              | `gh pr create`, `gh pr merge`, `gh pr view`                     |

Always run tools through `uv run` instead of activating the virtualenv manually,
so the right interpreter and dependency set are used.

## Branching

- `main` is the integration branch. Work on a **feature branch** unless the user
  explicitly says to work on `main` directly (e.g. a one-line docs fix).
- Branch names follow `<type>/<short-kebab-description>`, where `<type>` matches
  the commit type below, e.g. `feat/db-health-check`, `docs/agent-guidelines`.
- Before branching, sync first: `git fetch origin` and fast-forward the local
  base branch, so the new branch starts from an up-to-date `main`. Don't branch
  off a stale local `main` or off an unrelated feature branch.

## Commit messages: Conventional Commits + gitmoji

Spec references (read these for anything not covered here):

- Conventional Commits: <https://www.conventionalcommits.org/>
- gitmoji (full emoji list and meanings): <https://gitmoji.dev/>

Format: `<shortcode> <type>(<scope>): <description>` — English, imperative
mood, scope optional, one logical change per commit ("commit early, commit
often"). Use the gitmoji **shortcode** (`:sparkles:`), not the raw Unicode
emoji: GitHub and GitLab render the shortcode as the emoji in their web UI
anyway, but the raw character is plain ASCII everywhere else (terminals, CI
logs, `git log`), so it never breaks column alignment, encoding or grepping.

| Type       | Shortcode            | Use for                                                                  |
| ---------- | -------------------- | ------------------------------------------------------------------------ |
| `feat`     | `:sparkles:`         | new functionality                                                        |
| `fix`      | `:bug:`              | bug fixes                                                                |
| `build`    | `:package:`          | dependencies and build setup                                             |
| `chore`    | `:wrench:`           | configuration and maintenance                                            |
| `docs`     | `:memo:`             | documentation                                                            |
| `test`     | `:white_check_mark:` | tests                                                                    |
| `refactor` | `:recycle:`          | code changes without behavior change                                     |
| `perf`     | `:zap:`              | performance improvements                                                 |
| `style`    | `:art:`              | formatting-only changes (rarely needed; ruff format covers most of this) |
| `revert`   | `:rewind:`           | reverting a previous commit                                              |

For anything not in this table, look up the matching entry at
<https://gitmoji.dev/> instead of guessing or inventing a new emoji.

Examples:

```text
:sparkles: feat(api): add GET endpoint by id
:bug: fix(repository): close session on rollback
:memo: docs: rename attacke table to move in data model section
```

The shortcode is a visual aid, not a replacement for the type — keep both. The
Conventional Commit prefix alone must stay unambiguous even where a tool
doesn't expand the shortcode.

**Only commit when the user explicitly asks for it.** Preparing and running
checks is not the same as committing.

## Pull requests

**Push, open a PR, merge, and delete a branch are each a separate action that
needs its own explicit go-ahead from the user** — do not chain them
automatically just because an earlier one was approved.

- Open PRs with `gh pr create`, base `main`. Body has two sections:
  - `## Summary` — bullet points of what changed and why.
  - `## Test plan` — what was _actually_ run/verified (checked boxes), not a
    generic template.
- Merge with `gh pr merge <number> --merge` (no squash/rebase unless asked).
- After a merge, fast-forward local `main` (`git pull --ff-only origin main`),
  then delete the branch both locally (`git branch -d`) and on origin
  (`git push origin --delete`).

## Development loop

1. **Sync.** `git fetch origin`; fast-forward the base branch. Pulling in a
   teammate's changes can add new dependencies — check `pyproject.toml`/`uv.lock`
   for diffs and run `uv sync` again if they changed.
2. **Branch** from the up-to-date base (see above), or continue on the current
   feature branch for follow-up work on the same change.
3. **Implement** the change.
4. **Quality gates** before treating the work as done:
   `uv run ruff format`, `uv run ruff check`, `uv run ty check`, and
   `uv run pytest` whenever tests exist for the touched code.
5. **Actually run it** for anything touching the API or the database — static
   checks are not a substitute for exercising the change:
   - `docker compose up -d` in `extras/compose/postgres` for the database.
   - `uv run pokemon` to start the API (auto-reloads on file changes).
   - Hit the changed endpoint with `curl` (or the test suite) and check the
     real response, including the failure path (e.g. stop the DB container to
     confirm a health check actually flips).
6. **Commit / push / PR / merge / cleanup** — each only when the user explicitly
   asks for that specific step (see above).

Long-running commands (first `docker compose up -d` pulling an image, a cold
`uv sync`) should run in the background; wait for the completion notification
instead of polling or sleeping in a loop.

## Known environment gotchas (this machine)

- **Windows Smart App Control** may block a freshly downloaded compiled Python
  extension on its very first load (seen with SQLAlchemy's Cython module and
  psycopg's binary driver), surfacing as a DLL-load `ImportError` and a
  CodeIntegrity block event. This is not malware — Defender shows no threat —
  it's reputation evaluation. Retrying the server start once or twice resolves
  it. **Never disable Smart App Control** to work around this: Microsoft only
  allows re-enabling it via a clean Windows reinstall, which is far too
  destructive a trade-off for a local dev inconvenience.
- `gh` may not be on `PATH` yet in an already-open shell right after installing
  it. If `gh` is "not recognized", call it via its full path, e.g.
  `C:\Program Files\GitHub CLI\gh.exe`.
- A `cd` inside a backgrounded command does not persist to the next command in
  this environment — use absolute paths, or `cd` again per command.

## Keeping docs in sync

- Commit types and their meaning are also listed in `README.md`'s "Commit
  convention" section — update both if the convention changes.
- Tick items in `CHECKLIST.md` only once actually verified running (see step 5
  above), not just implemented.
