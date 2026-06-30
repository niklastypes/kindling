# Kindling

Copier template for bootstrapping Python projects. See README.md for user-facing docs.

## Repo Structure

```
kindling/
├── copier.yml          # Template config: questions, validators, tasks, skip rules
├── project/            # Template root (everything here gets copied to generated projects)
│   ├── .github/workflows/
│   ├── src/{{package_name}}/
│   └── tests/
└── tests/              # Tests for the template itself
    ├── test_generate.py    # Generation correctness (files exist, rendering, validation)
    └── test_update.py      # Upgrade path from v0.1.0 to HEAD
```

Top-level files (`pyproject.toml`, `.github/workflows/`, `release-please-config.json`, `renovate.json`, `CHANGELOG.md`) are kindling's own infrastructure, NOT part of the template.

## Commands

```bash
# Run template tests
uv run pytest tests/ -v

# Lint and format (kindling's own code, tests/ only since there's no src/)
uv run ruff check tests/
uv run ruff format --check tests/
uv run ty check tests/

# Generate a test project locally
copier copy . /tmp/test-project --trust \
  --data project_name=my-project \
  --data project_description="A test project" \
  --data author_name="Your Name" \
  --data github_username="your-username" \
  --data python_version="3.13"
```

## Templating Rules

- Files needing Jinja rendering get a `.jinja` suffix. Files without it are copied verbatim.
- GitHub Actions `${{ }}` conflicts with Jinja `{{ }}`. Wrap every `${{ }}` expression in `{% raw %}...{% endraw %}`. Plain `if:` conditions without `${{ }}` don't need wrapping.
- `_skip_if_exists` in copier.yml prevents `copier update` from overwriting files users typically customize (AGENTS.md, README.md, LICENSE, .gitignore).
- `_subdirectory: project` tells copier to use `project/` as the template root.
- `_tasks` runs post-generation shell commands (git init + first commit + `v0.1.0` tag). Requires `--trust`. The tag anchors release-please's manifest entry so the git tag history matches `version = "0.1.0"` from the start.

## Copier Validators

Validators in `copier.yml` are Jinja expressions. They return an error message string if validation fails, or empty string if valid. The `project_name` validator uses `regex_search` (a Jinja filter provided by copier) to enforce kebab-case: `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`.

## What Gets Generated

| File | Notes |
|---|---|
| `pyproject.toml` | uv + hatchling, ruff, ty, pytest config |
| `.python-version` | From copier question |
| `.gitignore` | Standard Python ignores |
| `.gitattributes` | Line ending normalization (`* text=auto`) |
| `.env.example` | Empty placeholder |
| `LICENSE` | MIT |
| `AGENTS.md` | Python-specific standards quick reference |
| `README.md` | Project README with setup instructions |
| `renovate.json` | Automated dependency updates |
| `release-please-config.json` | Automated versioning (feat bumps minor pre-1.0) |
| `.release-please-manifest.json` | Release-please version anchor (starts at 0.1.0) |
| `.pre-commit-config.yaml` | See hook stages below |
| `.github/workflows/ci.yml` | lint, format, type check, test |
| `.github/workflows/release.yml` | release-please |
| `src/{{package_name}}/__init__.py` | Package init with version |
| `src/{{package_name}}/py.typed` | PEP 561 marker for downstream type checkers |
| `.copier-answers.yml` | Tracks template version for `copier update` |
| `tests/__init__.py` | Empty |
| `tests/test_{{package_name}}.py` | Smoke test (confirms package imports and has a version) |
| `docs/ubiquitous-language.md` | Guide: maintaining a canonical glossary for the project's design vocabulary |
| `docs/full-stack.md` | Guide: adding a Vue 3 frontend + Nx monorepo |
| `docs/productionalize.md` | Guide: Docker, CI, health endpoints, deploy readiness |

Not generated deliberately: logging config, Docker, FastAPI/CLI scaffolding, test fixtures. The `docs/` guides explain how to add these when needed.

**Generated when `enable_github_pm=true`:** `.github/ISSUE_TEMPLATE/{epic,slice,spike,idea,bug,stage}.yml`, `.github/pull_request_template.md`, `scripts/bootstrap-pm.sh`, `docs/project-management.md`, and `.claude/skills/forge/SKILL.md`, the `/forge` skill that structures `notes/` into `docs/` (architecture, ADRs, slim roadmap) and GitHub Project items (milestones, epics, slices, ideas). The generated README and CLAUDE.md both point users/agents at it.

**Generated when `full_stack=true`:** `api/` (FastAPI backend), `ui/` (Vue 3 frontend), `nx.json`, `package.json`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `docs/full-stack.md`; root-level Python files move into `api/`.

**Generated when `hexagonal=true`** (full-stack only, default-on): the backend uses a ports & adapters layout (`domain/`, `ports/`, `adapters/`, `application/` + an `app.py` composition-root shim) instead of the flat `api/`-router layout, with import-linter contracts in `pyproject.toml` and a `lint-imports` hook in pre-commit + CI. Opt out (`hexagonal=false`) for the flat backend. The two layouts are mutually exclusive, selected by `_exclude` rules.

## Hook Stages

| Stage | Hooks | Notes |
|---|---|---|
| pre-commit | ruff (lint + format), check-ast, trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-added-large-files, check-merge-conflict, debug-statements, detect-private-key | Runs on every commit, all fast |
| commit-msg | conventional-pre-commit | Enforces conventional commit format |
| pre-push | ty check, pre-commit-update | Slower checks that don't need to run on every commit |

## Copier Questions

| Variable | Type | Default | Notes |
|---|---|---|---|
| `project_name` | str | (required) | Kebab-case, validated. Used for pyproject.toml name, directory. |
| `project_description` | str | "A Python project, kindled with Kindling" | One-liner for pyproject.toml and README |
| `author_name` | str | (required) | For pyproject.toml and LICENSE |
| `github_username` | str | (required) | GitHub username or org, for project URLs |
| `python_version` | str | "3.13" | Choices: 3.12, 3.13 |
| `full_stack` | bool | false | Scaffold a Vue 3 + FastAPI + Nx monorepo. Python moves into `api/`, adds `ui/`. |
| `hexagonal` | bool | `{{ full_stack }}` | Asked only for full-stack. Hexagonal (ports & adapters) backend with import-linter-enforced boundaries; opt out for the flat layout. |
| `enable_github_pm` | bool | false | Add the Project board bootstrap, issue/PR templates, labels, and the `/forge` skill. |
| `package_name` | str | (computed) | `project_name` with hyphens replaced by underscores. Not shown to user. |

`package_name` is used everywhere a Python-valid identifier is needed (src directory, imports, pyproject.toml). `project_name` is used for human-readable names.

## Design Decisions

| Decision | Choice | Why |
|---|---|---|
| Templating | Copier | `copier update` pulls improvements into existing projects. Cookiecutter can't. |
| Package management | uv | Fast, modern, PEP 517 compliant |
| Build backend | hatchling | Simple, src-layout native |
| Linting + formatting | ruff | Single tool, fast, comprehensive |
| Type checking | ty | Astral's type checker, pairs with ruff |
| Testing | pytest | Industry standard |
| Versioning | release-please | Automated from conventional commits |
| Dependency updates | Renovate | Automated PRs |
| Layout | src-layout | Clean separation of source and tests |
