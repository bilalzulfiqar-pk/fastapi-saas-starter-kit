from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class WorkspaceCreateInput(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    slug: str | None = Field(default=None, min_length=3, max_length=180)


class WorkspaceUpdateInput(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    logo_url: str | None = Field(default=None, max_length=512)


class WorkspaceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    owner_id: UUID
    logo_url: str | None
    created_at: datetime
    updated_at: datetime


class WorkspaceListItem(WorkspaceSummary):
    role: str


class WorkspaceMemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    workspace_id: UUID
    role: str
    joined_at: datetime
    email: EmailStr
    name: str
    avatar_url: str | None


class MemberRoleUpdateInput(BaseModel):
    role: str = Field(pattern="^(owner|admin|member)$")

