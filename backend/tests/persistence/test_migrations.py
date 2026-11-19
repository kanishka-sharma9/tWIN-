from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text


def _version(url: str) -> str | None:
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            exists = connection.execute(
                text("SELECT to_regclass('alembic_version')")
            ).scalar()
            if exists is None:
                return None
            return connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar()
    finally:
        engine.dispose()


def test_upgrade_downgrade_upgrade(test_database_url: str, alembic_cfg: Config) -> None:
    config = alembic_cfg
    command.upgrade(config, "head")
    assert _version(test_database_url) == "0002_users_vaults_folders"
    command.downgrade(config, "base")
    assert _version(test_database_url) is None
    command.upgrade(config, "head")
    assert _version(test_database_url) == "0002_users_vaults_folders"


def test_models_match_the_migration(test_database_url: str) -> None:
    """Autogenerate finds no difference between the ORM rows and the migrated schema."""
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    from twin.adapters.persistence.models import Base

    engine = create_engine(test_database_url)
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            assert compare_metadata(context, Base.metadata) == []
    finally:
        engine.dispose()
