from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.security import utcnow


class Workspace(SQLModel, table=True):
    __tablename__ = "workspaces"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=160)
    slug: str = Field(index=True, unique=True, max_length=180)
    owner_id: UUID = Field(foreign_key="users.id", index=True)
    logo_url: str | None = Field(default=None, max_length=512)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class WorkspaceMember(SQLModel, table=True):
    __tablename__ = "workspace_members"
    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="uq_workspace_members_workspace_user"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspaces.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: str = Field(default="member", max_length=32)
    joined_at: datetime = Field(default_factory=utcnow)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

