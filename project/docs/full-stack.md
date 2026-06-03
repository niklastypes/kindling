# Full-Stack Guide

This project was scaffolded as a full-stack app with Vue 3 + FastAPI + Nx. The monorepo structure, Nx wiring, Vite proxy, and FastAPI health endpoint are already set up. This guide covers conventions and patterns for building on top of the scaffold.

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
