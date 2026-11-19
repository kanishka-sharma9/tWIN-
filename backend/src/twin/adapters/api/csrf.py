from urllib.parse import urlsplit

from fastapi import Request

from twin.domain.session import CsrfFailed

REQUIRED_HEADER = "x-requested-with"
REQUIRED_VALUE = "twin"


def require_csrf(request: Request) -> None:
    """Guard for the routes that act on the refresh cookie.

    A cross-site form or `fetch` cannot add a custom header without a CORS preflight (which
    this API never approves), and the `Origin`, when the browser sends one, must belong to the
    host being called. SameSite=Lax on the cookie is the third layer.
    """
    if request.headers.get(REQUIRED_HEADER) != REQUIRED_VALUE:
        raise CsrfFailed("Missing or wrong X-Requested-With header.")
    origin = request.headers.get("origin")
    if origin is None:
        return
    origin_host = urlsplit(origin).hostname
    own_host = urlsplit(f"//{request.headers.get('host', '')}").hostname
    if not origin_host or origin_host != own_host:
        raise CsrfFailed("Cross-site request refused.")
