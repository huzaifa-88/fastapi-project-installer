# Developer commands

Command reference for working on fastapi-installer. Run everything from the repo root unless a
section says otherwise.

**Requirements:** [uv](https://docs.astral.sh/uv/getting-started/installation/), `make`, and
Docker Desktop (only for `make dev` and for running generated projects).

## First-time setup

```bash
make local-setup
```

Installs Python and all dependencies, creates the git repo if there isn't one, and turns on the
pre-commit hook that runs `make check` before every commit.

## Daily workflow

| Command | What it does |
|---|---|
| `make` / `make help` | List all commands |
| `make install` | Install or update dependencies (`uv sync`) |
| `make dev` | Generate a fresh demo project in `.playground/demo-app`, start its Postgres (port 55432), run migrations and start the server on http://127.0.0.1:8000/docs |
| `make dev-down` | Stop the demo project's Postgres and delete its data |
| `make format` | Format code, sort imports and auto-fix lint issues |
| `make lint` | Check lint, import order and formatting without changing files |
| `make test` | Run the test suite |
| `make check` | `lint` + `test`; must pass before every commit |
| `make clean` | Stop the demo Postgres and remove caches, build output and `.playground/` |

Use a different port for the demo database: `make dev DEV_DB_PORT=5440`.

A typical change: edit code or templates → `make format` → `make check` → try it with `make dev`.

## Running the CLI locally

```bash
uv run fastapi-installer --help
uv run fastapi-installer --version
uv run fastapi-installer new my-app -o .playground/my-app            # interactive
uv run fastapi-installer new my-app -y -o .playground/my-app         # defaults, no questions
uv run fastapi-installer new my-app -y --infra none --migrations none -o .playground/my-app
uv run fastapi-installer new my-app -y -o .playground/my-app --force # overwrite a non-empty folder
```

`.playground/` is git-ignored, so use it for anything you generate by hand.

### All `new` options

| Flag | Values (supported now) | Default |
|---|---|---|
| `--arch` | `clean` | `clean` |
| `--db` | `postgres` | `postgres` |
| `--orm` | `sqlalchemy` | `sqlalchemy` |
| `--migrations` | `alembic`, `none` | `alembic` |
| `--api` | `rest` | `rest` |
| `--auth` | `jwt`, `none` | `jwt` |
| `--testing` | `pytest`, `none` | `pytest` |
| `--infra` | `docker-compose`, `none` | `docker-compose` |
| `--pm` | `uv` | `uv` |
| `-o`, `--output` | target folder | `./<name>` |
| `-y`, `--yes` | use defaults for anything not passed | off |
| `--force` | write into a non-empty folder | off |

### Install the CLI globally (as an end user would)

```bash
uv tool install --editable .        # code changes apply immediately
fastapi-installer new my-app
uv tool uninstall fastapi-installer
```

## Testing

```bash
make test                                    # whole suite
uv run pytest -v                             # list every test
uv run pytest tests/test_generator.py        # one file
uv run pytest -k migrations_none             # tests whose name matches
uv run pytest -x                             # stop at the first failure
```

The generator tests render every combination of supported options and check the output for
leftover `{{ }}` placeholders, compile errors and ruff violations.

## Working on templates

Templates live in `src/fastapi_installer/templates/`, one folder per option (see the
template layer contract in `CLAUDE.md`).

```bash
# after editing a template, regenerate and inspect the result
uv run fastapi-installer new t -y -o .playground/t --force
find .playground/t -type f | sort
```

## Running a generated project

From inside the generated project folder:

```bash
cp .env.example .env
uv sync
docker compose up -d db                      # start PostgreSQL
uv run alembic upgrade head                  # create/update tables
uv run fastapi dev src/<slug>/main.py        # dev server with reload
docker compose up --build                    # whole stack in containers
docker compose down -v                       # stop and delete the database data
```

Migrations:

```bash
uv run alembic revision --autogenerate -m "add products"   # create a migration from model changes
uv run alembic upgrade head                                 # apply
uv run alembic downgrade -1                                 # undo the last one
uv run alembic check                                        # models and migrations in sync?
```

## Building the package

```bash
uv build                 # creates dist/*.whl and dist/*.tar.gz
unzip -l dist/*.whl      # check that the templates are included
```

## Git

- Commits run `make check` through the pre-commit hook. Don't bypass it with `--no-verify`.
- Make small commits, one logical change each.
- Never force push.

See `CLAUDE.md` for the full rules.

## Troubleshooting

| Problem | Fix |
|---|---|
| `docker: command not found` | Open a new terminal, or run `source ~/.zprofile`. If that doesn't help, add `export PATH="$PATH:$HOME/.docker/bin"` to `~/.zshrc` |
| `Bind for ...:55432 failed: port is already allocated` | Run `make dev-down`, or use another port: `make dev DEV_DB_PORT=5440` |
| `password authentication failed` | Another Postgres is answering on that port. Pick a free one and set `POSTGRES_PORT` in `.env` |
| `Directory ... already exists and is not empty` | Pass `--force`, or choose another `-o` folder |
| `Not supported yet (coming soon)` | That option has no template yet; see `todo.md` |
| Lint fails on a long line | `make format`, then wrap whatever ruff can't fix automatically |
