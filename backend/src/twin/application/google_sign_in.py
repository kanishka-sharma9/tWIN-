from collections.abc import Callable

from twin.application.create_user import CreateUser
from twin.application.ports.unit_of_work import UnitOfWork
from twin.domain.email import Email
from twin.domain.identity import AccountExists, ExternalIdentity
from twin.domain.vault import EmailTaken, User


class GoogleSignIn:
    """Finds or creates the account behind a verified Google identity (D-030: never links)."""

    def __init__(
        self, uow_factory: Callable[[], UnitOfWork], create_user: CreateUser
    ) -> None:
        self._uow_factory = uow_factory
        self._create_user = create_user

    def execute(self, identity: ExternalIdentity) -> User:
        email = Email(identity.email)
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
