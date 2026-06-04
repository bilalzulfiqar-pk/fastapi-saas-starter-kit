from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.billing.router import router as billing_router
from app.modules.invites.router import router as invites_router
from app.modules.users.router import router as users_router
from app.modules.workspaces.router import router as workspaces_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(workspaces_router)
api_router.include_router(invites_router)
api_router.include_router(billing_router)

