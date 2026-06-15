"""Core generation tests: file existence, rendering, validators, git init."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import copier
import pytest
from conftest import DEFAULT_DATA, TEMPLATE_ROOT


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
    assert (generated / "CLAUDE.md").exists()
    assert (generated / "README.md").exists()
    assert (generated / ".github" / "workflows" / "ci.yml").exists()
    assert (generated / ".github" / "workflows" / "release.yml").exists()
    assert (generated / "src" / "test_project" / "__init__.py").exists()
    assert (generated / "src" / "test_project" / "py.typed").exists()
    assert (generated / ".gitattributes").exists()
    assert (generated / "tests" / "__init__.py").exists()
    assert (generated / "tests" / "test_test_project.py").exists()
    assert (generated / "docs" / "productionalize.md").exists()
    assert (generated / "docs" / "architecture.md").exists()
    assert (generated / "docs" / "decisions" / "0000-template.md").exists()
    assert (generated / "docs" / "designs" / ".gitkeep").exists()


def test_no_jinja_artifacts(generated: Path) -> None:
    jinja_var = re.compile(r"(?<!\$){{")

    for path in generated.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {
            ".py",
            ".toml",
            ".yml",
            ".yaml",
            ".json",
            ".md",
            ".txt",
        }:
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


# --- Python-only regression guards ---


def test_python_only_excludes_full_stack_files(generated: Path) -> None:
    assert not (generated / "api" / "pyproject.toml").exists()
    assert not (generated / "ui" / "package.json").exists()
    assert not (generated / "nx.json").exists()
    assert not (generated / "package.json").exists()
    assert not (generated / "pnpm-workspace.yaml").exists()
    assert not (generated / "tsconfig.base.json").exists()


def test_python_only_no_full_stack_md(generated: Path) -> None:
    assert not (generated / "docs" / "full-stack.md").exists()


def test_python_only_no_pm_files(generated: Path) -> None:
    assert not (generated / ".github" / "ISSUE_TEMPLATE" / "epic.yml").exists()
    assert not (generated / ".github" / "pull_request_template.md").exists()
    assert not (generated / "scripts" / "bootstrap-pm.sh").exists()
    assert not (generated / "docs" / "project-management.md").exists()


def test_python_only_readme_does_not_mention_pnpm(generated: Path) -> None:
    content = (generated / "README.md").read_text()
    assert "pnpm" not in content


def test_python_only_gitignore_no_node_entries(generated: Path) -> None:
    content = (generated / ".gitignore").read_text()
    assert "node_modules" not in content


def test_gitignore_excludes_claude_local_settings(generated: Path) -> None:
    content = (generated / ".gitignore").read_text()
    assert ".claude/settings.local.json" in content


def test_python_only_pre_commit_no_directory_flag(generated: Path) -> None:
    content = (generated / ".pre-commit-config.yaml").read_text()
    assert "--directory" not in content
    assert "uv run ty check src/ tests/" in content
