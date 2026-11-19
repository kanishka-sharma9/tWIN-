from twin.application.create_user import CreateUser
from twin.application.ports.password_hasher import PasswordHasher
from twin.domain.email import Email
from twin.domain.password import Password
from twin.domain.vault import User


class SignUp:
    """Creates an account (user, vault, root folder) from an email and a password."""

    def __init__(self, create_user: CreateUser, hasher: PasswordHasher) -> None:
        self._create_user = create_user
        self._hasher = hasher

    def execute(self, email: str, password: str) -> User:
        parsed = Email(email)
        checked = Password(password)
        return self._create_user.execute(
            parsed.value, password_hash=self._hasher.hash(checked.value)
        )
