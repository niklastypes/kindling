"""Full-stack generation tests (full_stack=true)."""

from __future__ import annotations

import re
from pathlib import Path


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
    # Shared
    assert (generated_full_stack / ".gitignore").exists()
    assert (generated_full_stack / ".pre-commit-config.yaml").exists()
    assert (generated_full_stack / "CLAUDE.md").exists()
    assert (generated_full_stack / "AGENTS.md").exists()
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
