"""Command-line entry point: ``fastapi-installer new <name>``."""

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console

from fastapi_installer import __version__
from fastapi_installer.config import (
    ORM,
    APIStyle,
    Architecture,
    Auth,
    Database,
    Infra,
    Migrations,
    PackageManager,
    ProjectConfig,
    Testing,
)
from fastapi_installer.generator import TargetNotEmptyError, generate
from fastapi_installer.prompts import ask_missing
from fastapi_installer.registry import UnsupportedOptionError

app = typer.Typer(help="Generate production-ready FastAPI projects.", no_args_is_help=True)
console = Console()


def _version(value: bool) -> None:
    if value:
        console.print(f"fastapi-installer {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option("--version", callback=_version, is_eager=True, help="Show version.")
    ] = False,
) -> None:
    pass


@app.command()
def new(
    name: Annotated[str, typer.Argument(help="Project name, e.g. my-app.")],
    arch: Annotated[Architecture | None, typer.Option("--arch")] = None,
    db: Annotated[Database | None, typer.Option("--db")] = None,
    orm: Annotated[ORM | None, typer.Option("--orm")] = None,
    migrations: Annotated[Migrations | None, typer.Option("--migrations")] = None,
    api: Annotated[APIStyle | None, typer.Option("--api")] = None,
    auth: Annotated[Auth | None, typer.Option("--auth")] = None,
    testing: Annotated[Testing | None, typer.Option("--testing")] = None,
    infra: Annotated[Infra | None, typer.Option("--infra")] = None,
    pm: Annotated[PackageManager | None, typer.Option("--pm", help="Package manager.")] = None,
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Target directory (default: ./<name>).")
    ] = None,
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Use defaults for anything not passed as a flag.")
    ] = False,
    force: Annotated[bool, typer.Option(help="Write into a non-empty directory.")] = False,
) -> None:
    """Create a new FastAPI project."""
    preset = {
        "architecture": arch,
        "database": db,
        "orm": orm,
        "migrations": migrations,
        "api_style": api,
        "auth": auth,
        "testing": testing,
        "infra": infra,
        "package_manager": pm,
    }
    if yes:
        options = {key: value for key, value in preset.items() if value is not None}
    else:
        try:
            options = ask_missing(preset)
        except KeyboardInterrupt:
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit(1) from None

    try:
        config = ProjectConfig(project_name=name, **options)
    except ValidationError as exc:
        console.print(f"[red]Invalid project name:[/red] {exc.errors()[0]['msg']}")
        raise typer.Exit(1) from None

    target = (output or Path.cwd() / name).resolve()
    try:
        files = generate(config, target, force=force)
    except (UnsupportedOptionError, TargetNotEmptyError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from None

    console.print(f"[green]Created[/green] {config.project_name} ({len(files)} files) at {target}")
