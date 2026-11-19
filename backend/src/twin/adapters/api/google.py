import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from twin.adapters.api.auth import get_sessions, set_refresh_cookie
from twin.adapters.auth.oauth_state import (
    OAuthState,
    StateCookie,
    code_challenge,
    new_state,
)
from twin.application.google_sign_in import GoogleSignIn
from twin.application.ports.identity_provider import IdentityProvider
from twin.application.sessions import Sessions
from twin.domain.identity import AccountExists, IdentityRejected, ProviderDisabled
from twin.settings import Settings

router = APIRouter(prefix="/auth", tags=["auth"])

STATE_COOKIE = "oauth_state"
STATE_COOKIE_PATH = "/api/auth/google"
STATE_COOKIE_SECONDS = 600


class Providers(BaseModel):
    google: bool


def _provider(request: Request) -> IdentityProvider:
    provider: IdentityProvider | None = request.app.state.identity_provider
    if provider is None:
        raise ProviderDisabled("Google sign-in is not set up on this server.")
    return provider


def _redirect(path: str) -> RedirectResponse:
    response = RedirectResponse(path, status_code=302)
    response.headers["Cache-Control"] = "no-store"
    response.delete_cookie(STATE_COOKIE, path=STATE_COOKIE_PATH)
    return response


@router.get("/providers")
def providers(request: Request) -> Providers:
    return Providers(google=request.app.state.identity_provider is not None)


@router.get("/google/start", status_code=302, response_class=RedirectResponse)
def google_start(
    request: Request, provider: Annotated[IdentityProvider, Depends(_provider)]
) -> RedirectResponse:
    settings: Settings = request.app.state.settings
    cookie: StateCookie = request.app.state.state_cookie
    flow = new_state()
    response = RedirectResponse(
        provider.authorization_url(flow.state, code_challenge(flow.verifier)),
        status_code=302,
    )
    response.headers["Cache-Control"] = "no-store"
    response.set_cookie(
        STATE_COOKIE,
        cookie.dump(flow),
        max_age=STATE_COOKIE_SECONDS,
        path=STATE_COOKIE_PATH,
        httponly=True,
        samesite="lax",  # the callback is a top-level navigation from Google
        secure=settings.cookie_secure,
    )
    return response


@router.get("/google/callback", status_code=302, response_class=RedirectResponse)
def google_callback(
    request: Request,
    provider: Annotated[IdentityProvider, Depends(_provider)],
    sessions: Annotated[Sessions, Depends(get_sessions)],
    code: str | None = None,
    state: str | None = None,
    oauth_state: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    cookie: StateCookie = request.app.state.state_cookie
    sign_in: GoogleSignIn = request.app.state.google_sign_in
    flow: OAuthState | None = cookie.load(oauth_state)
    # `error=access_denied` (the person said no) arrives without a code and lands here too.
    if (
        flow is None
        or not code
        or not state
        or not secrets.compare_digest(flow.state, state)
    ):
        return _redirect("/login?error=google_failed")
    try:
        user = sign_in.execute(provider.exchange(code, flow.verifier))
    except AccountExists:
        return _redirect("/login?error=account_exists")
    except IdentityRejected:
        return _redirect("/login?error=google_failed")
    response = _redirect("/")
    set_refresh_cookie(request, response, sessions.start(user))
    return response
