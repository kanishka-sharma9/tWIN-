"""Accounts, their private vault and the vault root folder (D-009)."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from twin.domain.errors import DomainError

ROOT_FOLDER_NAME = "Root"


class EmailTaken(DomainError):
    code = "email_taken"


class InvalidEmail(DomainError):
    code = "invalid_email"


class NotAuthenticated(DomainError):
    code = "not_authenticated"


class VaultNotFound(DomainError):
    code = "vault_not_found"


@dataclass(frozen=True)
class User:
    id: UUID
    email: str
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


def clean_email(raw: str) -> str:
    """Trim and check the shape only; signup (E02-S02) owns the fuller rules."""
    email = raw.strip()
    local, at, domain = email.partition("@")
    if not local or not at or not domain or "@" in domain or " " in email:
        raise InvalidEmail("Enter a valid email address.")
    return email
