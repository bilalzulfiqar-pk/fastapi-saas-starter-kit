from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.security import utcnow


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column("email", String(320), nullable=False, unique=True, index=True))
    name: str = Field(max_length=120)
    avatar_url: str | None = Field(default=None, max_length=512)
    password_hash: str = Field(max_length=512)
    email_verified_at: datetime | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    last_login_at: datetime | None = None

