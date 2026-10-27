import pytest
from pydantic import ValidationError

from fastapi_installer.config import Database, ProjectConfig, slugify


@pytest.mark.parametrize(
    ("name", "slug"),
    [("myapp", "myapp"), ("my-app", "my_app"), ("My_App2", "my_app2")],
)
def test_slugify(name, slug):
    assert slugify(name) == slug
    assert ProjectConfig(project_name=name).project_slug == slug


@pytest.mark.parametrize("name", ["", "1app", "my app", "app!", "class", "-app"])
def test_invalid_names_rejected(name):
    with pytest.raises(ValidationError):
        ProjectConfig(project_name=name)


def test_defaults_are_v1_stack():
    config = ProjectConfig(project_name="demo")
    assert config.database is Database.POSTGRES
    assert config.model_dump(mode="json")["architecture"] == "clean"
