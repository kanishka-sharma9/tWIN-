import base64
import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta

import jwt

from twin.application.ports.clock import Clock

AUDIENCE = "twin-oauth-state"
LIFETIME = timedelta(minutes=10)


@dataclass(frozen=True)
class OAuthState:
    state: str
    verifier: str


def new_state() -> OAuthState:
    return OAuthState(secrets.token_urlsafe(32), secrets.token_urlsafe(48))


def code_challenge(verifier: str) -> str:
    """The PKCE S256 challenge: base64url(SHA-256(verifier)) without padding."""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


class StateCookie:
    """Signs and reads the short-lived cookie that carries `state` and the PKCE verifier.

    The key is derived from the JWT secret and the token carries its own audience, so a
    cookie can never pass for an access token or the other way round.
    """

    def __init__(self, secret: str, clock: Clock) -> None:
        self._key = hashlib.sha256(f"oauth-state|{secret}".encode()).digest()
        self._clock = clock

    def dump(self, value: OAuthState) -> str:
        now = self._clock.now()
        return jwt.encode(
            {
                "aud": AUDIENCE,
                "st": value.state,
                "cv": value.verifier,
                "exp": int((now + LIFETIME).timestamp()),
            },
            self._key,
            algorithm="HS256",
        )

    def load(self, cookie: str | None) -> OAuthState | None:
        if not cookie:
            return None
        try:
            claims = jwt.decode(
                cookie,
                self._key,
                algorithms=["HS256"],
                audience=AUDIENCE,
                options={"require": ["exp", "st", "cv"], "verify_exp": False},
            )
            if claims["exp"] <= self._clock.now().timestamp():
                return None
            return OAuthState(str(claims["st"]), str(claims["cv"]))
        except jwt.PyJWTError, KeyError, TypeError:
            return None
