from collections.abc import Callable
from uuid import uuid4

from twin.application.ports.clock import Clock
from twin.application.ports.unit_of_work import UnitOfWork
from twin.domain.email import Email
from twin.domain.vault import EmailTaken, Folder, User, Vault

ROOT_FOLDER_NAME = "Home"


class CreateUser:
    """Creates a user, their one vault and its root folder in a single transaction."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork], clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(
        self,
        email: str,
        *,
        password_hash: str | None = None,
        google_subject: str | None = None,
    ) -> User:
        if not password_hash and not google_subject:
            raise ValueError("A user needs a password hash or a Google subject.")
        parsed = Email(email)
        now = self._clock.now()
        user = User(uuid4(), parsed, password_hash, google_subject, now)
        vault = Vault(uuid4(), user.id, now)
        root = Folder(uuid4(), vault.id, None, ROOT_FOLDER_NAME, now)
        with self._uow_factory() as uow:
            if uow.users.get_by_email(parsed) is not None:
                raise EmailTaken(
                    "An account with this email already exists.",
                    details={"field": "email"},
                )
            uow.users.add(user)
            uow.vaults.add(vault, root)
            uow.commit()
        return user
