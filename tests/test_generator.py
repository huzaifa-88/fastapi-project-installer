import compileall
import itertools
import subprocess
import sys

import pytest
from typer.testing import CliRunner

from fastapi_installer.cli import app
from fastapi_installer.config import ProjectConfig
from fastapi_installer.generator import TargetNotEmptyError, generate
from fastapi_installer.registry import OPTION_FIELDS, is_supported


def _supported_combinations() -> list[dict]:
    choices = [
        [value for value in ProjectConfig.model_fields[field].annotation if is_supported(value)]
        for field in OPTION_FIELDS
    ]
    return [dict(zip(OPTION_FIELDS, combo, strict=True)) for combo in itertools.product(*choices)]


COMBINATIONS = _supported_combinations()


@pytest.fixture
def project(tmp_path):
    target = tmp_path / "my-app"
    files = generate(ProjectConfig(project_name="my-app"), target)
    return target, files


def test_generates_expected_tree(project):
    target, files = project
    expected = {
        "pyproject.toml",
        "README.md",
        ".gitignore",
        ".env.example",
        ".python-version",
        "src/my_app/__init__.py",
        "src/my_app/main.py",
        "src/my_app/core/config.py",
        "src/my_app/core/database.py",
        "src/my_app/domain/users/entities.py",
        "src/my_app/domain/users/repository.py",
        "src/my_app/application/users/service.py",
        "src/my_app/infrastructure/db/session.py",
        "src/my_app/infrastructure/users/repository.py",
        "src/my_app/presentation/api/deps.py",
        "src/my_app/presentation/api/health.py",
        "src/my_app/presentation/api/v1/users.py",
        "alembic.ini",
        "migrations/env.py",
        "migrations/script.py.mako",
        "migrations/versions/0001_create_users_table.py",
        "docker-compose.yml",
        "Dockerfile",
        ".dockerignore",
    }
    assert expected <= {str(path) for path in files}
    assert all((target / path).is_file() for path in files)
    assert not any(path.name == ".gitkeep" for path in target.rglob("*"))


@pytest.fixture(params=COMBINATIONS, ids=lambda c: "-".join(str(v) for v in c.values()))
def any_project(request, tmp_path):
    """A project for every combination of supported options."""
    target = tmp_path / "my-app"
    generate(ProjectConfig(project_name="my-app", **request.param), target)
    return target


def test_templates_fully_rendered(any_project):
    target = any_project
    for path in target.rglob("*"):
        if path.is_file():
            assert "{{" not in path.name
            assert ".jinja" not in path.name
            assert "{{" not in path.read_text(), path


def test_python_files_compile(any_project):
    target = any_project
    assert compileall.compile_dir(target, quiet=1)


@pytest.mark.parametrize("command", [["check"], ["format", "--check"]])
def test_generated_project_passes_ruff(any_project, command):
    target = any_project
    result = subprocess.run(
        [sys.executable, "-m", "ruff", *command, "--config", str(target / "pyproject.toml")],
        cwd=target,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_infra_none_skips_docker(tmp_path):
    target = tmp_path / "app"
    generate(ProjectConfig(project_name="app", infra="none"), target)
    for name in ("Dockerfile", "docker-compose.yml", ".dockerignore"):
        assert not (target / name).exists(), name
    assert "docker compose" not in (target / "README.md").read_text()


def test_migrations_none_skips_alembic_and_creates_tables_on_startup(tmp_path):
    target = tmp_path / "app"
    generate(ProjectConfig(project_name="app", migrations="none"), target)
    assert not (target / "alembic.ini").exists()
    assert not (target / "migrations").exists()
    assert "alembic" not in (target / "pyproject.toml").read_text()
    assert "alembic" not in (target / "docker-compose.yml").read_text()
    assert "alembic" not in (target / "README.md").read_text()
    assert (
        "async def create_tables" in (target / "src/app/infrastructure/db/session.py").read_text()
    )
    assert "await create_tables()" in (target / "src/app/main.py").read_text()


def test_alembic_project_does_not_create_tables_on_startup(project):
    target, _ = project
    assert "create_tables" not in (target / "src/my_app/main.py").read_text()
    assert "alembic upgrade head" in (target / "docker-compose.yml").read_text()


def test_refuses_non_empty_target(project):
    target, _ = project
    config = ProjectConfig(project_name="my-app")
    with pytest.raises(TargetNotEmptyError):
        generate(config, target)
    generate(config, target, force=True)


def test_cli_non_interactive(tmp_path):
    result = CliRunner().invoke(app, ["new", "demo", "-y", "-o", str(tmp_path / "demo")])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "demo" / "src" / "demo" / "main.py").is_file()


def test_cli_rejects_unsupported_option(tmp_path):
    result = CliRunner().invoke(
        app, ["new", "demo", "-y", "--db", "mysql", "-o", str(tmp_path / "demo")]
    )
    assert result.exit_code == 1
    assert "coming soon" in result.output
    assert not (tmp_path / "demo").exists()


@pytest.mark.parametrize("flag", ["--infra", "--migrations", "--auth", "--testing"])
def test_cli_accepts_none(tmp_path, flag):
    result = CliRunner().invoke(app, ["new", "demo", "-y", flag, "none", "-o", str(tmp_path / "d")])
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("value", ["None", "", "docker", "no"])
def test_cli_rejects_unknown_infra_value(tmp_path, value):
    result = CliRunner().invoke(
        app, ["new", "demo", "-y", "--infra", value, "-o", str(tmp_path / "d")]
    )
    assert result.exit_code != 0
    assert not (tmp_path / "d").exists()
