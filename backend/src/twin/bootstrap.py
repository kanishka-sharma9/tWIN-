"""Composition root: the only place adapters are wired together."""

from fastapi import FastAPI

from twin.adapters.api.errors import register_error_handlers
from twin.adapters.api.router import api_router
from twin.adapters.auth.argon2_hasher import Argon2PasswordHasher
from twin.adapters.auth.null_authenticator import NullAuthenticator
from twin.adapters.persistence.engine import create_db_engine
from twin.adapters.persistence.repositories import SqlUnitOfWork
from twin.adapters.persistence.session import create_session_factory
from twin.adapters.system_clock import SystemClock
from twin.application.create_user import CreateUser
from twin.application.sign_up import SignUp
from twin.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = create_db_engine(settings.database_url)
    app = FastAPI(title="tWIN!!")
    app.state.settings = settings
    session_factory = create_session_factory(engine)
    app.state.session_factory = session_factory
    app.state.uow_factory = lambda: SqlUnitOfWork(session_factory)
    # Authenticates nobody until E02-S03 swaps in real sessions.
    app.state.authenticator = NullAuthenticator()
    app.state.sign_up = SignUp(
        CreateUser(app.state.uow_factory, SystemClock()), Argon2PasswordHasher()
    )
    register_error_handlers(app)
    app.include_router(api_router, prefix="/api")
    return app
