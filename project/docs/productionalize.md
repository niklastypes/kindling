# Productionalize

How to take a Kindling project from local dev to a deployed, production-ready application. This covers containerization, CI, health endpoints, environment management, and serving strategy.

---

## Health endpoint

Every deployable service needs a health check. Add one early:

```python
# src/<pkg>/api/health.py
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

If the app has a database or upstream dependency, consider a richer check:

```python
@router.get("/api/health")
async def health(db: Db) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
```

---

## Environment management

### Pattern

Use `pydantic-settings` with a `.env` file:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    log_level: str = "INFO"
    cors_allowed_origins: str = ""

    # Upstream services
    upstream_base_url: str = ""
    upstream_api_key: str = ""

    # Database (optional)
    database_url: str = ""

settings = Settings()
```

### .env.example

Commit a `.env.example` with all variable names but no real values:

```bash
LOG_LEVEL=INFO
CORS_ALLOWED_ORIGINS=http://localhost:4200
UPSTREAM_BASE_URL=
UPSTREAM_API_KEY=
DATABASE_URL=
```

Never commit `.env` itself. Kindling's `.gitignore` already handles this.

### Frontend

Use `VITE_API_BASE_URL` for the API base. It defaults to empty string (same-origin), which works in production. In dev, Vite's proxy handles routing to the backend.

---

## Logging

Use stdlib `logging` with structured format. Keep it simple:

```python
import logging
from .settings import settings

def configure_logging() -> None:
    level = settings.log_level.upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    # Quiet down noisy libraries
    for name in ("uvicorn", "httpx", "httpcore", "asyncio"):
        logging.getLogger(name).setLevel(logging.WARNING)
```

Call `configure_logging()` at the top of `create_app()`.

Follow the pattern from AGENTS.md: use `%s` formatting, not f-strings:

```python
logger.info("Processing item %s", item_id)
```

---

## CORS

Conditional on environment. Wide open in dev, locked down in production:

```python
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

Set `CORS_ALLOWED_ORIGINS=http://localhost:4200` for dev. In production, set it to the actual frontend origin or omit it entirely if frontend and API share the same origin (single-container deploy).

---

## Docker

### Single container (recommended starting point)

One container serves both API and frontend. Simplest to deploy:

```dockerfile
# Stage 1: Python dependencies
FROM python:3.13-dev AS api
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --frozen --no-install-project
COPY api/ .
RUN uv sync --frozen

# Stage 2: Frontend build
FROM node:22-dev AS ui
RUN corepack enable
WORKDIR /workspace
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY ui/ ui/
RUN pnpm install --frozen-lockfile
RUN pnpm exec nx run ui:build --outDir /app/dist

# Stage 3: Runtime
FROM python:3.13
WORKDIR /app
COPY --from=api /app/.venv .venv
COPY --from=ui /app/dist dist/
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8080
CMD ["uvicorn", "<pkg>.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
```

### SPA serving in FastAPI

Add this to `create_app()` after mounting routers:

```python
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

# Serve built frontend assets
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

# SPA catch-all: return index.html for all non-API routes
@app.get("/{full_path:path}")
async def catch_all(request: Request, full_path: str) -> Response:
    if request.url.path.startswith("/api"):
        return Response(status_code=404)
    return FileResponse("dist/index.html")
```

**Important:** Mount the catch-all AFTER all API routers. FastAPI evaluates routes in order.

### When to split into two containers

The single-container approach works well for most projects. Consider splitting (nginx + FastAPI as separate containers) when:

- Frontend and backend need independent scaling
- You want independent deploy cycles
- You need nginx-specific features (caching, rate limiting, SSE buffering control)

---

## CI

Kindling generates Python-only CI (`ci.yml`). For a full-stack monorepo, replace it with an Nx-based workflow that covers both sides:

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - uses: astral-sh/setup-uv@v7

      - run: pnpm install --frozen-lockfile

      - uses: nrwl/nx-set-shas@v4
      - run: npx nx affected -t lint typecheck test
