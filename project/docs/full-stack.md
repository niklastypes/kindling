# Full-Stack Guide

How to evolve a Kindling-generated Python project into a Vue 3 + FastAPI monorepo. This doc covers everything Kindling doesn't: the frontend, Nx wiring, and how the two sides connect.

Kindling owns the Python tooling choices (ruff, ty, pytest, uv, hatchling). Don't override them.

---

## Monorepo layout

Move the Kindling-generated project into `api/` and add the frontend alongside it:

```
<project-root>/
├── api/                      # Kindling-generated backend
├── ui/                       # Vue 3 frontend
├── ui-e2e/                   # Playwright E2E
├── .prettierrc
├── eslint.config.mjs
├── nx.json
├── package.json              # Root (private)
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
├── tsconfig.base.json
└── vitest.workspace.ts
```

The root level is JS/Nx only. Python config stays inside `api/` (owned by Kindling).

---

## Nx setup

Nx orchestrates all tasks across Python and JS. One command for everything.

### Root package.json

```json
{
  "name": "<project>",
  "private": true,
  "packageManager": "pnpm@10.29.3",
  "devDependencies": {
    "@nx/eslint": "^22.0.0",
    "@nx/playwright": "^22.0.0",
    "@nx/vite": "^22.0.0",
    "@nx/vitest": "^22.0.0",
    "@nx/vue": "^22.0.0",
    "@nxlv/python": "^22.0.0",
    "nx": "^22.0.0",
    "typescript": "~5.9.0"
  }
}
```

### pnpm-workspace.yaml

```yaml
packages:
  - 'ui'
  - 'ui-e2e'
```

### nx.json

```json
{
  "defaultBase": "main",
  "plugins": [
    "@nxlv/python",
    "@nx/vite/plugin",
    "@nx/eslint/plugin",
    "@nx/vitest",
    "@nx/playwright/plugin"
  ],
  "targetDefaults": {
    "build": { "cache": true, "dependsOn": ["^build"] },
    "typecheck": { "dependsOn": ["^build"] }
  }
}
```

### Backend project.json

Create `api/project.json` alongside Kindling's files:

```json
{
  "name": "api",
  "projectType": "application",
  "sourceRoot": "api/src",
  "tags": ["fastapi"],
  "targets": {
    "serve": {
      "executor": "nx:run-commands",
      "options": {
        "command": "uv run uvicorn <pkg>.app:create_app --factory --reload --host 0.0.0.0 --port 8080",
        "cwd": "{projectRoot}",
        "env": { "CORS_ALLOWED_ORIGINS": "http://localhost:4200" }
      },
      "continuous": true
    }
  }
}
```

`@nxlv/python` infers `lint`, `format`, and `pytest:test` from Kindling's `pyproject.toml`. Only `serve` needs manual definition.

### Frontend project.json

```json
{
  "name": "ui",
  "projectType": "application",
  "sourceRoot": "ui/src",
  "tags": ["vue"],
  "targets": {
    "typecheck": {
      "executor": "nx:run-commands",
      "options": {
        "commands": ["vue-tsc --noEmit -p tsconfig.app.json"],
        "cwd": "{projectRoot}"
      }
    }
  }
}
```

Nx infers `build`, `serve`, `test`, and `lint` from Vite/ESLint plugins.

### Commands

```bash
# Dev (start both)
npx nx run-many -t serve

# Individual
npx nx run api:serve              # uvicorn --reload :8080
npx nx run ui:serve               # vite dev :4200

# Quality
npx nx run api:lint               # ruff
npx nx run ui:lint                # ESLint
npx nx run api:typecheck          # ty
npx nx run ui:typecheck           # vue-tsc
npx nx run api:pytest:test        # pytest
npx nx run ui:test                # Vitest
npx nx run ui-e2e:e2e             # Playwright

# Only what changed
npx nx affected -t lint test typecheck

# Discover targets
npx nx show project api
```

---

## How backend & frontend communicate

The frontend and backend communicate over HTTP. The frontend sends requests to the backend's REST API, and the backend responds with JSON. This is the only communication pattern you need for most applications.

