"""Which option values are supported, and which template layer each one adds.

To support a new option value, add its template directory under ``templates/``
and register it in ``LAYERS``. Values missing from ``LAYERS`` are "coming soon".
"""

from enum import StrEnum

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

BASE_LAYER = "base"

# Option value -> template layer (relative to templates/). ``None`` means supported, no files.
LAYERS: dict[StrEnum, str | None] = {
    Architecture.CLEAN: "architecture/clean",
    Database.POSTGRES: "database/postgres",
    ORM.SQLALCHEMY: "orm/sqlalchemy",
    Migrations.ALEMBIC: "migrations/alembic",
    Migrations.NONE: None,
    APIStyle.REST: None,
    Auth.JWT: "auth/jwt",
    Auth.NONE: None,
    Testing.PYTEST: "testing/pytest",
    Testing.NONE: None,
    Infra.DOCKER_COMPOSE: "infra/docker_compose",
    Infra.NONE: None,
    PackageManager.UV: "package_manager/uv",
}

# Config fields in the order their layers are applied. Later layers overwrite earlier files.
OPTION_FIELDS: tuple[str, ...] = (
    "architecture",
    "database",
    "orm",
    "migrations",
    "api_style",
    "auth",
    "testing",
    "infra",
    "package_manager",
)


class UnsupportedOptionError(ValueError):
    pass


def is_supported(value: StrEnum) -> bool:
    return value in LAYERS


def ensure_supported(config: ProjectConfig) -> None:
    unsupported = [
        f"{field}={getattr(config, field).value}"
        for field in OPTION_FIELDS
        if not is_supported(getattr(config, field))
    ]
    if unsupported:
        raise UnsupportedOptionError("Not supported yet (coming soon): " + ", ".join(unsupported))


def resolve_layers(config: ProjectConfig) -> list[str]:
    """Return the ordered template layers for ``config``, starting with the base layer."""
    ensure_supported(config)
    layers = [BASE_LAYER]
    for field in OPTION_FIELDS:
        layer = LAYERS[getattr(config, field)]
        if layer is not None:
            layers.append(layer)
    return layers
