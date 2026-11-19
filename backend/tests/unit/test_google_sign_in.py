import pytest
from tests.fakes.clock import FixedClock
from tests.fakes.memory import MemoryStore, MemoryUnitOfWork

from twin.application.create_user import CreateUser
from twin.application.google_sign_in import GoogleSignIn
from twin.application.ports.unit_of_work import UnitOfWork
from twin.domain.identity import AccountExists, ExternalIdentity, IdentityRejected


def make() -> tuple[GoogleSignIn, CreateUser, MemoryStore]:
    store = MemoryStore()

    def factory() -> UnitOfWork:
        return MemoryUnitOfWork(store)

    create = CreateUser(factory, FixedClock())
    return GoogleSignIn(factory, create), create, store


def test_first_sign_in_creates_user_and_vault_without_a_password() -> None:
    sign_in, _, store = make()
    user = sign_in.execute(ExternalIdentity("sub-1", "Ada@Example.com"))
    assert user.google_subject == "sub-1"
    assert user.password_hash is None
    assert len(store.users) == len(store.vaults) == len(store.folders) == 1


def test_second_sign_in_finds_the_same_user_by_subject() -> None:
    sign_in, _, store = make()
    first = sign_in.execute(ExternalIdentity("sub-1", "ada@example.com"))
    again = sign_in.execute(ExternalIdentity("sub-1", "ada@example.com"))
    assert again.id == first.id
    assert len(store.users) == len(store.vaults) == 1


def test_subject_wins_over_a_changed_email() -> None:
    sign_in, _, store = make()
    first = sign_in.execute(ExternalIdentity("sub-1", "ada@example.com"))
    again = sign_in.execute(ExternalIdentity("sub-1", "new-address@example.com"))
    assert again.id == first.id
    assert len(store.users) == 1


@pytest.mark.parametrize("google_email", ["ada@example.com", "ADA@EXAMPLE.COM"])
def test_email_of_a_password_account_is_refused_and_nothing_is_created(
    google_email: str,
) -> None:
    sign_in, create, store = make()
    create.execute("ada@example.com", password_hash="hash")
    with pytest.raises(AccountExists):
        sign_in.execute(ExternalIdentity("sub-9", google_email))
    assert len(store.users) == len(store.vaults) == 1
    assert store.users[0].google_subject is None


def test_email_of_another_google_account_is_refused() -> None:
    sign_in, _, store = make()
    sign_in.execute(ExternalIdentity("sub-1", "ada@example.com"))
    with pytest.raises(AccountExists):
        sign_in.execute(ExternalIdentity("sub-2", "ada@example.com"))
    assert len(store.users) == 1


def test_an_unusable_email_from_the_provider_is_rejected() -> None:
    sign_in, _, store = make()
    with pytest.raises(IdentityRejected):
        sign_in.execute(ExternalIdentity("sub-1", "not an email"))
    assert store.users == []
