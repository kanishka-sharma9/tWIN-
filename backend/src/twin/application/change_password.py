from collections.abc import Callable
from uuid import UUID

from twin.application.ports.clock import Clock
from twin.application.ports.login_limiter import LoginLimiter
from twin.application.ports.password_hasher import PasswordHasher
from twin.application.ports.unit_of_work import UnitOfWork
from twin.application.sessions import hash_token
from twin.domain.password import NoPassword, Password, WrongPassword
from twin.domain.session import RateLimited
from twin.domain.vault import NotAuthenticated


class ChangePassword:
    """Swap the password of a logged-in person and end their other login sessions."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        clock: Clock,
        hasher: PasswordHasher,
        limiter: LoginLimiter,
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._hasher = hasher
        self._limiter = limiter

    def family_of(self, user_id: UUID, raw_token: str | None) -> UUID | None:
        """The login session behind the caller's refresh cookie, if it is theirs and live."""
        if not raw_token:
            return None
        with self._uow_factory() as uow:
            record = uow.refresh_tokens.get_by_hash(hash_token(raw_token))
        if record is None or record.user_id != user_id or record.is_spent:
            return None
        return record.family_id

    def execute(
        self, user_id: UUID, current: str, new: str, keep_family: UUID | None
    ) -> None:
        # Guessing the current password through this route counts like failed logins do.
        key = f"change-password|{user_id}"
        wait = self._limiter.blocked_for(key)
        if wait is not None:
            raise RateLimited(
                "Too many failed attempts. Try again later.", retry_after=wait
            )
        with self._uow_factory() as uow:
            user = uow.users.get_by_id(user_id)
            if user is None:
                raise NotAuthenticated("Log in to continue.")
            if user.password_hash is None:
                raise NoPassword(
                    "This account signs in with Google and has no password to change."
                )
            if not self._hasher.verify(user.password_hash, current):
                self._limiter.record_failure(key)
                raise WrongPassword("The current password is not right.")
            self._limiter.reset(key)
            checked = Password(new)
            uow.users.set_password_hash(user_id, self._hasher.hash(checked.value))
            uow.refresh_tokens.revoke_user_families(
                user_id, keep_family, self._clock.now()
            )
            uow.commit()
