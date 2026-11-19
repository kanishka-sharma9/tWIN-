from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from twin.domain.email import Email
from twin.domain.errors import DomainError


class EmailTaken(DomainError):
    code = "email_taken"


class NotAuthenticated(DomainError):
    code = "unauthorized"


@dataclass(frozen=True)
class User:
    id: UUID
    email: Email
    password_hash: str | None
    google_subject: str | None
    created_at: datetime


@dataclass(frozen=True)
class Vault:
    id: UUID
    owner_id: UUID
    created_at: datetime


@dataclass(frozen=True)
class Folder:
    id: UUID
    vault_id: UUID
    parent_id: UUID | None
    name: str
    created_at: datetime


@dataclass(frozen=True)
class CurrentVault:
    """The vault the request is allowed to touch. Every later query takes its `id`."""

    id: UUID
    owner_id: UUID
    root_folder_id: UUID
