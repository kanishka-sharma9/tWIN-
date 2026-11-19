from collections.abc import Callable

from twin.application.create_user import CreateUser
from twin.application.ports.unit_of_work import UnitOfWork
from twin.domain.email import Email, InvalidEmail
from twin.domain.identity import AccountExists, IdentityRejected, VerifiedIdentity
from twin.domain.vault import EmailTaken, User


class SignInWithGoogle:
    """Finds or creates the account behind a verified Google identity (D-030: never links)."""

    def __init__(
        self, uow_factory: Callable[[], UnitOfWork], create_user: CreateUser
    ) -> None:
        self._uow_factory = uow_factory
        self._create_user = create_user

    def execute(self, identity: VerifiedIdentity) -> User:
        try:
            email = Email(identity.email)
        except InvalidEmail as error:
            raise IdentityRejected("Google sign-in did not complete.") from error
        with self._uow_factory() as uow:
            known = uow.users.get_by_google_subject(identity.subject)
            if known is not None:
                return known
            if uow.users.get_by_email(email) is not None:
                raise AccountExists("An account with this email already exists.")
        try:
            return self._create_user.execute(
                email.value, google_subject=identity.subject
            )
        except EmailTaken as error:
            # Lost a race with a signup for the same email.
            raise AccountExists("An account with this email already exists.") from error
