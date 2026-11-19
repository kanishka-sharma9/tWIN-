from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from twin.application.ports.unit_of_work import UnitOfWork
from twin.domain.vault import CurrentVault, NotAuthenticated


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
