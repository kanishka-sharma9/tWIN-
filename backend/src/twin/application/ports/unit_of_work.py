from types import TracebackType
from typing import Protocol, Self

from twin.application.ports.refresh_token_repository import RefreshTokenRepository
from twin.application.ports.user_repository import UserRepository
from twin.application.ports.vault_repository import VaultRepository


class UnitOfWork(Protocol):
    """One transaction. Leaving the block without `commit()` rolls everything back."""

    @property
    def users(self) -> UserRepository: ...

    @property
    def refresh_tokens(self) -> RefreshTokenRepository: ...

    @property
    def vaults(self) -> VaultRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...
