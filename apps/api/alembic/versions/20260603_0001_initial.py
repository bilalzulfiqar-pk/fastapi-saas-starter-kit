"""Initial starter schema."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260603_0001"
down_revision = None
branch_labels = None
depends_on = None


def _uuid_type() -> sa.types.TypeEngine:
    return postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", _uuid_type(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "plans",
        sa.Column("id", _uuid_type(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("price_monthly", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price_yearly", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("features_json", sa.JSON(), nullable=False),
        sa.Column("limits_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_plans_slug", "plans", ["slug"], unique=True)

    op.create_table(
        "workspaces",
        sa.Column("id", _uuid_type(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("owner_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("logo_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workspaces_owner_id", "workspaces", ["owner_id"], unique=False)
    op.create_index("ix_workspaces_slug", "workspaces", ["slug"], unique=True)

    op.create_table(
        "workspace_members",
        sa.Column("id", _uuid_type(), primary_key=True, nullable=False),
        sa.Column("workspace_id", _uuid_type(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_members_workspace_user"),
    )
    op.create_index("ix_workspace_members_workspace_id", "workspace_members", ["workspace_id"], unique=False)
    op.create_index("ix_workspace_members_user_id", "workspace_members", ["user_id"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", _uuid_type(), primary_key=True, nullable=False),
        sa.Column("user_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("ip_address", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)

    op.create_table(
        "workspace_invites",
        sa.Column("id", _uuid_type(), primary_key=True, nullable=False),
        sa.Column("workspace_id", _uuid_type(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("invited_by_user_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workspace_invites_workspace_id", "workspace_invites", ["workspace_id"], unique=False)
    op.create_index("ix_workspace_invites_email", "workspace_invites", ["email"], unique=False)
    op.create_index("ix_workspace_invites_token_hash", "workspace_invites", ["token_hash"], unique=True)
    op.execute(
        "CREATE UNIQUE INDEX uq_workspace_invites_pending_email ON workspace_invites (workspace_id, email) WHERE status = 'pending'"
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", _uuid_type(), primary_key=True, nullable=False),
        sa.Column("workspace_id", _uuid_type(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("plan_id", _uuid_type(), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("workspace_id", name="uq_subscriptions_workspace_id"),
    )
    op.create_index("ix_subscriptions_workspace_id", "subscriptions", ["workspace_id"], unique=True)
    op.create_index("ix_subscriptions_plan_id", "subscriptions", ["plan_id"], unique=False)

    plans_table = sa.table(
        "plans",
        sa.column("id", _uuid_type()),
        sa.column("name", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("price_monthly", sa.Integer()),
        sa.column("price_yearly", sa.Integer()),
        sa.column("features_json", sa.JSON()),
        sa.column("limits_json", sa.JSON()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    now = datetime.now(UTC)
    op.bulk_insert(
        plans_table,
        [
            {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "name": "Free",
                "slug": "free",
                "price_monthly": 0,
                "price_yearly": 0,
                "features_json": {},
                "limits_json": {},
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": UUID("22222222-2222-2222-2222-222222222222"),
                "name": "Pro",
                "slug": "pro",
                "price_monthly": 2900,
                "price_yearly": 29000,
                "features_json": {},
                "limits_json": {},
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": UUID("33333333-3333-3333-3333-333333333333"),
                "name": "Business",
                "slug": "business",
                "price_monthly": 9900,
                "price_yearly": 99000,
                "features_json": {},
                "limits_json": {},
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_subscriptions_plan_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_workspace_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("uq_workspace_invites_pending_email", table_name="workspace_invites")
    op.drop_index("ix_workspace_invites_token_hash", table_name="workspace_invites")
    op.drop_index("ix_workspace_invites_email", table_name="workspace_invites")
    op.drop_index("ix_workspace_invites_workspace_id", table_name="workspace_invites")
    op.drop_table("workspace_invites")

    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("ix_workspace_members_user_id", table_name="workspace_members")
    op.drop_index("ix_workspace_members_workspace_id", table_name="workspace_members")
    op.drop_table("workspace_members")

    op.drop_index("ix_workspaces_slug", table_name="workspaces")
    op.drop_index("ix_workspaces_owner_id", table_name="workspaces")
    op.drop_table("workspaces")

    op.drop_index("ix_plans_slug", table_name="plans")
    op.drop_table("plans")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
