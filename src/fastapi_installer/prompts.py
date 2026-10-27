"""Interactive questions for any option not already set by a CLI flag."""

from enum import StrEnum

import questionary

from fastapi_installer.config import ProjectConfig
from fastapi_installer.registry import OPTION_FIELDS, is_supported

LABELS: dict[str, str] = {
    "architecture": "Architecture",
    "database": "Database",
    "orm": "ORM",
    "migrations": "Migrations",
    "api_style": "API style",
    "auth": "Authentication",
    "testing": "Testing",
    "infra": "Infrastructure",
    "package_manager": "Package manager",
}


def _ask(field: str, enum_type: type[StrEnum], default: StrEnum) -> StrEnum:
    choices = [
        questionary.Choice(
            title="none (skip)" if member.value == "none" else member.value,
            value=member,
            disabled=None if is_supported(member) else "coming soon",
        )
        for member in enum_type
    ]
    answer = questionary.select(LABELS[field], choices=choices, default=default).ask()
    if answer is None:  # Ctrl+C
        raise KeyboardInterrupt
    return answer


def ask_missing(preset: dict[str, StrEnum | None]) -> dict[str, StrEnum]:
    """Prompt for every option whose value in ``preset`` is None."""
    answers: dict[str, StrEnum] = {}
    for field in OPTION_FIELDS:
        value = preset.get(field)
        if value is None:
            info = ProjectConfig.model_fields[field]
            value = _ask(field, info.annotation, info.default)
        answers[field] = value
    return answers
