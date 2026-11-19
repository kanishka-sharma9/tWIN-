from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from twin.adapters.persistence.accounts import (
    SqlFolderRepository,
    SqlUserRepository,
    SqlVaultRepository,
)
from twin.application.ports.accounts import UserAuthenticator, VaultRepository
from twin.domain.accounts import NotAuthenticated, Vault, VaultNotFound


def get_session(request: Request) -> Iterator[Session]:
    """One session per request; the factory is wired in `bootstrap`."""
    with request.app.state.session_factory() as session:
        yield session


def get_user_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SqlUserRepository:
    return SqlUserRepository(session)


def get_vault_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SqlVaultRepository:
    return SqlVaultRepository(session)


def get_folder_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SqlFolderRepository:
    return SqlFolderRepository(session)


def get_current_user_id(
    request: Request, authorization: Annotated[str | None, Header()] = None
) -> UUID:
    """The caller, as reported by the authenticator port wired in `bootstrap`."""
    authenticator: UserAuthenticator = request.app.state.authenticator
    user_id = authenticator.authenticate(authorization)
    if user_id is None:
        raise NotAuthenticated("Log in to continue.")
    return user_id


def get_current_vault(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    vaults: Annotated[VaultRepository, Depends(get_vault_repository)],
) -> Vault:
    """The caller vault. Every later query is scoped by `vault.id` taken from here, never from input."""
    vault = vaults.get_by_owner(user_id)
    if vault is None:
        raise VaultNotFound("This account has no vault.")
    return vault
