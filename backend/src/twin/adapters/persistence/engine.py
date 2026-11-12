from sqlalchemy import Engine, create_engine


def create_db_engine(database_url: str) -> Engine:
    """Synchronous engine (D-026). It connects lazily, so building it never fails."""
    return create_engine(
        database_url, pool_pre_ping=True, connect_args={"connect_timeout": 2}
    )
