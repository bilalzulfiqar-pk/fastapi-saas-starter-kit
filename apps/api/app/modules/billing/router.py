from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.modules.auth.service import require_active_user
from app.modules.billing.schemas import PlanResponse, SubscriptionResponse
from app.modules.billing.service import get_workspace_subscription, list_plans
from app.modules.users.models import User

router = APIRouter(tags=["billing"])


@router.get("/billing/plans")
def get_plans(session: Session = Depends(get_session)):
    plans = [PlanResponse.model_validate(plan) for plan in list_plans(session)]
    return {"data": {"plans": plans}}


@router.get("/workspaces/{workspace_id}/subscription")
def get_subscription(
    workspace_id: UUID,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    subscription = get_workspace_subscription(session, workspace_id, current_user)
    return {"data": {"subscription": SubscriptionResponse.model_validate(subscription)}}
