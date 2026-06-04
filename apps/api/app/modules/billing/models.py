from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.security import utcnow


class Plan(SQLModel, table=True):
    __tablename__ = "plans"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=100)
    slug: str = Field(index=True, unique=True, max_length=64)
    price_monthly: int = 0
    price_yearly: int = 0
    features_json: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    limits_json: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("workspace_id", name="uq_subscriptions_workspace_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspaces.id", unique=True, index=True)
    plan_id: UUID = Field(foreign_key="plans.id", index=True)
    status: str = Field(default="active", max_length=32)
    stripe_customer_id: str | None = Field(default=None, max_length=255)
    stripe_subscription_id: str | None = Field(default=None, max_length=255)
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    cancel_at_period_end: bool = False
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

