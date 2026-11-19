"""Declarative base. D-026: 2.0 `select()` style, no lazy loading, no ORM object leaves a repository."""

from datetime import datetime
from uuid import UUID

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


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # The database refuses two emails that differ only by case (see migration 0002).
    __table_args__ = (Index("uq_users_email_lower", func.lower(email), unique=True),)


class VaultModel(Base):
    __tablename__ = "vaults"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class FolderModel(Base):
    __tablename__ = "folders"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    vault_id: Mapped[UUID] = mapped_column(ForeignKey("vaults.id"), index=True)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("folders.id"))
    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index(
            "uq_folders_one_root_per_vault",
            "vault_id",
            unique=True,
            postgresql_where=text("parent_id IS NULL"),
        ),
    )
