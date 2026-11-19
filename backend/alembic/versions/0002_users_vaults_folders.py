"""Users, vaults and the root folder (E02-S01).

Revision ID: 0002_users_vaults_folders
Revises: 0001_baseline
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_users_vaults_folders"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    # Case-insensitive uniqueness is enforced by the database, whatever the application does.
    op.create_index(
        "uq_users_email_lower", "users", [sa.text("lower(email)")], unique=True
    )

    op.create_table(
        "vaults",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_vaults"),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name="fk_vaults_owner_id_users"
        ),
        # One vault per account for now (D-009); dropping this constraint allows more later.
        sa.UniqueConstraint("owner_id", name="uq_vaults_owner_id"),
    )

    # Minimal folder storage: E04-S01 adds names rules, sibling uniqueness and the bin.
    op.create_table(
        "folders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("vault_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_folders"),
        sa.ForeignKeyConstraint(
            ["vault_id"], ["vaults.id"], name="fk_folders_vault_id_vaults"
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["folders.id"], name="fk_folders_parent_id_folders"
        ),
    )
    op.create_index("ix_folders_vault_id", "folders", ["vault_id"])
    op.create_index(
        "uq_folders_one_root_per_vault",
        "folders",
        ["vault_id"],
        unique=True,
        postgresql_where=sa.text("parent_id IS NULL"),
    )


def downgrade() -> None:
    op.drop_table("folders")
    op.drop_table("vaults")
    op.drop_table("users")
