from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Index, text
from sqlmodel import Field, SQLModel

from app.core.security import utcnow


class WorkspaceInvite(SQLModel, table=True):
    __tablename__ = "workspace_invites"
    __table_args__ = (
        Index(
            "uq_workspace_invites_pending_email",
            "workspace_id",
            "email",
            unique=True,
            postgresql_where=text("status = 'pending'"),
            sqlite_where=text("status = 'pending'"),
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspaces.id", index=True)
    email: str = Field(index=True, max_length=320)
    role: str = Field(default="member", max_length=32)
    token_hash: str = Field(index=True, unique=True, max_length=64)
    invited_by_user_id: UUID = Field(foreign_key="users.id", index=True)
    status: str = Field(default="pending", max_length=32)
    expires_at: datetime
    accepted_at: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

