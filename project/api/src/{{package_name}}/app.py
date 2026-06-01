import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI()

    cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins.split(","),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health_router, prefix="/api")
    return app
