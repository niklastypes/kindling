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
COPY apps/<app>/api/pyproject.toml apps/<app>/api/uv.lock ./
RUN uv sync --frozen --no-install-project
COPY apps/<app>/api/ .
RUN uv sync --frozen

# Stage 2: Frontend build
FROM node:22-dev AS ui
RUN corepack enable
WORKDIR /workspace
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/<app>/ui/ apps/<app>/ui/
RUN pnpm install --frozen-lockfile
RUN pnpm exec nx run <app>-ui:build --outDir /app/dist

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

## Database (if needed)

### Local dev with Docker Compose

```yaml
# apps/<app>/docker-compose.yml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_DB: <app>
      POSTGRES_USER: <app>
      POSTGRES_PASSWORD: <app>
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

```bash
cd apps/<app> && docker compose up -d
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
- [ ] Docker build succeeds locally: `docker build -t <app> .`
- [ ] Container starts and serves both API and frontend
- [ ] Frontend routes work (SPA catch-all returns `index.html`)
- [ ] CI passes: lint, typecheck, test on both sides
- [ ] `LOG_LEVEL` defaults to `INFO` (not `DEBUG`) in production
