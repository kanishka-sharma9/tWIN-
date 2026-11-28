from collections.abc import Iterator
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from twin.adapters.persistence.models import (
    FolderRow,
    RefreshTokenRow,
    UserRow,
    VaultRow,
)
from twin.settings import Settings


@pytest.fixture
def email(settings: Settings) -> Iterator[str]:
    """A unique address; the account it creates is removed afterwards."""
    address = f"Ada-{uuid4().hex}@Example.com"
    yield address
    engine = create_engine(settings.database_url)
    with Session(engine) as session, session.begin():
        ids = list(session.scalars(select(UserRow.id).where(UserRow.email == address)))
        vaults = list(
            session.scalars(select(VaultRow.id).where(VaultRow.owner_id.in_(ids)))
        )
        session.execute(
            delete(RefreshTokenRow)
            .where(RefreshTokenRow.user_id.in_(ids))
            .execution_options(synchronize_session=False)
        )
        session.execute(delete(FolderRow).where(FolderRow.vault_id.in_(vaults)))
        session.execute(delete(VaultRow).where(VaultRow.owner_id.in_(ids)))
        session.execute(delete(UserRow).where(UserRow.id.in_(ids)))
    engine.dispose()
