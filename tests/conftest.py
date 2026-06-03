from __future__ import annotations

import os
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

PM_DATA = {
    **DEFAULT_DATA,
    "enable_github_pm": True,
}

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@test.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@test.com",
}


def git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, env=GIT_ENV
    )


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


@pytest.fixture
def generated_pm(tmp_path: Path) -> Path:
    copier.run_copy(
        str(TEMPLATE_ROOT),
        tmp_path / "test-project",
        data=PM_DATA,
        unsafe=True,
        vcs_ref="HEAD",
    )
    return tmp_path / "test-project"
