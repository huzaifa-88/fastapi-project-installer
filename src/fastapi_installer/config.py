"""Project configuration: every option a user can choose, plus the validated config model."""

import keyword
import re
from enum import StrEnum

from pydantic import BaseModel, computed_field, field_validator


class Architecture(StrEnum):
    CLEAN = "clean"
    MONOLITHIC = "monolithic"
    EVENT_DRIVEN = "event-driven"


class Database(StrEnum):
    POSTGRES = "postgres"
    MYSQL = "mysql"


class ORM(StrEnum):
    SQLALCHEMY = "sqlalchemy"
    SQLMODEL = "sqlmodel"


class PackageManager(StrEnum):
    UV = "uv"
    POETRY = "poetry"


class APIStyle(StrEnum):
    REST = "rest"
    GRAPHQL = "graphql"


class Auth(StrEnum):
    JWT = "jwt"
    NONE = "none"


class Testing(StrEnum):
    PYTEST = "pytest"
    NONE = "none"


class Infra(StrEnum):
    DOCKER_COMPOSE = "docker-compose"
    NONE = "none"


class Migrations(StrEnum):
    ALEMBIC = "alembic"
    NONE = "none"


_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def slugify(name: str) -> str:
    """Turn a project name into a valid Python package name: ``my-app`` -> ``my_app``."""
    return name.strip().lower().replace("-", "_")


class ProjectConfig(BaseModel):
    project_name: str
    architecture: Architecture = Architecture.CLEAN
    database: Database = Database.POSTGRES
    orm: ORM = ORM.SQLALCHEMY
    package_manager: PackageManager = PackageManager.UV
    api_style: APIStyle = APIStyle.REST
    auth: Auth = Auth.JWT
    testing: Testing = Testing.PYTEST
    infra: Infra = Infra.DOCKER_COMPOSE
    migrations: Migrations = Migrations.ALEMBIC
    python_version: str = "3.12"

    @field_validator("project_name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        value = value.strip()
        if not _NAME_RE.match(value):
            raise ValueError(
                "must start with a letter and contain only letters, digits, '-' or '_'"
            )
        if keyword.iskeyword(slugify(value)):
            raise ValueError(f"'{value}' is a reserved Python keyword")
        return value

    @computed_field
    @property
    def project_slug(self) -> str:
        return slugify(self.project_name)
