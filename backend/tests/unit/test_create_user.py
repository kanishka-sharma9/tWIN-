import pytest
from tests.fakes.clock import FixedClock
from tests.fakes.memory import MemoryStore, MemoryUnitOfWork

from twin.application.create_user import CreateUser
from twin.application.ports.unit_of_work import UnitOfWork
from twin.domain.email import InvalidEmail
from twin.domain.vault import EmailTaken


def make() -> tuple[CreateUser, MemoryStore]:
    store = MemoryStore()

    def factory() -> UnitOfWork:
        return MemoryUnitOfWork(store)

    return CreateUser(factory, FixedClock()), store


def test_new_user_has_exactly_one_vault_with_one_root_folder() -> None:
    create_user, store = make()
    user = create_user.execute("ada@example.com", password_hash="hash")
    assert [v.owner_id for v in store.vaults] == [user.id]
    vault = store.vaults[0]
    roots = [f for f in store.folders if f.vault_id == vault.id]
    assert len(roots) == 1
    assert roots[0].parent_id is None


def test_each_user_gets_their_own_vault() -> None:
    create_user, store = make()
    a = create_user.execute("a@example.com", password_hash="h")
    b = create_user.execute("b@example.com", google_subject="sub-1")
    assert {v.owner_id for v in store.vaults} == {a.id, b.id}
    assert len({v.id for v in store.vaults}) == 2


def test_email_is_taken_ignoring_case_and_nothing_is_stored_twice() -> None:
    create_user, store = make()
    create_user.execute("Ada@Example.com", password_hash="h")
    with pytest.raises(EmailTaken) as raised:
        create_user.execute("ada@example.COM", google_subject="g")
    assert raised.value.code == "email_taken"
    assert len(store.users) == len(store.vaults) == len(store.folders) == 1


def test_invalid_email_stores_nothing() -> None:
    create_user, store = make()
    with pytest.raises(InvalidEmail):
        create_user.execute("nope", password_hash="h")
    assert store.users == []


def test_a_credential_is_required() -> None:
    create_user, _ = make()
    with pytest.raises(ValueError, match="password hash or a Google subject"):
        create_user.execute("ada@example.com")
    with pytest.raises(ValueError, match="password hash or a Google subject"):
        create_user.execute("ada@example.com", password_hash="")
