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

# Full-stack defaults to hexagonal; this opts out for the flat backend layout.
FLAT_FULL_STACK_DATA = {
    **FULL_STACK_DATA,
    "hexagonal": False,
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


# The generated* fixtures are session-scoped: copier.run_copy (with unsafe=True)
# runs git init + uv sync per generation, plus pnpm install for full-stack, so
# regenerating per test is expensive. Contract: consumers must treat the
# generated project as READ-ONLY. A test that needs to mutate the project (e.g.
# the copier update tests) must create its own copy via run_copy directly.


@pytest.fixture(scope="session")
def generated(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dest = tmp_path_factory.mktemp("generated") / "test-project"
    copier.run_copy(
        str(TEMPLATE_ROOT),
        dest,
        data=DEFAULT_DATA,
        unsafe=True,
        vcs_ref="HEAD",
    )
    return dest


@pytest.fixture(scope="session")
def generated_full_stack(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dest = tmp_path_factory.mktemp("generated_full_stack") / "test-project"
    # No `hexagonal` key in the data + defaults=True exercises the real default
    # (hexagonal is on for full-stack projects).
    copier.run_copy(
        str(TEMPLATE_ROOT),
        dest,
        data=FULL_STACK_DATA,
        defaults=True,
        unsafe=True,
        vcs_ref="HEAD",
    )
    return dest


@pytest.fixture(scope="session")
def generated_flat_full_stack(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dest = tmp_path_factory.mktemp("generated_flat_full_stack") / "test-project"
    copier.run_copy(
        str(TEMPLATE_ROOT),
        dest,
        data=FLAT_FULL_STACK_DATA,
        unsafe=True,
        vcs_ref="HEAD",
    )
    return dest


@pytest.fixture(scope="session")
def generated_pm(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dest = tmp_path_factory.mktemp("generated_pm") / "test-project"
    copier.run_copy(
        str(TEMPLATE_ROOT),
        dest,
        data=PM_DATA,
        unsafe=True,
        vcs_ref="HEAD",
    )
    return dest
