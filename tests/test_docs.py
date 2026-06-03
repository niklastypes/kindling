"""Tests for docs restructuring: CLAUDE.md, AGENTS.md, architecture, ADR."""

from __future__ import annotations

from pathlib import Path


def test_claude_md_exists(generated: Path) -> None:
    assert (generated / "CLAUDE.md").exists()
    content = (generated / "CLAUDE.md").read_text()
    assert "test-project" in content
    assert "A test project" in content


def test_agents_md_is_redirect(generated: Path) -> None:
    content = (generated / "AGENTS.md").read_text()
    assert "CLAUDE.md" in content
    assert len(content.strip().splitlines()) <= 3


def test_docs_scaffolding_exists(generated: Path) -> None:
    assert (generated / "docs" / "architecture.md").exists()
    assert (generated / "docs" / "decisions" / "0000-template.md").exists()
    assert (generated / "docs" / "designs" / ".gitkeep").exists()
    assert (generated / "docs" / "productionalize.md").exists()


def test_claude_md_has_growing_beyond_pointers(generated: Path) -> None:
    content = (generated / "CLAUDE.md").read_text()
    assert "copier update" in content
    assert "full_stack=true" in content
    assert "enable_github_pm=true" in content
    assert "productionalize.md" in content


def test_claude_md_no_pm_lifecycle(generated: Path) -> None:
    content = (generated / "CLAUDE.md").read_text()
    assert "Issue Lifecycle" not in content
    assert "In Progress" not in content
    assert "Fixes #N" not in content


def test_full_stack_claude_md_no_full_stack_pointer(
    generated_full_stack: Path,
) -> None:
    content = (generated_full_stack / "CLAUDE.md").read_text()
    assert "full_stack=true" not in content
    assert "enable_github_pm=true" in content


def test_full_stack_docs_scaffolding(generated_full_stack: Path) -> None:
    assert (generated_full_stack / "docs" / "architecture.md").exists()
    assert (generated_full_stack / "docs" / "decisions" / "0000-template.md").exists()
    assert (generated_full_stack / "docs" / "designs" / ".gitkeep").exists()
    content = (generated_full_stack / "docs" / "architecture.md").read_text()
    assert "api/" in content
    assert "ui/" in content
