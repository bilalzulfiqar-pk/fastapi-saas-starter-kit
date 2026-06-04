from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UserUpdateInput(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    avatar_url: str | None = Field(default=None, max_length=512)


class ChangePasswordInput(BaseModel):
    current_password: str = Field(min_length=8, max_length=256)
    new_password: str = Field(min_length=8, max_length=256)


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str
    avatar_url: str | None
    is_active: bool

