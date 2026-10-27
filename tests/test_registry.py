import pytest

from fastapi_installer.config import Architecture, Database, ProjectConfig
from fastapi_installer.generator import TEMPLATES_DIR
from fastapi_installer.registry import (
    BASE_LAYER,
    LAYERS,
    UnsupportedOptionError,
    resolve_layers,
)


def test_resolve_layers_order():
    layers = resolve_layers(ProjectConfig(project_name="demo"))
    assert layers == [
        BASE_LAYER,
        "architecture/clean",
        "database/postgres",
        "orm/sqlalchemy",
        "migrations/alembic",
        "auth/jwt",
        "testing/pytest",
        "infra/docker_compose",
        "package_manager/uv",
    ]


@pytest.mark.parametrize(
    "overrides",
    [{"database": Database.MYSQL}, {"architecture": Architecture.EVENT_DRIVEN}],
)
def test_unsupported_options_rejected(overrides):
    config = ProjectConfig(project_name="demo", **overrides)
    with pytest.raises(UnsupportedOptionError, match="coming soon"):
        resolve_layers(config)


def test_every_registered_layer_exists():
    for layer in [BASE_LAYER, *filter(None, LAYERS.values())]:
        assert (TEMPLATES_DIR / layer).is_dir(), layer
