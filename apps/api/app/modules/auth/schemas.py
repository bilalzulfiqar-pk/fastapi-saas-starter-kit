from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    name: str = Field(min_length=1, max_length=120)


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    name: str
    avatar_url: str | None = None
    email_verified_at: datetime | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None

