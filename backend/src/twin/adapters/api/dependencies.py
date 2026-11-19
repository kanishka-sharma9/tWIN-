from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from twin.application.ports.unit_of_work import UnitOfWork
from twin.domain.vault import CurrentVault, NotAuthenticated, User

# Declares the bearer scheme in OpenAPI so Swagger UI offers an Authorize button. It never
# refuses a request itself (`auto_error=False`); the authenticator reads the header.
bearer_scheme = HTTPBearer(auto_error=False, description="The access token from login.")


def get_session(request: Request) -> Iterator[Session]:
    """One session per request; the factory is wired in `bootstrap`."""
    with request.app.state.session_factory() as session:
        yield session


def get_uow(request: Request) -> Iterator[UnitOfWork]:
    """One transaction per request; `app.state.uow_factory` is wired in `bootstrap`."""
    with request.app.state.uow_factory() as uow:
        yield uow


def get_current_vault(
    request: Request,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    authorization: Annotated[str | None, Header()] = None,
    _scheme: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> CurrentVault:
    """The vault of the caller. Every vault-scoped query takes its `id`.

    Later stories declare this dependency on each route, so a request can only ever reach
    the vault that its own login owns.
    """
    owner_id = request.app.state.authenticator.authenticate(authorization)
    vault = uow.vaults.get_current(owner_id) if owner_id else None
    if vault is None:
        raise NotAuthenticated("Log in to continue.")
    return vault


def get_current_user(
    request: Request,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    authorization: Annotated[str | None, Header()] = None,
    _scheme: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> User:
    """The account behind the bearer token; 401 when the token is missing, bad or expired."""
    user_id = request.app.state.authenticator.authenticate(authorization)
    user = uow.users.get_by_id(user_id) if user_id else None
    if user is None:
        raise NotAuthenticated("Log in to continue.")
    return user
