from collections.abc import Callable

from twin.application.ports.clock import Clock
from twin.application.ports.password_hasher import PasswordHasher
from twin.application.ports.unit_of_work import UnitOfWork
from twin.domain.email import Email
from twin.domain.password import NoPassword, NoSuchAccount, Password


class ResetPassword:
    """Set a new password for an account without knowing the old one (developer command).

    Every login session of the account ends, so every device must log in again.
    """

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        clock: Clock,
        hasher: PasswordHasher,
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._hasher = hasher

    def execute(self, email: str, new: str) -> str:
        """Returns the account's email as stored."""
        address = Email(email)
        with self._uow_factory() as uow:
            user = uow.users.get_by_email(address)
            if user is None:
                raise NoSuchAccount("No account with that email.")
            if user.password_hash is None:
                raise NoPassword(
                    "That account signs in with Google and has no password."
                )
            checked = Password(new)
            uow.users.set_password_hash(user.id, self._hasher.hash(checked.value))
            uow.refresh_tokens.revoke_user_families(user.id, None, self._clock.now())
            uow.commit()
            return user.email.value
