from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from app.core.errors import AppError
from app.modules.billing.models import Plan, Subscription
from app.modules.users.models import User
from app.modules.workspaces.service import require_workspace_member


def list_plans(session: Session) -> list[Plan]:
    return session.exec(select(Plan).where(Plan.is_active == True).order_by(Plan.price_monthly)).all()


def get_workspace_subscription(session: Session, workspace_id: UUID, user: User) -> Subscription:
    require_workspace_member(session, workspace_id, user.id)
    subscription = session.exec(select(Subscription).where(Subscription.workspace_id == workspace_id)).first()
    if not subscription:
        raise AppError(code="subscription_not_found", message="Subscription not found", status_code=404)
    return subscription

