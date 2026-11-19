import pytest
from tests.fakes.clock import FixedClock
from tests.fakes.memory import MemoryStore, MemoryUnitOfWork

from twin.application.create_user import CreateUser
from twin.application.ports.unit_of_work import UnitOfWork
from twin.application.sign_up import SignUp
from twin.domain.email import InvalidEmail
from twin.domain.password import WeakPassword
from twin.domain.vault import EmailTaken


class ReversingHasher:
    def hash(self, password: str) -> str:
        return "hashed:" + password[::-1]

    def verify(self, password_hash: str, password: str) -> bool:
        return password_hash == self.hash(password)

    def needs_rehash(self, password_hash: str) -> bool:
        return False


def make() -> tuple[SignUp, MemoryStore]:
    store = MemoryStore()

    def factory() -> UnitOfWork:
        return MemoryUnitOfWork(store)

    return SignUp(CreateUser(factory, FixedClock()), ReversingHasher()), store


def test_sign_up_stores_user_vault_and_a_hash_instead_of_the_password() -> None:
    sign_up, store = make()
    user = sign_up.execute("Ada@Example.com", "a long password")
    assert user.email.value == "Ada@Example.com"
    assert user.password_hash == ReversingHasher().hash("a long password")
    assert len(store.vaults) == 1


def test_weak_password_stores_nothing() -> None:
    sign_up, store = make()
    with pytest.raises(WeakPassword):
        sign_up.execute("ada@example.com", "short")
    assert store.users == []


def test_invalid_email_stores_nothing() -> None:
    sign_up, store = make()
    with pytest.raises(InvalidEmail):
        sign_up.execute("nope", "a long password")
    assert store.users == []


def test_second_sign_up_with_other_case_is_refused() -> None:
    sign_up, store = make()
    sign_up.execute("ada@example.com", "a long password")
    with pytest.raises(EmailTaken):
        sign_up.execute("ADA@example.com", "another long one")
    assert len(store.users) == 1
