from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.security import refresh_token_expiry, utcnow


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(index=True, unique=True, max_length=64)
    expires_at: datetime = Field(default_factory=refresh_token_expiry)
    revoked_at: datetime | None = None
    user_agent: str | None = Field(default=None, max_length=512)
    ip_address: str | None = Field(default=None, max_length=128)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

