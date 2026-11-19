import pytest
from tests.fakes.accounts import (
    InMemoryFolders,
    InMemoryUsers,
    InMemoryVaults,
    RecordingUnitOfWork,
)
from tests.fakes.clock import FixedClock
from tests.fakes.security import FakePasswordHasher

from twin.application.create_user import CreateUser
from twin.domain.accounts import EmailTaken, Folder, InvalidEmail, WeakPassword

PASSWORD = "correct horse battery"


def make() -> tuple[
    CreateUser, InMemoryUsers, InMemoryVaults, InMemoryFolders, RecordingUnitOfWork
]:
    users, vaults, folders, uow = (
        InMemoryUsers(),
        InMemoryVaults(),
        InMemoryFolders(),
        RecordingUnitOfWork(),
    )
    return (
        CreateUser(users, vaults, folders, uow, FixedClock(), FakePasswordHasher()),
        users,
        vaults,
        folders,
        uow,
    )


def test_creates_user_with_one_vault_and_a_root_folder() -> None:
    create, users, vaults, folders, uow = make()
    account = create("Ada@Example.com ", PASSWORD)
    assert users.get(account.user.id) == account.user
    assert account.user.email == "Ada@Example.com"
    assert vaults.get_by_owner(account.user.id) == account.vault
    assert folders.get_root(account.vault.id) == account.root
    assert account.root.parent_id is None
    assert uow.commits == 1


def test_email_is_taken_regardless_of_case() -> None:
    create, _, vaults, _, uow = make()
    create("ada@example.com", PASSWORD)
    with pytest.raises(EmailTaken):
        create("ADA@example.com", PASSWORD)
    assert len(vaults.rows) == 1
    assert uow.commits == 1


@pytest.mark.parametrize("bad", ["", "no-at", "@x.com", "a@", "a b@x.com", "a@b@c"])
def test_rejects_malformed_email(bad: str) -> None:
    create, users, _, _, _ = make()
    with pytest.raises(InvalidEmail):
        create(bad, PASSWORD)
    assert not users.rows


class FailingFolders(InMemoryFolders):
    def add(self, folder: Folder) -> None:
        raise RuntimeError("disk")


def test_failure_midway_rolls_back() -> None:
    uow = RecordingUnitOfWork()
    create = CreateUser(
        InMemoryUsers(),
        InMemoryVaults(),
        FailingFolders(),
        uow,
        FixedClock(),
        FakePasswordHasher(),
    )
    with pytest.raises(RuntimeError):
        create("a@b.co", PASSWORD)
    assert uow.rollbacks == 1
    assert uow.commits == 0


def test_stores_a_hash_not_the_password() -> None:
    create, users, *_ = make()
    account = create("ada@example.com", PASSWORD)
    stored = users.get(account.user.id)
    assert stored is not None
    assert stored.password_hash == FakePasswordHasher().hash(PASSWORD)
    assert stored.password_hash != PASSWORD
    assert PASSWORD not in repr(stored)


def test_weak_password_creates_nothing() -> None:
    create, users, vaults, _, uow = make()
    with pytest.raises(WeakPassword):
        create("ada@example.com", "short")
    assert not users.rows
    assert not vaults.rows
    assert uow.commits == 0


def test_duplicate_email_is_reported_before_the_password_is_judged() -> None:
    create, *_ = make()
    create("ada@example.com", PASSWORD)
    with pytest.raises(EmailTaken):
        create("ADA@example.com", PASSWORD)
