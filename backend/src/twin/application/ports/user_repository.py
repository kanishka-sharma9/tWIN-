from typing import Protocol
from uuid import UUID

from twin.domain.email import Email
from twin.domain.vault import User


class UserRepository(Protocol):
    def add(self, user: User) -> None:
        """Store the user. Raises `EmailTaken` when the email is used, ignoring case."""
        ...

    def get_by_email(self, email: Email) -> User | None: ...

    def get_by_id(self, user_id: UUID) -> User | None: ...