### The request flow

In development, the Vite dev server proxies `/api` requests to the backend, so both feel like they're on the same origin:

```
Browser  →  Vite (:4200)  →  /api/*  →  FastAPI (:8080)
```

The proxy is configured in `vite.config.ts` (see Frontend architecture). In production, a reverse proxy (nginx, Caddy, or a cloud load balancer) serves the same role.

On the backend, all routes are mounted under `/api` (see the `app.include_router(..., prefix="/api")` pattern in Backend patterns). On the frontend, all HTTP calls go through `shared/api/client.ts`, a thin wrapper around `fetch` that handles JSON parsing and errors. Feature-specific API functions live in each feature's `api/` folder and map raw responses to clean frontend types.

### When to reach for more than REST

REST (request/response over HTTP) covers the vast majority of use cases. Before adding another protocol, make sure you actually need it:

| Pattern | When to use | Example |
|---|---|---|
| **REST** | Client asks, server answers. The default. | CRUD operations, form submissions, data fetching |
| **SSE (Server-Sent Events)** | Server needs to push updates to the client (one-directional). | Progress bars, live notifications, streaming LLM responses |
| **WebSockets** | Both sides need to send messages at any time (bidirectional). | Chat, collaborative editing, multiplayer state sync |

**Start with REST.** If you find yourself polling an endpoint every few seconds, that's a signal to consider SSE. If you need the client and server to exchange messages freely without a request/response cycle, that's when WebSockets make sense.

FastAPI has native support for both: `StreamingResponse` for SSE and `WebSocket` routes for WebSockets. When the time comes, adding either is straightforward without changing the existing REST setup.

---

## Backend patterns

Kindling provides the Python skeleton. Add these FastAPI-specific pieces inside `src/<pkg>/`.

### Dependencies to add

Add to Kindling's `[project.dependencies]` in `pyproject.toml`:

```toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
    "pydantic-settings>=2.9.0",
    "httpx>=0.28.0",
]
```

