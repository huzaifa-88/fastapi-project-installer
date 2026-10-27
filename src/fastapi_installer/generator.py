"""Render template layers into a new project directory.

Each layer is a directory under ``templates/``. Files ending in ``.jinja`` are rendered
with the project config (the suffix is dropped); everything else is copied as-is.
Path segments may contain placeholders such as ``{{project_slug}}``.
"""

import shutil
from pathlib import Path

from jinja2 import Environment, StrictUndefined

from fastapi_installer.config import ProjectConfig
from fastapi_installer.registry import resolve_layers

TEMPLATES_DIR = Path(__file__).parent / "templates"
TEMPLATE_SUFFIX = ".jinja"
IGNORED_NAMES = {".gitkeep", "__pycache__", ".DS_Store"}


class TargetNotEmptyError(FileExistsError):
    pass


def _env() -> Environment:
    return Environment(
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
    )


def _render_path(env: Environment, relative: Path, context: dict) -> Path:
    parts = [
        env.from_string(part).render(context) if "{{" in part else part for part in relative.parts
    ]
    rendered = Path(*parts)
    if rendered.suffix == TEMPLATE_SUFFIX:
        rendered = rendered.with_suffix("")
    return rendered


def _iter_files(layer_dir: Path):
    for path in sorted(layer_dir.rglob("*")):
        if path.is_file() and not IGNORED_NAMES.intersection(path.parts):
            yield path


def generate(config: ProjectConfig, target: Path, *, force: bool = False) -> list[Path]:
    """Generate the project into ``target``. Returns the written paths, relative to ``target``."""
    if target.exists() and any(target.iterdir()) and not force:
        raise TargetNotEmptyError(f"Directory '{target}' already exists and is not empty.")

    env = _env()
    context = config.model_dump(mode="json")
    written: dict[Path, None] = {}

    for layer in resolve_layers(config):
        layer_dir = TEMPLATES_DIR / layer
        if not layer_dir.is_dir():
            raise FileNotFoundError(f"Template layer '{layer}' is missing at {layer_dir}")

        for source in _iter_files(layer_dir):
            relative = _render_path(env, source.relative_to(layer_dir), context)
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix == TEMPLATE_SUFFIX:
                content = env.from_string(source.read_text()).render(context)
                destination.write_text(content)
            else:
                shutil.copyfile(source, destination)
            written[relative] = None

    return list(written)
