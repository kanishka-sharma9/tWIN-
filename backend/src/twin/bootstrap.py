"""Composition root: the only place adapters are wired together."""

from fastapi import FastAPI

from twin.adapters.api.router import api_router
from twin.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="tWIN!!")
    app.state.settings = settings
    app.include_router(api_router, prefix="/api")
    return app
