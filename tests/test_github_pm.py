"""Tests for GitHub PM scaffolding (enable_github_pm=true)."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest


def test_pm_key_files_exist(generated_pm: Path) -> None:
    assert (generated_pm / ".github" / "ISSUE_TEMPLATE" / "stage.yml").exists()
    assert (generated_pm / ".github" / "ISSUE_TEMPLATE" / "epic.yml").exists()
    assert (generated_pm / ".github" / "ISSUE_TEMPLATE" / "slice.yml").exists()
    assert (generated_pm / ".github" / "ISSUE_TEMPLATE" / "spike.yml").exists()
    assert (generated_pm / ".github" / "ISSUE_TEMPLATE" / "idea.yml").exists()
    assert (generated_pm / ".github" / "ISSUE_TEMPLATE" / "bug.yml").exists()
    assert (generated_pm / ".github" / "pull_request_template.md").exists()
    assert (generated_pm / "scripts" / "bootstrap-pm.sh").exists()
    assert (generated_pm / "docs" / "project-management.md").exists()
    assert (generated_pm / ".claude" / "skills" / "forge" / "SKILL.md").exists()


def test_pm_forge_skill_has_frontmatter(generated_pm: Path) -> None:
    content = (generated_pm / ".claude" / "skills" / "forge" / "SKILL.md").read_text()
    assert "name: forge" in content
    assert "AskUserQuestion" in content


def test_forge_skill_absent_without_pm(generated: Path) -> None:
    # copier may leave an empty parent dir behind, so assert on the file.
    assert not (generated / ".claude" / "skills" / "forge" / "SKILL.md").exists()


def test_pm_spike_template_has_required_fields(generated_pm: Path) -> None:
    content = (generated_pm / ".github" / "ISSUE_TEMPLATE" / "spike.yml").read_text()
    assert "kind:spike" in content
    assert "Question to answer" in content
    assert "Time box" in content
    assert "Decision criteria" in content


def test_pm_bootstrap_script_seeds_spike_label(generated_pm: Path) -> None:
    content = (generated_pm / "scripts" / "bootstrap-pm.sh").read_text()
    assert "kind:spike|#5319e7|Time-boxed research" in content


def test_pm_bootstrap_script_seeds_stage_label(generated_pm: Path) -> None:
    content = (generated_pm / "scripts" / "bootstrap-pm.sh").read_text()
    assert "kind:stage|" in content


def test_pm_stage_template_has_required_fields(generated_pm: Path) -> None:
    content = (generated_pm / ".github" / "ISSUE_TEMPLATE" / "stage.yml").read_text()
    assert "kind:stage" in content
    assert "Stage definition" in content
    assert "Milestone" in content


def test_pm_claude_md_has_lifecycle(generated_pm: Path) -> None:
    content = (generated_pm / "CLAUDE.md").read_text()
    assert "Issue Lifecycle" in content
    assert "In Progress" in content
    assert "Fixes #N" in content
    assert "project-management.md" in content
    assert "Label System" in content


def test_pm_bootstrap_script_rendered(generated_pm: Path) -> None:
    content = (generated_pm / "scripts" / "bootstrap-pm.sh").read_text()
    assert 'PROJECT_NAME="test-project"' in content
    assert 'OWNER="test-user"' in content
    assert "{{" not in content
    assert "{%" not in content


def test_pm_readme_has_setup_section(generated_pm: Path) -> None:
    content = (generated_pm / "README.md").read_text()
    assert "bootstrap-pm.sh" in content
    assert "project-management.md" in content


def test_pm_no_jinja_artifacts(generated_pm: Path) -> None:
    jinja_var = re.compile(r"(?<!\$){{")

    for path in generated_pm.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(generated_pm))
        if ".venv" in rel:
            continue
        if path.suffix not in {
            ".py",
            ".toml",
            ".yml",
            ".yaml",
            ".json",
            ".md",
            ".txt",
            ".sh",
        }:
            continue
        content = path.read_text()
        assert not jinja_var.search(content), f"Unrendered Jinja in {path}"
        assert "{%" not in content, f"Unrendered Jinja tag in {path}"


def test_pm_bootstrap_script_passes_shellcheck(generated_pm: Path) -> None:
    """The rendered bootstrap script passes ShellCheck cleanly."""
    if shutil.which("shellcheck") is None:
        pytest.skip("shellcheck not installed (available on ubuntu-latest CI runners)")

    script = generated_pm / "scripts" / "bootstrap-pm.sh"
    result = subprocess.run(
        ["shellcheck", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"shellcheck reported issues in {script}:\n{result.stdout}\n{result.stderr}"
    )
