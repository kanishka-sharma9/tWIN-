from urllib.parse import urlencode

import httpx
import jwt

from twin.application.ports.clock import Clock
from twin.domain.identity import ExternalIdentity, IdentityRejected

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
ISSUERS = frozenset({"https://accounts.google.com", "accounts.google.com"})
TIMEOUT_SECONDS = 10.0


def _rejected() -> IdentityRejected:
    return IdentityRejected("Google sign-in did not complete.")


class GoogleIdentityProvider:
    """Google as an `IdentityProvider`: authorization code with PKCE, backend to backend.

    The ID token comes straight from the token endpoint over TLS in answer to our own
    request, so its signature is not checked (OpenID Connect Core 3.1.3.7); its claims are.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        clock: Clock,
        client: httpx.Client | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._clock = clock
        self._http = client or httpx.Client(timeout=TIMEOUT_SECONDS)

    def authorization_url(self, state: str, code_challenge: str) -> str:
        query = urlencode(
            {
                "client_id": self._client_id,
                "redirect_uri": self._redirect_uri,
                "response_type": "code",
                "scope": "openid email",
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "prompt": "select_account",
            }
        )
        return f"{AUTHORIZATION_ENDPOINT}?{query}"

    def exchange(self, code: str, code_verifier: str) -> ExternalIdentity:
        try:
            response = self._http.post(
                TOKEN_ENDPOINT,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "code_verifier": code_verifier,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "redirect_uri": self._redirect_uri,
                },
            )
            response.raise_for_status()
            id_token = response.json()["id_token"]
            claims = jwt.decode(
                id_token,
                options={"verify_signature": False, "verify_exp": False},
            )
        except httpx.HTTPError, KeyError, ValueError, TypeError, jwt.PyJWTError:
            raise _rejected() from None
        return self._check(claims)

    def _check(self, claims: dict[str, object]) -> ExternalIdentity:
        exp = claims.get("exp")
        audience = claims.get("aud")
        subject = claims.get("sub")
        email = claims.get("email")
        if not (
            claims.get("iss") in ISSUERS
            and (
                audience == self._client_id
                or (isinstance(audience, list) and self._client_id in audience)
            )
            and isinstance(exp, int | float)
            and exp > self._clock.now().timestamp()
            and claims.get("email_verified") is True
            and isinstance(subject, str)
            and subject
            and isinstance(email, str)
            and email
        ):
            raise _rejected()
        return ExternalIdentity(subject, email)