```

This single job runs:
- **Python:** ruff lint, ty typecheck, pytest (via `@nxlv/python`)
- **Frontend:** ESLint, vue-tsc, Vitest (via Nx plugins)

Only affected projects are checked, so it stays fast.

Keep Kindling's `release.yml` if you want release-please. It works alongside the Nx CI.

### Quality tools summary

| Side | Lint | Format | Typecheck | Test |
|------|------|--------|-----------|------|
| Python | ruff | ruff format | ty | pytest |
| Frontend | ESLint | Prettier | vue-tsc | Vitest |
| E2E | | | | Playwright |

---

## Testing strategy

A full-stack app needs tests at multiple levels. The goal is fast feedback for most things, with slower, broader tests reserved for what actually needs them.

### Test pyramid

| Level | Tool | What it covers | Speed |
|---|---|---|---|
| **Unit** | pytest, Vitest | Pure functions, isolated logic, edge cases | Fast (ms) |
| **Integration** | pytest (with real DB/services) | Component interactions, database queries, service layers | Medium (seconds) |
| **API-level BDD** | pytest-bdd | User-facing behavior through the API contract | Medium (seconds) |
| **Contract** | openapi-typescript, pytest | Frontend/backend type agreement via OpenAPI spec | Fast (ms) |
| **E2E** | Playwright | Critical user journeys through the browser | Slow (seconds to minutes) |
| **Smoke** | pytest or curl in CI | Post-deploy sanity check (is the app alive and functional?) | Fast (ms) |

Most of your tests should live in the bottom two rows. The top rows catch the things that slip through.

### Unit tests

Already covered in the full-stack guide. Backend unit tests live in `api/tests/`, frontend unit tests run via Vitest. Use these for pure logic, edge cases, and anything that doesn't need external dependencies.

### Integration tests

Test how components work together with real dependencies (database, caches, external service clients). These catch the bugs that unit tests with mocks miss: wrong SQL, transaction handling, serialization mismatches.

```python
# api/tests/integration/conftest.py
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest_asyncio.fixture()
async def db_session():
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost:5432/test")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()
```

```python
# api/tests/integration/test_items_repository.py
import pytest

@pytest.mark.asyncio
async def test_create_and_retrieve_item(db_session):
    repo = ItemRepository(db_session)
    created = await repo.create(name="Widget")
    retrieved = await repo.get(created.id)
    assert retrieved.name == "Widget"
```

Use a pytest marker to separate integration tests from unit tests so you can run them independently:

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = ["integration: tests requiring external services"]
```

```bash
uv run pytest -m "not integration"    # Fast: unit tests only
uv run pytest -m integration          # Slower: integration tests (needs DB running)
uv run pytest                         # Everything
```

### BDD at the API layer

This is the sweet spot for behavior tests. Gherkin feature files describe what the system does from a user's perspective, and step definitions exercise the FastAPI endpoints through the test client. No browser, no UI coupling, just the business behavior.

```
api/tests/
├── features/
│   └── items.feature
├── step_defs/
│   └── test_items.py
├── integration/
│   └── ...
├── conftest.py
└── test_smoke.py
```

```gherkin
# api/tests/features/items.feature
Feature: Item management

  Scenario: Create and list items
    Given an empty item store
    When I create an item named "Widget"
    Then the items list contains "Widget"
```

```python
# api/tests/step_defs/test_items.py
from pytest_bdd import scenario, given, when, then

@scenario("../features/items.feature", "Create and list items")
def test_create_and_list():
    pass

@given("an empty item store", target_fixture="context")
def empty_store():
    return {}

@when("I create an item named \"Widget\"", target_fixture="context")
def create_item(client, context):
    response = client.post("/api/items", json={"name": "Widget"})
    assert response.status_code == 201
    context["created"] = response.json()
    return context

@then("the items list contains \"Widget\"")
def check_list(client, context):
    response = client.get("/api/items")
    names = [item["name"] for item in response.json()]
    assert "Widget" in names
```

Write feature files in business language, not implementation details. "When I create an item" is good. "When I POST to /api/items with JSON body" is not.

Add `pytest-bdd` to Kindling's dev dependencies:

```toml
[dependency-groups]
dev = [
    # ... existing
    "pytest-bdd>=8.0.0",
]
```

### Contract tests

Frontend and backend can drift apart silently. Contract tests catch this at build time.

