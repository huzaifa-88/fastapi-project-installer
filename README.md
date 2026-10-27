# fastapi-installer

Generate a production-ready FastAPI project with one command.

```bash
fastapi-installer new my-app            # interactive
fastapi-installer new my-app -y         # use defaults, no questions
fastapi-installer new my-app --arch clean --db postgres --orm sqlalchemy --pm uv -y
```

## Supported options

Use `none` to leave a feature out, e.g. `--infra none` for no Docker files.

| Option          | Flag           | Supported now    | Coming soon            |
|-----------------|----------------|------------------|------------------------|
| Architecture    | `--arch`       | `clean`          | `monolithic`, `event-driven` |
| Database        | `--db`         | `postgres`       | `mysql`                |
| ORM             | `--orm`        | `sqlalchemy`     | `sqlmodel`             |
| Migrations      | `--migrations` | `alembic`, `none` |                       |
| API style       | `--api`        | `rest`           | `graphql`              |
| Authentication  | `--auth`       | `jwt`, `none`    |                        |
| Testing         | `--testing`    | `pytest`, `none` |                        |
| Infrastructure  | `--infra`      | `docker-compose`, `none` |                |
| Package manager | `--pm`         | `uv`             | `poetry`               |

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
```

### Adding an option

1. Add the template files under `src/fastapi_installer/templates/<group>/<value>/`.
   Files ending in `.jinja` are rendered with the project config; path segments may use
   `{{project_slug}}`.
2. Register the value in `LAYERS` in `src/fastapi_installer/registry.py`.
