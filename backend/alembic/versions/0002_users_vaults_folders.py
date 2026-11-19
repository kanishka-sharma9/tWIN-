"""Users, vaults and folders (E02-S01).

Revision ID: 0002_users_vaults_folders
Revises: 0001_baseline
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_users_vaults_folders"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def _created_at() -> sa.Column[sa.DateTime]:
    return sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("google_subject", sa.Text(), nullable=True),
        _created_at(),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("google_subject", name="uq_users_google_subject"),
    )
    op.create_index(
        "uq_users_email_lower", "users", [sa.text("lower(email)")], unique=True
    )

    op.create_table(
        "vaults",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("id", name="pk_vaults"),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name="fk_vaults_owner_id_users"
        ),
        sa.UniqueConstraint("owner_id", name="uq_vaults_owner_id"),
    )

    op.create_table(
        "folders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vault_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("id", name="pk_folders"),
        sa.ForeignKeyConstraint(
            ["vault_id"], ["vaults.id"], name="fk_folders_vault_id_vaults"
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["folders.id"], name="fk_folders_parent_id_folders"
        ),
    )
    op.create_index(
        "uq_folders_vault_id_root",
        "folders",
        ["vault_id"],
        unique=True,
        postgresql_where=sa.text("parent_id is null"),
    )


def downgrade() -> None:
    op.drop_table("folders")
    op.drop_table("vaults")
    op.drop_table("users")