FastAPI generates an OpenAPI spec for free at `/openapi.json`. Use this as the single source of truth:

1. **Backend side:** add a pytest fixture that exports the spec to a known location during CI:

```python
# api/tests/test_openapi.py
import json
from pathlib import Path

def test_export_openapi_spec(app):
    spec = app.openapi()
    Path("openapi.json").write_text(json.dumps(spec, indent=2))
```

2. **Frontend side:** use `openapi-typescript` to generate types from that spec and check them into the repo (or generate on CI). If the spec changes in a way that breaks the frontend's assumptions, the TypeScript compiler catches it.

```bash
# In CI or as a dev script
npx openapi-typescript api/openapi.json -o ui/src/shared/api/schema.d.ts
```

This replaces the manual `RawItem` / `mapItem` pattern from the full-stack guide with compile-time safety. Start with manual mapping, graduate to contract tests when the API surface grows.

### E2E tests

Playwright tests in `ui-e2e/` cover critical user journeys through the browser. These are expensive to write and maintain, so be selective:

- Login/signup flow
- The primary happy path (the one thing your app absolutely must do)
- Payment or other irreversible actions

Don't duplicate what BDD and integration tests already cover. If a scenario can be tested at the API level, it should be.

### Smoke tests

A small suite that runs post-deploy to verify the deployed app is actually working. These are not comprehensive, just "is it alive and minimally functional?"

```python
# api/tests/smoke/test_smoke.py
import httpx
import os

BASE_URL = os.environ["SMOKE_TEST_URL"]  # e.g. https://my-app.example.com

def test_health():
    response = httpx.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200

def test_frontend_loads():
    response = httpx.get(BASE_URL)
    assert response.status_code == 200
    assert "index.html" in response.text or "<div id=" in response.text
```

Run these in CI after deployment, or as a scheduled job. They should complete in seconds.

### Where tests run

| Test type | When | Runner |
|---|---|---|
| Unit + Integration + BDD | Every PR, on affected projects | `npx nx affected -t test` |
| Contract | Every PR (spec export + type generation) | CI pipeline |
| E2E | Every PR (or nightly if slow) | `npx nx run ui-e2e:e2e` |
| Smoke | Post-deploy | Separate CI job or scheduled trigger |

---

## Database (if needed)

### Local dev with Docker Compose

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

```bash
docker compose up -d
```

### SQLAlchemy async pattern

```python
# src/<pkg>/db.py
from typing import Annotated, AsyncIterator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .settings import settings

engine = create_async_engine(settings.database_url)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

Db = Annotated[AsyncSession, Depends(get_db)]
```

Add to `pyproject.toml`:
```toml
dependencies = [
    # ... existing
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
]
```

---

## Upstream error handling

If the backend proxies external APIs, add exception handlers:

```python
import httpx

@app.exception_handler(httpx.ConnectError)
async def handle_connect_error(request, exc):
    return JSONResponse(status_code=502, content={"detail": "Upstream service unreachable"})

@app.exception_handler(httpx.TimeoutException)
async def handle_timeout(request, exc):
    return JSONResponse(status_code=504, content={"detail": "Upstream service timeout"})
```

---

## Observability (when you need it)

Not needed at the start, but when debugging production behavior matters:

- **OpenTelemetry** for distributed tracing (auto-instruments FastAPI and httpx)
- **Langfuse** for LLM-specific traces (if building AI features)
- **Prometheus** for metrics (request counts, latencies)

These add complexity. Add them when you have a production environment to observe, not before.

---

## Checklist

Before deploying for the first time:

- [ ] Health endpoint exists and returns 200
- [ ] `.env.example` documents all required variables
- [ ] No secrets in git (`.env` is gitignored)
- [ ] `CORS_ALLOWED_ORIGINS` is set correctly for the deploy environment
- [ ] Docker build succeeds locally: `docker build -t <project> .`
- [ ] Container starts and serves both API and frontend
- [ ] Frontend routes work (SPA catch-all returns `index.html`)
- [ ] CI passes: lint, typecheck, test on both sides
- [ ] `LOG_LEVEL` defaults to `INFO` (not `DEBUG`) in production
