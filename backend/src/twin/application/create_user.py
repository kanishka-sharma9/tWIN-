from dataclasses import dataclass
from uuid import uuid4

from twin.application.ports.accounts import (
    FolderRepository,
    UnitOfWork,
    UserRepository,
    VaultRepository,
)
from twin.application.ports.clock import Clock
from twin.application.ports.security import PasswordHasher
from twin.domain.accounts import (
    ROOT_FOLDER_NAME,
    EmailTaken,
    Folder,
    User,
    Vault,
    check_password,
    clean_email,
)


@dataclass(frozen=True)
class NewAccount:
    user: User
    vault: Vault
    root: Folder


class CreateUser:
    """Creates the user, their one vault and its root folder in a single transaction."""

    def __init__(
        self,
        users: UserRepository,
        vaults: VaultRepository,
        folders: FolderRepository,
        uow: UnitOfWork,
        clock: Clock,
        hasher: PasswordHasher,
    ) -> None:
        self._users = users
        self._vaults = vaults
        self._folders = folders
        self._uow = uow
        self._clock = clock
        self._hasher = hasher

    def __call__(self, email: str, password: str) -> NewAccount:
        email = clean_email(email)
        check_password(password)
        if self._users.get_by_email(email) is not None:
            raise EmailTaken("An account with this email already exists.")
        now = self._clock.now()
        user = User(
            id=uuid4(),
            email=email,
            created_at=now,
            password_hash=self._hasher.hash(password),
        )
        vault = Vault(id=uuid4(), owner_id=user.id, created_at=now)
        root = Folder(
            id=uuid4(),
            vault_id=vault.id,
            parent_id=None,
            name=ROOT_FOLDER_NAME,
            created_at=now,
        )
        try:
            self._users.add(user)
            self._vaults.add(vault)
            self._folders.add(root)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return NewAccount(user=user, vault=vault, root=root)
