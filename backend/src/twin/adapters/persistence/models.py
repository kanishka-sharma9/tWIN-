"""Declarative base. D-026: 2.0 `select()` style, no lazy loading, no ORM object leaves a repository."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, MetaData, Text, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Constraint names are fixed now because renaming unique indexes later is painful.
NAMING_CONVENTION = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UserRow(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("uq_users_email_lower", func.lower(text("email")), unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str | None] = mapped_column(Text)
    google_subject: Mapped[str | None] = mapped_column(Text, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class VaultRow(Base):
    __tablename__ = "vaults"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class FolderRow(Base):
    __tablename__ = "folders"
    __table_args__ = (
        # Exactly one root (parent_id is null) per vault.
        Index(
            "uq_folders_vault_id_root",
            "vault_id",
            unique=True,
            postgresql_where=text("parent_id is null"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    vault_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vaults.id"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("folders.id"))
    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RefreshTokenRow(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    # SHA-256 of the random token; the token itself is never stored.
    token_hash: Mapped[str] = mapped_column(Text, unique=True)
    family_id: Mapped[uuid.UUID] = mapped_column(index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
