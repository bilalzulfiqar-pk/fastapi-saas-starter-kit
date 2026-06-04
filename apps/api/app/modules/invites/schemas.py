from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InviteCreateInput(BaseModel):
    email: EmailStr
    role: str = Field(default="member", pattern="^(owner|admin|member)$")


class InviteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    email: EmailStr
    role: str
    status: str
    expires_at: datetime
    accepted_at: datetime | None
    invite_url: str | None = None
