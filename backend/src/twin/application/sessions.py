import hashlib
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID, uuid4

from twin.application.ports.access_tokens import AccessTokenIssuer
from twin.application.ports.clock import Clock
from twin.application.ports.login_limiter import LoginLimiter
from twin.application.ports.password_hasher import PasswordHasher
from twin.application.ports.unit_of_work import UnitOfWork
from twin.domain.email import Email, InvalidEmail
from twin.domain.session import (
    InvalidCredentials,
    InvalidRefreshToken,
    RateLimited,
    RefreshToken,
)
from twin.domain.vault import NotAuthenticated, User

REFRESH_TOKEN_TTL = timedelta(days=30)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@dataclass(frozen=True)
class SessionTokens:
    """What login, signup and refresh hand back: both tokens and the account."""

    access_token: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    user: User


class Sessions:
    """Log in, swap refresh tokens, log out."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        clock: Clock,
        hasher: PasswordHasher,
        access_tokens: AccessTokenIssuer,
        limiter: LoginLimiter,
        refresh_ttl: timedelta = REFRESH_TOKEN_TTL,
    ) -> None:
        self._uow_factory = uow_factory
        self._clock = clock
        self._hasher = hasher
        self._access_tokens = access_tokens
        self._limiter = limiter
        self._refresh_ttl = refresh_ttl
        # Verified against when the email is unknown, so both failures take the same time.
        self._dummy_hash = hasher.hash(secrets.token_urlsafe(16))

    def login(self, email: str, password: str, client: str) -> SessionTokens:
        try:
            parsed: Email | None = Email(email)
        except InvalidEmail:
            parsed = None
        key = f"{parsed.key if parsed else email.strip().lower()}|{client}"
        wait = self._limiter.blocked_for(key)
        if wait is not None:
            raise RateLimited(
                "Too many failed attempts. Try again later.", retry_after=wait
            )
        user = self._find(parsed)
        stored = user.password_hash if user else None
        matches = self._hasher.verify(stored or self._dummy_hash, password)
        if user is None or stored is None or not matches:
            self._limiter.record_failure(key)
            raise InvalidCredentials("Wrong email or password.")
        self._limiter.reset(key)
        return self.start(user)

    def start(self, user: User) -> SessionTokens:
        """Begin a new login session (a new token family) for the user."""
        return self._issue(user.id, uuid4(), None)

    def refresh(self, raw_token: str | None) -> SessionTokens:
        if not raw_token:
            raise InvalidRefreshToken("Log in again.")
        now = self._clock.now()
        with self._uow_factory() as uow:
            current = uow.refresh_tokens.get_by_hash(hash_token(raw_token))
            if current is None:
                raise InvalidRefreshToken("Log in again.")
            if current.is_spent:
                # A token that was already swapped or revoked is being replayed: assume it
                # leaked and end the whole login session.
                uow.refresh_tokens.revoke_family(current.family_id, now)
                uow.commit()
                raise InvalidRefreshToken("Log in again.")
            if current.expires_at <= now:
                raise InvalidRefreshToken("Log in again.")
            return self._issue(current.user_id, current.family_id, current, uow)

    def logout(self, raw_token: str | None) -> None:
        """Revoke the login session behind the token. Unknown tokens are ignored."""
        if not raw_token:
            return
        with self._uow_factory() as uow:
            current = uow.refresh_tokens.get_by_hash(hash_token(raw_token))
            if current is not None:
                uow.refresh_tokens.revoke_family(current.family_id, self._clock.now())
                uow.commit()

    def _find(self, email: Email | None) -> User | None:
        if email is None:
            return None
        with self._uow_factory() as uow:
            return uow.users.get_by_email(email)

    def _issue(
        self,
        user_id: UUID,
        family_id: UUID,
        replaces: RefreshToken | None,
        uow: UnitOfWork | None = None,
    ) -> SessionTokens:
        if uow is None:
            with self._uow_factory() as own:
                return self._issue(user_id, family_id, replaces, own)
        user = uow.users.get_by_id(user_id)
        vault = uow.vaults.get_current(user_id)
        if user is None or vault is None:
            raise NotAuthenticated("Log in to continue.")
        now = self._clock.now()
        raw = secrets.token_urlsafe(32)
        record = RefreshToken(
            id=uuid4(),
            user_id=user_id,
            token_hash=hash_token(raw),
            family_id=family_id,
            expires_at=now + self._refresh_ttl,
            revoked_at=None,
            replaced_by=None,
            created_at=now,
        )
        uow.refresh_tokens.add(record)
        if replaces is not None:
            uow.refresh_tokens.mark_replaced(replaces.id, record.id)
        uow.commit()
        access = self._access_tokens.issue(user_id, vault.id)
        return SessionTokens(
            access_token=access.token,
            expires_in=access.expires_in,
            refresh_token=raw,
            refresh_expires_in=int(self._refresh_ttl.total_seconds()),
            user=user,
        )
