"""Composition root: the only place adapters are wired together."""

from datetime import timedelta

from fastapi import FastAPI

from twin.adapters.api.errors import register_error_handlers
from twin.adapters.api.router import api_router
from twin.adapters.auth.argon2_hasher import Argon2PasswordHasher
from twin.adapters.auth.google_identity import GoogleIdentityProvider
from twin.adapters.auth.jwt_tokens import JwtAccessTokens
from twin.adapters.auth.oauth_state import StateCookie
from twin.adapters.persistence.engine import create_db_engine
from twin.adapters.persistence.repositories import SqlUnitOfWork
from twin.adapters.persistence.session import create_session_factory
from twin.adapters.ratelimit.memory_login_limiter import MemoryLoginLimiter
from twin.adapters.system_clock import SystemClock
from twin.application.create_user import CreateUser
from twin.application.ports.identity_provider import IdentityProvider
from twin.application.sessions import Sessions
from twin.application.sign_in_with_google import SignInWithGoogle
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
    if settings.jwt_secret is None:
        raise RuntimeError(
            "Set TWIN_JWT_SECRET (at least 32 characters) to start the API."
        )
    clock = SystemClock()
    hasher = Argon2PasswordHasher()
    tokens = JwtAccessTokens(
        settings.jwt_secret.get_secret_value(),
        clock,
        timedelta(minutes=settings.access_token_minutes),
    )
    # One object plays both ports: it issues access tokens and reads them back.
    app.state.authenticator = tokens
    app.state.sign_up = SignUp(CreateUser(app.state.uow_factory, clock), hasher)
    app.state.sessions = Sessions(
        app.state.uow_factory,
        clock,
        hasher,
        tokens,
        MemoryLoginLimiter(clock),
        timedelta(days=settings.refresh_token_days),
    )
    create_user = CreateUser(app.state.uow_factory, clock)
    app.state.sign_in_with_google = SignInWithGoogle(app.state.uow_factory, create_user)
    app.state.state_cookie = StateCookie(settings.jwt_secret.get_secret_value(), clock)
    # None switches Google sign-in off: the routes answer 404 and /providers says false.
    identity_provider: IdentityProvider | None = None
    if (
        settings.google_enabled
        and settings.google_client_id
        and settings.google_client_secret
    ):
        identity_provider = GoogleIdentityProvider(
            settings.google_client_id,
            settings.google_client_secret.get_secret_value(),
            settings.google_redirect_uri,
            clock,
        )
    app.state.identity_provider = identity_provider
    register_error_handlers(app)
    app.include_router(api_router, prefix="/api")
    return app
