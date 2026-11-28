from urllib.parse import urlencode

import httpx
import jwt

from twin.application.ports.clock import Clock
from twin.domain.identity import IdentityRejected, VerifiedIdentity

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
ISSUERS = frozenset({"https://accounts.google.com", "accounts.google.com"})
TIMEOUT_SECONDS = 10.0


def _rejected() -> IdentityRejected:
    return IdentityRejected("Google sign-in did not complete.")


class GoogleIdentityProvider:
    """Google as an `IdentityProvider`: authorization code with PKCE, backend to backend.

    The ID token is verified against Google's published signing keys (RS256, fetched from
    `JWKS_URI` and kept until a token names a key we do not have), then its claims are checked.
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
        self._keys: dict[str, jwt.PyJWK] = {}

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

    def exchange(self, code: str, code_verifier: str) -> VerifiedIdentity:
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
                self._signing_key(id_token),
                algorithms=["RS256"],
                options={"verify_exp": False, "verify_aud": False, "verify_iss": False},
            )
        except httpx.HTTPError, KeyError, ValueError, TypeError, jwt.PyJWTError:
            raise _rejected() from None
        return self._check(claims)

    def _signing_key(self, id_token: str) -> jwt.PyJWK:
        """The RSA public key that Google's key set lists for the token's `kid`."""
        kid = jwt.get_unverified_header(id_token)["kid"]
        if kid not in self._keys:
            response = self._http.get(JWKS_URI)
            response.raise_for_status()
            self._keys = {
                str(key["kid"]): jwt.PyJWK.from_dict(key)
                for key in response.json()["keys"]
            }
        return self._keys[kid]

    def _check(self, claims: dict[str, object]) -> VerifiedIdentity:
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
        return VerifiedIdentity(subject, email)
