# Kindling

Small, dry, catches quickly. A copier template for bootstrapping Python projects with clean defaults and consistent standards. **Kindling starts the fire, it doesn't become it.**

Replaces the old `instant-repo` template (Poetry, mypy, commitizen, MkDocs, all superseded). Archived.

## Goal

Generate a new Python project with everything you'd never want to set up by hand: CI, linting, formatting, type checking, release automation, pre-commit hooks. Then get out of the way.

Also serves as the **single source of truth for Python project standards**: tooling choices, preferred libraries, code patterns.

## What Gets Generated

| File | Notes |
|---|---|
| `pyproject.toml` | uv + hatchling, ruff, ty, pytest config |
| `.python-version` | From copier question |
| `.gitignore` | Standard Python ignores |
| `.env.example` | Empty placeholder |
| `LICENSE` | MIT |
| `AGENTS.md` | Python-specific standards quick reference |
| `README.md` | Project README with setup instructions |
| `renovate.json` | Automated dependency updates |
| `release-please-config.json` | Automated versioning (feat bumps minor pre-1.0) |
| `.gitattributes` | Line ending normalization (`* text=auto`) |
| `.pre-commit-config.yaml` | conventional commits, ruff + check-ast (pre-commit), ty + pre-commit-update (pre-push) |
| `.github/workflows/ci.yml` | lint, format, type check, test |
| `.github/workflows/release.yml` | release-please |
| `src/{{package_name}}/__init__.py` | Package init with version |
| `src/{{package_name}}/py.typed` | PEP 561 marker for downstream type checkers |
| `tests/__init__.py` | Empty |
| `tests/test_{{package_name}}.py` | Smoke test (confirms package imports and has a version) |
| `.copier-answers.yml` | Tracks template version for `copier update` |
| `.release-please-manifest.json` | Release-please version anchor (starts at 0.1.0) |

What is deliberately NOT generated: logging config, docs framework, Docker, FastAPI/CLI scaffolding, test fixtures.

## Design Decisions

| Decision | Choice | Why |
|---|---|---|
| Templating | Copier | `copier update` pulls improvements into existing projects. Cookiecutter can't do this. |
| Package management | uv | Fast, modern, PEP 517 compliant |
| Build backend | hatchling | Simple, src-layout native |
| Linting + formatting | ruff | Single tool, fast, comprehensive |
| Type checking | ty | Astral's type checker, pairs with ruff |
| Testing | pytest | Industry standard |
| Versioning | release-please | Automated from conventional commits |
| Dependency updates | Renovate | Automated PRs |
| Pre-commit hooks | conventional-pre-commit, ruff, check-ast, ty, pre-commit-update | Catch issues before CI. ty and pre-commit-update run on pre-push to keep commits fast |
| Layout | src-layout | Clean separation of source and tests |

## Copier Questions

| Variable | Type | Default | Notes |
|---|---|---|---|
| `project_name` | str | (required) | Kebab-case, validated (`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`). Used for pyproject.toml name, directory. |
| `project_description` | str | "A Python project, kindled with Kindling" | One-liner for pyproject.toml and README |
| `author_name` | str | (required) | For pyproject.toml and LICENSE |
| `github_username` | str | (required) | GitHub username or org, for project URLs |
| `python_version` | str | "3.13" | Choices: 3.12, 3.13 |
| `package_name` | str | (computed) | `project_name` with hyphens replaced by underscores. Not shown to user. |

`package_name` is used everywhere a Python-valid identifier is needed: src directory, import paths, pyproject.toml package config. `project_name` is used for human-readable names (README title, pyproject.toml `name` field).

## Repo Structure

```
kindling/
├── copier.yml          # Template config: questions, tasks, skip rules
├── project/            # Template root — everything here is copied to generated projects
└── tests/              # Tests for the template itself (test_generate.py, test_update.py)
```

Other top-level files (`pyproject.toml`, `.github/workflows/`, `release-please-config.json`, `renovate.json`, `CHANGELOG.md`) are kindling's own infrastructure and are NOT copied to generated projects.

## Templating Rules

- Files needing Jinja rendering get a `.jinja` suffix. Files without the suffix are copied verbatim.
- GitHub Actions uses `${{ }}` which conflicts with Jinja's `{{ }}`. Wrap every `${{ }}` expression in `{% raw %}...{% endraw %}`. Plain `if:` conditions without `${{ }}` don't need wrapping.
- `_skip_if_exists: [AGENTS.md, README.md, LICENSE, .gitignore]` prevents `copier update` from overwriting files users typically customize.
- `_subdirectory: project` tells copier to use `project/` as the template root, not the repo root.
- `_tasks` runs shell commands in the destination after generation. Currently used to auto-init git and create a conventional first commit. Requires `--trust` to run.

## Stages (Roadmap)

| Stage | Tag | Deliverable |
|---|---|---|
| Bus Ticket | v0.1.0 | copier.yml + pyproject.toml + src layout. `uv sync` works. |
| Skateboard | v0.2.0 | CI workflows + pre-commit hooks. Quality gates from day one. |
| Scooter | v0.3.0 | AGENTS.md + README + LICENSE + renovate + release-please + verification test. Fully production-ready. |

Tags are required for `copier update` to work. Every stage gets one.

## Commands

```bash
# Generate a test project
copier copy . /tmp/test-project --trust \
  --data project_name=my-project \
  --data project_description="A test project" \
  --data author_name="Your Name" \
  --data github_username="your-username" \
  --data python_version="3.13"

# Run the template verification tests
uv run pytest tests/ -v
```