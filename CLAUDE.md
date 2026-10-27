# CLAUDE.md

## Project
`fastapi-installer` is a CLI that generates production-ready FastAPI projects
(`fastapi-installer new my-app`). The source is in `src/fastapi_installer/`:
- `config.py`: option enums and `ProjectConfig`
- `registry.py`: which option values are supported, and which template layer each one adds
- `generator.py`: renders the template layers in order
- `cli.py` / `prompts.py`: the command line and the interactive questions
- `templates/`: one folder per layer. `.jinja` files are rendered, other files are copied as-is.

### Template layer contract
Layers are applied in order (`base` → architecture → database → orm → migrations → auth →
testing → infra → package manager), and a later layer overwrites a file with the same path.
Small per-option differences go in Jinja conditionals inside `base` (`pyproject.toml`,
`.env.example`, `README.md`). Anything larger is a file owned by one layer. Files other
layers rely on:
- database layer: `core/database.py` exposing `DatabaseSettings` with a `url` property
- orm layer: `infrastructure/db/session.py` exposing `get_session`, `ping_database` and
  `close_database`; `infrastructure/db/models.py` exposing `Base`;
  `presentation/api/deps.py` exposing `SessionDep`, `DatabaseHealthDep` and `<Feature>ServiceDep`

A new option value must provide these same names so the other layers keep working.

## Commands
- `make install`: install dependencies
- `make local-setup`: one-time developer setup (deps, git repo, pre-commit hook)
- `make dev`: generate a fresh demo project into `.playground/` and run its dev server
- `make lint` / `make format` / `make test` / `make check`

Full command reference: `docs/commands.md`. Planned work: `docs/todo.md`.

## Rules

### 1. Lint must pass
Every new task or feature must pass `make lint` (ruff check + ruff format check) before it
counts as done. Run `make format` to fix issues; do not silence rules with `noqa` unless
there is a written reason next to the `noqa` comment.

### 2. Tests must cover edge cases, not only the happy path
Every new feature needs unit tests that cover:
- valid input (happy path)
- invalid, empty, malformed and boundary input (wrong types, special characters, reserved
  words, very long values, missing values)
- failure paths: missing files, existing or non-empty directories, unsupported options,
  user cancelling a prompt

Assume the end user can do anything. The system must never crash with a raw traceback; it
must fail with a clear error message and a non-zero exit code. Write a test that proves
this for every user-facing failure.

### 3. Commits must be verified
Never commit until `make check` (lint + tests) passes. The pre-commit hook in `.githooks/`
enforces this. Never bypass it with `--no-verify`.

Every commit must also be signed (this repo uses SSH signing: `commit.gpgsign = true`,
`gpg.format = ssh`). Never disable signing or pass `--no-gpg-sign`. If signing fails because
the key is not loaded, ask the developer to run `ssh-add --apple-use-keychain <key>`.

### 4. Split commits after verification and review
After the changes are verified and reviewed, commit them as small, focused commits: one
logical change per commit (for example: feature code, its tests, docs). Do not bundle
unrelated changed files into one commit. Use clear messages in the imperative mood
("Add Postgres template layer").

### 5. No force push
Never run `git push --force`, `--force-with-lease`, or `-f`, and never rewrite history that
has been pushed.

### 6. Clean, ordered imports
Imports are grouped and sorted (standard library, third-party, then local) and enforced by
ruff's `I` rule. No unused imports, no wildcard imports, and use absolute imports
(`from fastapi_installer.config import ...`). `make format` sorts them automatically.

Note: files under `src/fastapi_installer/templates/` are excluded from ruff. Lint generated
output by generating a project (`make dev`, or the generator tests) rather than linting the
templates directly.
