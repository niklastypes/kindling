from __future__ import annotations

import re
import subprocess
from pathlib import Path

import copier
import pytest


TEMPLATE_ROOT = Path(__file__).parent.parent

DEFAULT_DATA = {
    "project_name": "test-project",
    "project_description": "A test project",
    "author_name": "Test Author",
    "github_username": "test-user",
    "python_version": "3.13",
}


@pytest.fixture
def generated(tmp_path: Path) -> Path:
    copier.run_copy(
        str(TEMPLATE_ROOT),
        tmp_path / "test-project",
        data=DEFAULT_DATA,
        unsafe=True,
        vcs_ref="HEAD",
    )
    return tmp_path / "test-project"


def test_key_files_exist(generated: Path) -> None:
    assert (generated / "pyproject.toml").exists()
    assert (generated / ".python-version").exists()
    assert (generated / ".gitignore").exists()
    assert (generated / ".env.example").exists()
    assert (generated / ".pre-commit-config.yaml").exists()
    assert (generated / ".copier-answers.yml").exists()
    assert (generated / ".release-please-manifest.json").exists()
    assert (generated / "LICENSE").exists()
    assert (generated / "renovate.json").exists()
    assert (generated / "release-please-config.json").exists()
    assert (generated / "AGENTS.md").exists()
    assert (generated / "README.md").exists()
    assert (generated / ".github" / "workflows" / "ci.yml").exists()
    assert (generated / ".github" / "workflows" / "release.yml").exists()
    assert (generated / "src" / "test_project" / "__init__.py").exists()
    assert (generated / "src" / "test_project" / "py.typed").exists()
    assert (generated / ".gitattributes").exists()
    assert (generated / "tests" / "__init__.py").exists()
    assert (generated / "tests" / "test_test_project.py").exists()
    assert (generated / "docs" / "full-stack.md").exists()
    assert (generated / "docs" / "productionalize.md").exists()


def test_no_jinja_artifacts(generated: Path) -> None:
    # Match {{ not preceded by $ (GitHub Actions uses ${{ }}, Jinja uses {{ }})
    jinja_var = re.compile(r"(?<!\$){{")

    for path in generated.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".toml", ".yml", ".yaml", ".json", ".md", ".txt"}:
            continue
        content = path.read_text()
        assert not jinja_var.search(content), f"Unrendered Jinja in {path}"
        assert "{%" not in content, f"Unrendered Jinja tag in {path}"


def test_pyproject_rendered_correctly(generated: Path) -> None:
    content = (generated / "pyproject.toml").read_text()
    assert 'name = "test-project"' in content
    assert 'packages = ["src/test_project"]' in content
    assert "https://github.com/test-user/test-project" in content
    assert "{{" not in content


def test_initial_commit_is_tagged_v0_1_0(generated: Path) -> None:
    result = subprocess.run(
        ["git", "tag", "--list"],
        cwd=generated,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "v0.1.0" in result.stdout.split()


def test_hyphenated_name_uses_underscores(tmp_path: Path) -> None:
    copier.run_copy(
        str(TEMPLATE_ROOT),
        tmp_path / "my-cool-project",
        data={**DEFAULT_DATA, "project_name": "my-cool-project"},
        unsafe=True,
        vcs_ref="HEAD",
    )
    project = tmp_path / "my-cool-project"
    assert (project / "src" / "my_cool_project" / "__init__.py").exists()
    assert (project / "tests" / "test_my_cool_project.py").exists()
    content = (project / "pyproject.toml").read_text()
    assert 'name = "my-cool-project"' in content
    assert 'packages = ["src/my_cool_project"]' in content


KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


@pytest.mark.parametrize(
    "name",
    [
        "My-Project",
        "my project",
        "my_project",
        "-my-project",
        "my-project-",
        "my--project",
        "123-project",
        "my@project",
    ],
)
def test_project_name_validator_rejects_invalid(name: str) -> None:
    assert not KEBAB_CASE_RE.match(name), f"Expected {name!r} to be rejected"


@pytest.mark.parametrize(
    "name",
    [
        "a",
        "a1",
        "my-project",
        "my-cool-project",
        "foo123",
    ],
)
def test_project_name_validator_accepts_valid(name: str) -> None:
    assert KEBAB_CASE_RE.match(name), f"Expected {name!r} to be accepted"
