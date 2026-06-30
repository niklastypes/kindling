"""Hexagonal backend tests (full_stack=true, hexagonal default-on)."""

from __future__ import annotations

from pathlib import Path


def _pkg(root: Path) -> Path:
    return root / "api" / "src" / "test_project"


def test_hexagonal_layer_tree_exists(generated_full_stack: Path) -> None:
    pkg = _pkg(generated_full_stack)
    assert (pkg / "domain" / "health.py").exists()
    assert (pkg / "ports" / "inbound" / "__init__.py").exists()
    assert (pkg / "ports" / "outbound" / "__init__.py").exists()
    assert (pkg / "adapters" / "inbound" / "http" / "app.py").exists()
    assert (pkg / "adapters" / "inbound" / "http" / "routes" / "health.py").exists()
    assert (pkg / "adapters" / "outbound" / "__init__.py").exists()
    assert (pkg / "application" / "app.py").exists()
    assert (pkg / "application" / "config.py").exists()
    # The flat router package is not generated in hexagonal mode.
    assert not (pkg / "api" / "health.py").exists()


def test_hexagonal_app_is_composition_root_shim(generated_full_stack: Path) -> None:
    content = (_pkg(generated_full_stack) / "app.py").read_text()
    assert "from test_project.application.app import create_app" in content


def test_hexagonal_health_route_calls_domain(generated_full_stack: Path) -> None:
    route = (
        _pkg(generated_full_stack)
        / "adapters"
        / "inbound"
        / "http"
        / "routes"
        / "health.py"
    ).read_text()
    assert "from test_project.domain.health import check_health" in route


def test_hexagonal_import_linter_configured(generated_full_stack: Path) -> None:
    pyproject = (generated_full_stack / "api" / "pyproject.toml").read_text()
    assert "import-linter" in pyproject
    assert "[tool.importlinter]" in pyproject
    assert 'root_package = "test_project"' in pyproject


def test_hexagonal_enforcement_wired_into_precommit_and_ci(
    generated_full_stack: Path,
) -> None:
    pre_commit = (generated_full_stack / ".pre-commit-config.yaml").read_text()
    ci = (generated_full_stack / ".github" / "workflows" / "ci.yml").read_text()
    assert "lint-imports" in pre_commit
    assert "lint-imports" in ci


def test_hexagonal_docs_describe_layering(generated_full_stack: Path) -> None:
    docs = (generated_full_stack / "docs" / "architecture.md").read_text()
    assert "Backend layering (hexagonal)" in docs
    assert "adapters → application → ports → domain" in docs


def test_hexagonal_flat_opt_out(generated_flat_full_stack: Path) -> None:
    pkg = _pkg(generated_flat_full_stack)
    # Flat layout: the router package is present, the hex layers are not.
    # Copier may leave empty dir skeletons, so assert on files, not dirs.
    assert (pkg / "api" / "health.py").exists()
    assert not (pkg / "domain" / "health.py").exists()
    assert not (pkg / "ports" / "outbound" / "__init__.py").exists()
    assert not (pkg / "adapters" / "inbound" / "http" / "app.py").exists()
    assert not (pkg / "application" / "app.py").exists()
    # No enforcement config in the flat layout.
    pyproject = (generated_flat_full_stack / "api" / "pyproject.toml").read_text()
    assert "importlinter" not in pyproject
