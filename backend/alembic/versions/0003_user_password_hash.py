"""Password hash on users (E02-S02).

Revision ID: 0003_user_password_hash
Revises: 0002_users_vaults_folders
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_user_password_hash"
down_revision = "0002_users_vaults_folders"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Null for accounts that have no password (Google sign-in, E02-S04).
    op.add_column("users", sa.Column("password_hash", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "password_hash")
