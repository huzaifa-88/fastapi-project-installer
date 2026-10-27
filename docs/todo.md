# TODO

Work planned for fastapi-installer, roughly in priority order. Tick items off as they land.

## 1. Add features after a project is created
Let users add an option they skipped earlier, e.g. a project created with `--infra none`
gets Docker later, or one created without a database gets one.

```bash
fastapi-installer add docker        # Dockerfile + docker-compose.yml
fastapi-installer add alembic       # alembic.ini + migrations/, removes create_tables on startup
fastapi-installer add db            # database + ORM layers (needs the "no database" option, see §3)
fastapi-installer add auth          # JWT auth
fastapi-installer add tests         # pytest setup
```

- [ ] Record the user's choices in the generated project (e.g. `[tool.fastapi-installer]` in
      `pyproject.toml`) so `add` knows what is already there
- [ ] `add <option>` renders only the new layer into the existing project
- [ ] Update shared files the new layer depends on: dependencies (`uv add ...`),
      `.env.example`, `README.md`, `main.py` / `deps.py` wiring
- [ ] Never silently overwrite a file the user edited: detect conflicts, show a diff, and let the
      user skip or apply (`--force` to overwrite)
- [ ] Refuse cleanly when run outside a generated project, or when the option is already present
- [ ] `--dry-run` that lists the files that would be created or changed
- [ ] Tests: add each option to a project generated without it; the result must match a project
      generated with it from the start, and must still pass ruff

## 2. Remaining v1 milestones
- [ ] **JWT auth (milestone 5):** password hashing, `/auth/register`, `/auth/login`, `/users/me`,
      `get_current_user` dependency, `hashed_password` column + migration; wire the `auth/jwt` layer
- [ ] **Tests in the generated project (milestone 6):** unit tests for services with an in-memory
      fake repository; API integration tests against Postgres; edge cases (invalid input,
      duplicates, not found, DB down), not only happy paths; pytest + httpx in dev dependencies
- [ ] **Post-generation steps (milestone 7):** run `uv sync` (`--no-install` to skip), `git init`
      + first commit (`--no-git` to skip), print next steps; creates `uv.lock` so Docker builds are
      reproducible
- [ ] **Publish (milestone 8):** final READMEs, CI (GitHub Actions running `make check`), publish
      to TestPyPI then PyPI, versioning + changelog

## 3. Options marked "coming soon"
- [ ] Architecture: `monolithic`
- [ ] Architecture: `event-driven`
- [ ] Database: `mysql`
- [ ] Database / ORM: `none` (project without a database; needs a template without the
      `users` DB feature)
- [ ] ORM: `sqlmodel`
- [ ] Package manager: `poetry`
- [ ] API style: `graphql`

Each new value: add its template layer, register it in `registry.py`, follow the layer contract
in `CLAUDE.md`, and add tests.

## 4. Other ideas
- [ ] `fastapi-installer add feature <name>`: scaffold a new feature across all layers (entity,
      repository, service, ORM model, router, schemas, migration)
- [ ] `fastapi-installer update`: bring an existing project up to a newer template version
- [ ] Shorter command alias (e.g. `fi new`)

## 5. Known issues
- [ ] With `--migrations none`, only new tables are created on startup; changes to existing
      tables are not applied. Documented in the generated README; `add alembic` (§1) is the fix
- [ ] When the database is down, API requests return 500; map connection errors to 503
- [ ] Unhandled errors are logged twice (the app's handler and the server); keep one
- [ ] Generator tests check generated code statically (render, compile, ruff); add a CI job that
      runs a generated project end to end against Postgres
- [x] "Commits must be verified" also means signed commits (SSH signing, see CLAUDE.md)
