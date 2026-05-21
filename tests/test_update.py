from __future__ import annotations

import os
import subprocess
from pathlib import Path

import copier


TEMPLATE_ROOT = Path(__file__).parent.parent
GIT_ENV = {**os.environ, "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@test.com", "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@test.com"}


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=GIT_ENV)


def test_update_from_v0_1_0(tmp_path: Path) -> None:
    # Generate from v0.1.0 — no CI, pre-commit, AGENTS.md, or README
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

    # copier update requires a git repo — v0.1.0 had no auto-init task yet
    _git(["init"], project)
    _git(["add", "."], project)
    _git(["commit", "-m", "init"], project)

    # Customize AGENTS.md and commit so the repo is clean before update
    (project / "AGENTS.md").write_text("my custom content")
    _git(["add", "."], project)
    _git(["commit", "-m", "customize"], project)

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

    # AGENTS.md should not have been overwritten
    assert (project / "AGENTS.md").read_text() == "my custom content"
