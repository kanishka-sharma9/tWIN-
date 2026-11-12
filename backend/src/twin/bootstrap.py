"""Composition root: the only place adapters are wired together."""

from fastapi import FastAPI

from twin.adapters.api.router import api_router
from twin.adapters.persistence.engine import create_db_engine
from twin.adapters.persistence.session import create_session_factory
from twin.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = create_db_engine(settings.database_url)
    app = FastAPI(title="tWIN!!")
    app.state.settings = settings
    app.state.session_factory = create_session_factory(engine)
    app.include_router(api_router, prefix="/api")
    return app
