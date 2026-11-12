from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session


def get_session(request: Request) -> Iterator[Session]:
    """One session per request; the factory is wired in `bootstrap`."""
    with request.app.state.session_factory() as session:
        yield session