And for dev (add to Kindling's `[dependency-groups] dev`):

```toml
[dependency-groups]
dev = [
    # ... Kindling's defaults (pytest, ruff, ty, pre-commit)
    "pytest-asyncio>=1.0.0",
    "httpx>=0.28.0",
]
```

### App factory

```python
# src/<pkg>/app.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .logging_config import configure_logging

@asynccontextmanager
async def _lifespan(app: FastAPI):
    yield

def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(lifespan=_lifespan)

    cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins.split(","),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    from .api.health import router as health_router
    app.include_router(health_router, prefix="/api")

    return app
```

### Settings

```python
# src/<pkg>/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    log_level: str = "INFO"

settings = Settings()
```

### Router factory

For routes with dependencies, use factory functions (no module-global state):

```python
def build_feature_router(*, settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/items")
    async def list_items() -> list[Item]:
        ...

    return router

# In create_app():
app.include_router(build_feature_router(settings=settings), prefix="/api")
```

### Logging

```python
# src/<pkg>/logging_config.py
import logging
from .settings import settings

def configure_logging() -> None:
    level = settings.log_level.upper()
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    for name in ("uvicorn", "httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
```

### Folder growth

Start flat. Organize when complexity demands it:

```
src/<pkg>/
├── app.py
├── settings.py
├── logging_config.py
├── api/              # Add when you have 2+ route files
│   ├── health.py
│   └── <resource>.py
├── services/         # Add when routes get complex
│   └── <resource>.py
└── models/           # Add when you have shared Pydantic schemas
    └── <resource>.py
```

### Testing

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from <pkg>.app import create_app

@pytest.fixture()
def app():
    return create_app()

@pytest_asyncio.fixture()
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

---

## Frontend architecture

### Setup

```bash
cd ui
pnpm install
npx shadcn-vue@latest init    # Style: new-york, Base color: neutral, CSS variables: yes
```

### Source tree

```
ui/src/
├── main.ts
├── vue-shims.d.ts
├── styles/globals.css
├── app/
│   ├── App.vue                   # <RouterView />
│   ├── AppLayout.vue             # Shell: sidebar + header + <RouterView />
│   ├── router/
│   │   ├── index.ts
│   │   └── routes.ts
│   └── providers/
│       └── vue-query.ts
├── pages/                        # One .vue per route
├── features/
│   └── <feature>/
│       ├── api/                  # HTTP functions
│       ├── queries/              # TanStack Query hooks + keys.ts
│       ├── composables/          # use* composables
│       ├── model/                # Pure TS types (no functions)
│       ├── lib/                  # Pure functions (no Vue)
│       ├── ui/                   # Vue SFCs
│       └── index.ts              # Barrel export
├── shared/
│   ├── api/client.ts             # fetch wrapper + ApiError
│   ├── composables/
│   └── lib/routes/names.ts       # Route name constants
└── components/ui/                # shadcn-vue (vendored by CLI)
```

### Key files

**package.json** dependencies:
```json
{
  "dependencies": {
    "@tanstack/vue-query": "^5.90.0",
    "@lukemorales/query-key-factory": "^1.3.0",
    "vue": "^3.5.0",
    "vue-router": "^4.5.0",
    "lucide-vue-next": "^0.474.0",
    "vue-sonner": "^2.0.0"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.1.0",
    "@vitejs/plugin-vue": "^6.0.0",
    "tailwindcss": "^4.1.0",
    "typescript": "~5.9.0",
    "vite": "^6.0.0",
    "vue-tsc": "^3.0.0"
  }
}
```

**vite.config.ts:**
```typescript
import { fileURLToPath, URL } from 'node:url';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 4200,
    proxy: {
      '/api': { target: 'http://localhost:8080', changeOrigin: true },
    },
  },
  build: { outDir: './dist', emptyOutDir: true },
});
```

**tsconfig.base.json** (at monorepo root):
```json
{
  "compilerOptions": {
    "strict": true,
    "target": "es2022",
    "module": "esnext",
    "moduleResolution": "bundler",
    "isolatedModules": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "skipLibCheck": true,
    "lib": ["es2022"]
  }
}
```

**main.ts:**
```typescript
import './styles/globals.css';
import { createApp } from 'vue';
import { VueQueryPlugin } from '@tanstack/vue-query';
import App from './app/App.vue';
import { router } from './app/router';
import { queryClient } from './app/providers/vue-query';

createApp(App)
  .use(router)
  .use(VueQueryPlugin, { queryClient })
  .mount('#root');
```

**shared/api/client.ts:**
```typescript
export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public body: unknown = null,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new ApiError(response.status, text || 'Unknown error');
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

// Add { credentials: 'include' } to each request if using cookie-based auth.
export function get<T>(path: string): Promise<T> {
  return fetch(`${API_BASE}${path}`).then(
    (response) => handleResponse<T>(response),
  );
}

export function post<T>(path: string, body: unknown): Promise<T> {
  return fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then((response) => handleResponse<T>(response));
}

export function patch<T>(path: string, body: unknown): Promise<T> {
  return fetch(`${API_BASE}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then((response) => handleResponse<T>(response));
}

export function del<T>(path: string): Promise<T> {
  return fetch(`${API_BASE}${path}`, {
    method: 'DELETE',
  }).then((response) => handleResponse<T>(response));
}
```

**vue-query.ts:**
```typescript
import { QueryClient } from '@tanstack/vue-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      gcTime: 5 * 60_000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

---

## Frontend conventions

### Import rules

