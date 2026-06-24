"""Tests for copier update upgrade paths."""

from __future__ import annotations

from pathlib import Path

import copier
from conftest import TEMPLATE_ROOT, git


def test_update_from_v0_1_0(tmp_path: Path) -> None:
    """Projects generated from v0.1.0 get new files on update to HEAD."""
    copier.run_copy(
        str(TEMPLATE_ROOT),
        tmp_path / "test-project",
        data={
            "project_name": "test-project",
            "project_description": "A test project",
            "author_name": "Test Author",
            "python_version": "3.13",
        },
        vcs_ref="v0.1.0",
        unsafe=True,
    )
    project = tmp_path / "test-project"
    assert not (project / ".pre-commit-config.yaml").exists()
    assert not (project / "AGENTS.md").exists()
    assert not (project / "README.md").exists()

    # copier update requires a git repo (v0.1.0 had no auto-init task yet)
    git(["init"], project)
    git(["add", "."], project)
    git(["commit", "-m", "init"], project)

    # Customize AGENTS.md and commit so the repo is clean before update
    (project / "AGENTS.md").write_text("my custom content")
    git(["add", "."], project)
    git(["commit", "-m", "customize"], project)

    # Update to HEAD
    copier.run_update(
        str(project),
        data={"github_username": "test-user"},
        vcs_ref="HEAD",
        unsafe=True,
        defaults=True,
        overwrite=True,
    )

    assert (project / ".pre-commit-config.yaml").exists()
    assert (project / ".github" / "workflows" / "ci.yml").exists()
    assert (project / "README.md").exists()

    # AGENTS.md should not have been overwritten (_skip_if_exists)
    assert (project / "AGENTS.md").read_text() == "my custom content"

    # Ubiquitous-language guide shipped with the BEGIN/END markers so
    # `copier update` can splice the user's Glossary entries back in.
    ul = (project / "docs" / "ubiquitous-language.md").read_text()
    assert "<!-- KINDLING:GLOSSARY:BEGIN -->" in ul
    assert "<!-- KINDLING:GLOSSARY:END -->" in ul
    assert "## Glossary" in ul


def test_update_from_v0_1_0_gains_new_docs(tmp_path: Path) -> None:
    """Projects from v0.1.0 get CLAUDE.md, architecture.md, and ADR on update."""
    copier.run_copy(
        str(TEMPLATE_ROOT),
        tmp_path / "test-project",
        data={
            "project_name": "test-project",
            "project_description": "A test project",
            "author_name": "Test Author",
            "python_version": "3.13",
        },
        vcs_ref="v0.1.0",
        unsafe=True,
    )
    project = tmp_path / "test-project"

    # v0.1.0 should not have these files
    assert not (project / "CLAUDE.md").exists()
    assert not (project / "docs" / "architecture.md").exists()
    assert not (project / "docs" / "decisions").exists()

    git(["init"], project)
    git(["add", "."], project)
    git(["commit", "-m", "init"], project)

    # Update to HEAD
    copier.run_update(
        str(project),
        data={"github_username": "test-user"},
        vcs_ref="HEAD",
        unsafe=True,
        defaults=True,
        overwrite=True,
    )

    # New docs files should appear
    assert (project / "CLAUDE.md").exists()
    assert (project / "docs" / "architecture.md").exists()
    assert (project / "docs" / "decisions" / "0000-template.md").exists()
    assert (project / "docs" / "designs" / ".gitkeep").exists()


def test_update_gitignore_propagates_and_preserves(tmp_path: Path) -> None:
    """.gitignore is merged (not frozen) on update: new template ignores land
    while user-added lines survive."""
    copier.run_copy(
        str(TEMPLATE_ROOT),
        tmp_path / "test-project",
        data={
            "project_name": "test-project",
            "project_description": "A test project",
            "author_name": "Test Author",
            "python_version": "3.13",
        },
        vcs_ref="v0.1.0",
        unsafe=True,
    )
    project = tmp_path / "test-project"

    # v0.1.0 predates the .claude/settings.local.json ignore.
    assert ".claude/settings.local.json" not in (project / ".gitignore").read_text()

    git(["init"], project)
    git(["add", "."], project)
    git(["commit", "-m", "init"], project)

    # User appends a project-specific ignore and commits.
    gitignore = project / ".gitignore"
    gitignore.write_text(gitignore.read_text() + "\n# Custom\nlocal-scratch/\n")
    git(["add", "."], project)
    git(["commit", "-m", "customize-gitignore"], project)

    copier.run_update(
        str(project),
        data={"github_username": "test-user"},
        vcs_ref="HEAD",
        unsafe=True,
        defaults=True,
        overwrite=True,
    )

    merged = (project / ".gitignore").read_text()
    # New template ignore propagated...
    assert ".claude/settings.local.json" in merged
    # ...and the user's line survived the merge.
    assert "local-scratch/" in merged


def test_update_skip_if_exists_protects_claude_md(tmp_path: Path) -> None:
    """CLAUDE.md is not overwritten on copier update if user customized it."""
    copier.run_copy(
        str(TEMPLATE_ROOT),
        tmp_path / "test-project",
        data={
            "project_name": "test-project",
            "project_description": "A test project",
            "author_name": "Test Author",
            "python_version": "3.13",
        },
        vcs_ref="v0.1.0",
        unsafe=True,
    )
    project = tmp_path / "test-project"

    git(["init"], project)
    git(["add", "."], project)
    git(["commit", "-m", "init"], project)

    # Create and customize CLAUDE.md
    (project / "CLAUDE.md").write_text("my custom claude instructions")
    git(["add", "."], project)
    git(["commit", "-m", "add-claude-md"], project)

    # Update to HEAD
    copier.run_update(
        str(project),
        data={"github_username": "test-user"},
        vcs_ref="HEAD",
        unsafe=True,
        defaults=True,
        overwrite=True,
    )

    # CLAUDE.md should not have been overwritten
    assert (project / "CLAUDE.md").read_text() == "my custom claude instructions"
