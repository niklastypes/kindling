# 🪵 Kindling

> Small, dry, catches quickly.

A copier template for bootstrapping Python projects with clean defaults and consistent standards.

## What's in the Bundle

- **uv** for package management
- **ruff** for formatting and linting
- **ty** for type checking
- **pytest** for testing
- **pre-commit** hooks (conventional commits, ruff, ty)
- **GitHub Actions** CI (lint, format, type check, test)
- **release-please** for automated versioning and releases
- **Renovate** for automated dependency updates
- src-layout, MIT license, AGENTS.md with project standards

## Usage

```bash
# Kindle a new project
copier copy gh:niklastypes/kindling my-project

# Feed the fire: pull template improvements into an existing project
cd my-project
copier update
```

You'll be asked for: project name, description, author, Python version.

## Requirements

- [copier](https://copier.readthedocs.io/) (`uv tool install copier`)
- [uv](https://docs.astral.sh/uv/) (for kindled projects)
