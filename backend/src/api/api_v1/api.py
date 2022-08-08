from fastapi import APIRouter

from src.api.api_v1.endpoints import (
    login,
    roles,
    users,
    upload,
)

api_router = APIRouter()

api_router.include_router(login.router, tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(upload.router, tags=["upload"])
