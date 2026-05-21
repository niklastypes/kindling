# Kindling

Small, dry, catches quickly. A copier template for bootstrapping Python projects with clean defaults and consistent standards. **Kindling starts the fire, it doesn't become it.**

Replaces the old [`instant-repo`](https://github.com/niklastypes/instant-repo) template (Poetry, mypy, commitizen, MkDocs, all superseded). Archived.

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
| `LICENSE` | MIT, current year |
| `AGENTS.md` | Python-specific standards quick reference |
| `README.md` | Project README with setup instructions |
| `renovate.json` | Automated dependency updates |
| `release-please-config.json` | Pre-1.0 safe version bumping |
| `.pre-commit-config.yaml` | conventional commits, ruff, ty |
| `.github/workflows/ci.yml` | lint, format, type check, test |
| `.github/workflows/release.yml` | release-please |
| `src/{{package_name}}/__init__.py` | Package init with version |
| `tests/__init__.py` | Empty |
| `.copier-answers.yml` | Tracks template version for `copier update` |

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
| Pre-commit hooks | conventional-pre-commit, ruff, ty | Catch issues before CI |
| Layout | src-layout | Clean separation of source and tests |

## Copier Questions

| Variable | Type | Default | Notes |
|---|---|---|---|
| `project_name` | str | (required) | Lowercase with hyphens. Used for pyproject.toml name, directory. |
| `project_description` | str | "A Python project" | One-liner for pyproject.toml and README |
| `author_name` | str | "Niklas Baier" | For pyproject.toml and LICENSE |
| `python_version` | str | "3.13" | Choices: 3.12, 3.13 |
| `package_name` | str | (computed) | `project_name` with hyphens replaced by underscores. Not shown to user. |

`package_name` is used everywhere a Python-valid identifier is needed: src directory, import paths, pyproject.toml package config. `project_name` is used for human-readable names (README title, pyproject.toml `name` field).

## Repo Structure

```
kindling/
├── copier.yml                          # Questions and copier config
├── CLAUDE.md                           # This file
├── README.md                           # Template repo README (not copied)
├── plan.md                             # Implementation plan
├── project/                            # Template root (_subdirectory in copier.yml)
│   ├── .copier-answers.yml.jinja
│   ├── .env.example
│   ├── .gitignore
│   ├── .python-version.jinja
│   ├── .pre-commit-config.yaml
│   ├── .github/workflows/
│   │   ├── ci.yml.jinja
│   │   └── release.yml.jinja
│   ├── AGENTS.md.jinja
│   ├── LICENSE.jinja
│   ├── README.md.jinja
│   ├── pyproject.toml.jinja
│   ├── release-please-config.json.jinja
│   ├── renovate.json
│   ├── src/{{package_name}}/
│   │   └── __init__.py
│   └── tests/
│       └── __init__.py
└── tests/                              # Tests for the template itself
    └── test_generate.py
```

## Templating Rules

- Files needing Jinja rendering get a `.jinja` suffix. Files without the suffix are copied verbatim.
- GitHub Actions uses `${{ }}` which conflicts with Jinja's `{{ }}`. Wrap every `${{ }}` expression in `{% raw %}...{% endraw %}`.
- `_skip_if_exists: [AGENTS.md, README.md]` prevents `copier update` from overwriting user-customized files.
- `_subdirectory: project` tells copier to use `project/` as the template root, not the repo root.

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
copier copy . /tmp/test-project \
  --data project_name=my-project \
  --data project_description="A test project" \
  --data author_name="Niklas Baier" \
  --data python_version="3.13"

# Run the template verification tests
uv run pytest tests/ -v

# Check for unrendered Jinja artifacts in a generated project
grep -r "{{" /tmp/test-project --include="*.py" --include="*.toml" --include="*.yml" --include="*.yaml" --include="*.json" --include="*.md"
```

## Current Status

Repo initialized. No template files created yet. See plan.md for the full step-by-step implementation.
