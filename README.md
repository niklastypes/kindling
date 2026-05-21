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

## One-time Setup

### Renovate

Kindled projects include a `renovate.json` for automated dependency updates. To activate it, install the Renovate GitHub App on your account once:

1. Go to [github.com/apps/renovate](https://github.com/apps/renovate) and click **Install**
2. Select your account, choose **Scan and Alert**, and grant access to repositories (all repos or selected)
3. Done. Any repo with a `renovate.json` will automatically receive dependency update PRs.

## Requirements

- [copier](https://copier.readthedocs.io/) (`uv tool install copier`)
- [uv](https://docs.astral.sh/uv/) (for kindled projects)
- [Renovate GitHub App](https://github.com/apps/renovate) installed on your GitHub account (one-time setup, see below)
