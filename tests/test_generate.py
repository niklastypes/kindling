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
    "full_stack": False,
    "enable_github_pm": False,
}


FULL_STACK_DATA = {
    **DEFAULT_DATA,
    "full_stack": True,
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


# --- Full-stack generation tests ---


@pytest.fixture
def generated_full_stack(tmp_path: Path) -> Path:
    copier.run_copy(
        str(TEMPLATE_ROOT),
        tmp_path / "test-project",
        data=FULL_STACK_DATA,
        unsafe=True,
        vcs_ref="HEAD",
    )
    return tmp_path / "test-project"


def test_full_stack_key_files_exist(generated_full_stack: Path) -> None:
    # Backend
    assert (generated_full_stack / "api" / "pyproject.toml").exists()
    assert (generated_full_stack / "api" / ".python-version").exists()
    assert (generated_full_stack / "api" / ".env.example").exists()
    assert (generated_full_stack / "api" / "project.json").exists()
    assert (
        generated_full_stack / "api" / "src" / "test_project" / "__init__.py"
    ).exists()
    assert (generated_full_stack / "api" / "src" / "test_project" / "py.typed").exists()
    assert (generated_full_stack / "api" / "src" / "test_project" / "app.py").exists()
    assert (
        generated_full_stack / "api" / "src" / "test_project" / "api" / "health.py"
    ).exists()
    assert (generated_full_stack / "api" / "tests" / "__init__.py").exists()
    assert (generated_full_stack / "api" / "tests" / "test_health.py").exists()
    # Frontend
    assert (generated_full_stack / "ui" / "package.json").exists()
    assert (generated_full_stack / "ui" / "vite.config.ts").exists()
    assert (generated_full_stack / "ui" / "index.html").exists()
    assert (generated_full_stack / "ui" / "tsconfig.json").exists()
    assert (generated_full_stack / "ui" / "tsconfig.app.json").exists()
    assert (generated_full_stack / "ui" / "src" / "main.ts").exists()
    assert (generated_full_stack / "ui" / "src" / "App.vue").exists()
    assert (generated_full_stack / "ui" / "src" / "styles" / "globals.css").exists()
    # Root monorepo
    assert (generated_full_stack / "nx.json").exists()
    assert (generated_full_stack / "package.json").exists()
    assert (generated_full_stack / "pnpm-workspace.yaml").exists()
    assert (generated_full_stack / "tsconfig.base.json").exists()
    # Shared (present in both modes)
    assert (generated_full_stack / ".gitignore").exists()
    assert (generated_full_stack / ".pre-commit-config.yaml").exists()
    assert (generated_full_stack / ".copier-answers.yml").exists()
    assert (generated_full_stack / "LICENSE").exists()
    assert (generated_full_stack / "README.md").exists()
    assert (generated_full_stack / "AGENTS.md").exists()
    assert (generated_full_stack / ".github" / "workflows" / "ci.yml").exists()
    assert (generated_full_stack / ".github" / "workflows" / "release.yml").exists()
    assert (generated_full_stack / "docs" / "full-stack.md").exists()
    assert (generated_full_stack / "docs" / "productionalize.md").exists()


def test_full_stack_excludes_root_python_files(generated_full_stack: Path) -> None:
    # Root src/ may exist as empty dir (copier creates dir skeleton before excluding
    # files), so check for actual files instead of the directory itself
    assert not (generated_full_stack / "src" / "test_project" / "__init__.py").exists()
    assert not (generated_full_stack / "tests" / "test_test_project.py").exists()
    assert not (generated_full_stack / "pyproject.toml").exists()
    assert not (generated_full_stack / ".python-version").exists()
    assert not (generated_full_stack / ".env.example").exists()


def test_full_stack_no_jinja_artifacts(generated_full_stack: Path) -> None:
    jinja_var = re.compile(r"(?<!\$){{")

    for path in generated_full_stack.rglob("*"):
        if not path.is_file():
            continue
        # Skip venvs and node_modules (installed packages may contain {{ }})
        rel = str(path.relative_to(generated_full_stack))
        if ".venv" in rel or "node_modules" in rel:
            continue
        if path.suffix not in {
            ".py",
            ".toml",
            ".yml",
            ".yaml",
            ".json",
            ".md",
            ".txt",
            ".ts",
            ".vue",
            ".css",
            ".html",
        }:
            continue
        content = path.read_text()
        # Skip App.vue which uses Vue's {{ }} template syntax
        if path.name == "App.vue":
            continue
        assert not jinja_var.search(content), f"Unrendered Jinja in {path}"
        assert "{%" not in content, f"Unrendered Jinja tag in {path}"


def test_full_stack_pyproject_has_fastapi_deps(generated_full_stack: Path) -> None:
    content = (generated_full_stack / "api" / "pyproject.toml").read_text()
    assert '"fastapi' in content
    assert '"uvicorn' in content
    assert '"anyio' in content
    assert '"httpx' in content


def test_full_stack_vite_proxy_config(generated_full_stack: Path) -> None:
    content = (generated_full_stack / "ui" / "vite.config.ts").read_text()
    assert "'/api'" in content
    assert "localhost:8080" in content


def test_full_stack_readme_mentions_pnpm(generated_full_stack: Path) -> None:
    content = (generated_full_stack / "README.md").read_text()
    assert "pnpm" in content


def test_full_stack_gitignore_has_node_entries(generated_full_stack: Path) -> None:
    content = (generated_full_stack / ".gitignore").read_text()
    assert "node_modules/" in content


def test_full_stack_pre_commit_has_api_directory(generated_full_stack: Path) -> None:
    content = (generated_full_stack / ".pre-commit-config.yaml").read_text()
    assert "uv --directory api run ty check" in content


def test_full_stack_ci_has_ui_job(generated_full_stack: Path) -> None:
    content = (generated_full_stack / ".github" / "workflows" / "ci.yml").read_text()
    assert "working-directory: api" in content
    assert "vue-tsc --noEmit" in content
    assert "vite build" in content


def test_full_stack_md_omits_setup_sections(generated_full_stack: Path) -> None:
    content = (generated_full_stack / "docs" / "full-stack.md").read_text()
    assert "## Monorepo layout" not in content
    assert "## Nx setup" not in content
    assert "## Frontend conventions" in content


# --- Python-only regression guards ---


def test_python_only_excludes_full_stack_files(generated: Path) -> None:
    # Copier may create empty dir skeletons, so check for actual files
    assert not (generated / "api" / "pyproject.toml").exists()
    assert not (generated / "ui" / "package.json").exists()
    assert not (generated / "nx.json").exists()
    assert not (generated / "package.json").exists()
    assert not (generated / "pnpm-workspace.yaml").exists()
    assert not (generated / "tsconfig.base.json").exists()


def test_python_only_readme_does_not_mention_pnpm(generated: Path) -> None:
    content = (generated / "README.md").read_text()
    assert "pnpm" not in content


def test_python_only_gitignore_no_node_entries(generated: Path) -> None:
    content = (generated / ".gitignore").read_text()
    assert "node_modules" not in content


def test_python_only_pre_commit_no_directory_flag(generated: Path) -> None:
    content = (generated / ".pre-commit-config.yaml").read_text()
    assert "--directory" not in content
    assert "uv run ty check src/ tests/" in content


def test_python_only_no_full_stack_md(generated: Path) -> None:
    assert not (generated / "docs" / "full-stack.md").exists()
