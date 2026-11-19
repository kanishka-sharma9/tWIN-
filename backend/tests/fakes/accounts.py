from uuid import UUID

from twin.domain.accounts import EmailTaken, Folder, User, Vault


class InMemoryUsers:
    def __init__(self) -> None:
        self.rows: dict[UUID, User] = {}

    def add(self, user: User) -> None:
        if self.get_by_email(user.email) is not None:
            raise EmailTaken("An account with this email already exists.")
        self.rows[user.id] = user

    def get(self, user_id: UUID) -> User | None:
        return self.rows.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next(
            (u for u in self.rows.values() if u.email.lower() == email.lower()), None
        )


class InMemoryVaults:
    def __init__(self) -> None:
        self.rows: dict[UUID, Vault] = {}

    def add(self, vault: Vault) -> None:
        self.rows[vault.id] = vault

    def get_by_owner(self, owner_id: UUID) -> Vault | None:
        return next((v for v in self.rows.values() if v.owner_id == owner_id), None)


class InMemoryFolders:
    def __init__(self) -> None:
        self.rows: dict[UUID, Folder] = {}

    def add(self, folder: Folder) -> None:
        self.rows[folder.id] = folder

    def get(self, vault_id: UUID, folder_id: UUID) -> Folder | None:
        folder = self.rows.get(folder_id)
        return folder if folder and folder.vault_id == vault_id else None

    def get_root(self, vault_id: UUID) -> Folder | None:
        return next(
            (
                f
                for f in self.rows.values()
                if f.vault_id == vault_id and f.parent_id is None
            ),
            None,
        )


class RecordingUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1
