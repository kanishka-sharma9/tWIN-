from datetime import timedelta
from uuid import UUID

import jwt

from twin.application.ports.access_tokens import AccessToken
from twin.application.ports.clock import Clock

ALGORITHM = "HS256"
MIN_SECRET_LENGTH = 32


class JwtAccessTokens:
    """Short-lived HS256 access tokens with claims `sub` (user), `vid` (vault), `iat`, `exp`.

    Implements both `AccessTokenIssuer` and `UserAuthenticator`. Expiry is judged against the
    injected clock, not the system time, so tests can move time.
    """

    def __init__(self, secret: str, clock: Clock, ttl: timedelta) -> None:
        if len(secret) < MIN_SECRET_LENGTH:
            raise ValueError(
                f"TWIN_JWT_SECRET must be at least {MIN_SECRET_LENGTH} characters."
            )
        self._secret = secret
        self._clock = clock
        self._ttl = ttl

    def issue(self, user_id: UUID, vault_id: UUID) -> AccessToken:
        now = self._clock.now()
        claims = {
            "sub": str(user_id),
            "vid": str(vault_id),
            "iat": int(now.timestamp()),
            "exp": int((now + self._ttl).timestamp()),
        }
        token = jwt.encode(claims, self._secret, algorithm=ALGORITHM)
        return AccessToken(token, int(self._ttl.total_seconds()))

    def authenticate(self, authorization: str | None) -> UUID | None:
        scheme, _, token = (authorization or "").partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[ALGORITHM],  # never trust the token's own `alg`
                options={
                    "require": ["sub", "exp", "iat"],
                    "verify_exp": False,
                    "verify_iat": False,
                },
            )
            if claims["exp"] <= self._clock.now().timestamp():
                return None
            return UUID(claims["sub"])
        except jwt.InvalidTokenError, ValueError, TypeError:
            return None