1. **Direction:** `app -> pages -> features -> shared`. Never reverse.
2. Cross-feature imports only via `features/<Y>/index.ts` barrel.
3. `shared/` never imports from `features/` or `pages/`.
4. `fetch` only in `shared/api/client.ts` and `features/*/api/`.
5. Feature components are route-agnostic (emit events, don't call `router.push`).
6. Vue components don't live in `model/` or `lib/`. Pure functions don't live in `model/`. Vue-dependent code doesn't live in `lib/`.

### Naming

- SFCs: `PascalCase.vue`
- Composables: `useThing.ts` exporting `useThing`
- Query hooks: `use<Resource>Query` / `use<Verb><Resource>Mutation`
- Types: `PascalCase`, no `I` prefix
- Functions: verb-first (`createItem`, `mapResponse`)
- Route names: kebab-case
- **No abbreviations.** `repository` not `repo`, `configuration` not `config`. Spell words out in full.

### Component patterns

- All `<script setup lang="ts">` (Composition API, never Options API)
- Props: `defineProps<{...}>()`
- Emits: `defineEmits<{...}>()`
- Styling: Tailwind utility classes, no `<style scoped>` blocks

### Where things live

| You have... | It goes in... |
|---|---|
| A TS interface | feature's `model/` |
| A fetch call | feature's `api/` |
| A query hook | feature's `queries/` |
| A Vue composable | feature's `composables/` |
| A pure function (no Vue) | feature's `lib/` |
| A component for one route | `pages/` |
| A component shared across features | feature's `ui/` (export via barrel) |
| A truly generic helper | `shared/` |

### Route state

Read URL state via composables, not `props: true`:

```typescript
export function useCurrentItemId(): ComputedRef<string | null> {
  const route = useRoute();
  return computed(() => {
    const value = route.params.itemId;
    return typeof value === 'string' && value.length > 0 ? value : null;
  });
}
```

Navigation goes through a central `useAppNavigation` composable in `shared/composables/`. Feature components emit events; pages wire them to navigation.

### Routing

```typescript
// shared/lib/routes/names.ts
export const routeNames = { home: 'home' } as const;

// app/router/routes.ts
import { routeNames } from '@/shared/lib/routes/names';
import AppLayout from '@/app/AppLayout.vue';

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', name: routeNames.home, component: () => import('@/pages/HomePage.vue') },
    ],
  },
];
```

Never hardcode route name strings. Always use `routeNames`.

### TanStack Query

One `keys.ts` per feature:

```typescript
import { createQueryKeys } from '@lukemorales/query-key-factory';
import { listItems, getItem } from '../api/items';

export const itemsKeys = createQueryKeys('items', {
  list: () => ({ queryKey: [{}], queryFn: () => listItems() }),
  detail: (id: string) => ({ queryKey: [{ id }], queryFn: () => getItem(id) }),
});
```

Query hooks:

```typescript
import { useQuery } from '@tanstack/vue-query';
import { itemsKeys } from './keys';
import type { Item } from '../model/item';

export function useItemsQuery() {
  return useQuery<Item[]>({ ...itemsKeys.list() });
}
```

### Adding a feature

1. Create the slice (only sub-folders you need):
   ```
   features/<name>/
   ├── api/
   ├── queries/       (+ keys.ts)
   ├── composables/
   ├── model/
   ├── lib/
   ├── ui/
   └── index.ts
   ```
2. `keys.ts` with `createQueryKeys(...)`.
3. Raw response shape + mapper in `api/`, clean type in `model/`.
4. `index.ts` exports only what others need.
5. Verify import direction.

Skip the folder when < 3 files. Extend an existing feature instead.

### Type mapping (frontend <> backend)

No codegen. Manual mapping per feature:

```typescript
// features/items/api/items.ts
import { get } from '@/shared/api/client';
import type { Item } from '../model/item';

interface RawItem {
  id: string;
  name: string;
  created_at: string;
}

function mapItem(raw: RawItem): Item {
  return { id: raw.id, name: raw.name, createdAt: raw.created_at };
}

export function listItems(): Promise<Item[]> {
  return get<RawItem[]>('/api/items').then((raw) => raw.map(mapItem));
}
```

Once the API surface grows, replace manual mapping with contract tests. See the testing strategy section in [productionalize.md](productionalize.md) for details on using FastAPI's OpenAPI spec with `openapi-typescript` for compile-time safety.

---

## Local dev

```bash
# 1. Install JS deps
pnpm install

# 2. Python setup (if not already done)
cd api && uv sync && cp .env.example .env && cd ..

# 3. Start both
npx nx run-many -t serve
# API  -> http://localhost:8080
# UI   -> http://localhost:4200 (Vite proxies /api -> :8080)
```
