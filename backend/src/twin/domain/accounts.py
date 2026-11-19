"""Accounts, their private vault and the vault root folder (D-009)."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from twin.domain.errors import DomainError

ROOT_FOLDER_NAME = "Root"
PASSWORD_MIN_LENGTH = 10
PASSWORD_MAX_LENGTH = 128
EMAIL_MAX_LENGTH = 254


class EmailTaken(DomainError):
    code = "email_taken"


class InvalidEmail(DomainError):
    code = "invalid_email"


class WeakPassword(DomainError):
    code = "weak_password"


class NotAuthenticated(DomainError):
    code = "not_authenticated"


class VaultNotFound(DomainError):
    code = "vault_not_found"


@dataclass(frozen=True)
class User:
    id: UUID
    email: str
    created_at: datetime
    # Null for accounts without a password. Never leaves the server; kept out of repr.
    password_hash: str | None = field(default=None, repr=False)


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
    """Trim and check the shape: one @, a local part, a dotted domain, at most 254 characters."""
    email = raw.strip()
    local, at, domain = email.partition("@")
    labels = domain.split(".")
    if (
        not local
        or not at
        or "@" in domain
        or len(email) > EMAIL_MAX_LENGTH
        or any(c.isspace() or (c.isascii() and not c.isprintable()) for c in email)
        or len(labels) < 2
        or any(not label for label in labels)
    ):
        raise InvalidEmail("Enter a valid email address.")
    return email


def check_password(password: str) -> None:
    """Length rules only (D-030): 10 to 128 characters, no composition rules."""
    if len(password) < PASSWORD_MIN_LENGTH:
        raise WeakPassword(
            f"Use at least {PASSWORD_MIN_LENGTH} characters.",
            details={"min_length": PASSWORD_MIN_LENGTH},
        )
    if len(password) > PASSWORD_MAX_LENGTH:
        raise WeakPassword(
            f"Use at most {PASSWORD_MAX_LENGTH} characters.",
            details={"max_length": PASSWORD_MAX_LENGTH},
        )
