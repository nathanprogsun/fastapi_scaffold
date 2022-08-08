from typing import Generator

from fastapi import Depends, Security
from fastapi.logger import logger
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src import crud, models, schemas
from src.api.errors.errors import (
    InactiveUser,
    InvalidScope,
    InvalidToken,
    UserNotFound,
)
from src.config import settings
from src.constants import Roles
from src.db.session import SessionLocal
from src.utils import cache as app_cache
from src.utils import security
from src.utils.security import verify_api_key

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    scopes={role.name: role.description for role in [Roles.NORMAL, Roles.ADMIN, Roles.SUPER_ADMIN]},
)

API_KEY_NAME = "api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, scheme_name="API key header", auto_error=False)


# apikey approach
def api_key_security(header_param: str = Security(api_key_header)) -> str:
    if header_param and verify_api_key(header_param):
        return header_param
    else:
        raise InvalidToken()


# OAuth2 approach
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
        security_scopes: SecurityScopes,
        db: Session = Depends(get_db),
        token: str = Depends(reusable_oauth2),
) -> models.User:
    try:
        print(token)
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
    except(jwt.JWTError, ValidationError):
        logger.exception("Invalid JWT token")
        raise InvalidToken()
    user = crud.user.get(db, id=token_data.id)
    if not user:
        raise UserNotFound()
    current_role = min(
        getattr(schemas.UserRole, token_data.role),
        schemas.UserRole(user.role),
    )
    if security_scopes.scopes and current_role.name not in security_scopes.scopes:
        logger.error(
            "Invalid JWT token scope: %s not in %s",
            current_role.name,
            security_scopes.scopes,
        )
        raise InvalidScope()
    return user


def get_current_active_user(
        current_user: models.User = Security(get_current_user, scopes=[]),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise InactiveUser()
    return current_user


def get_current_active_admin(
        current_user: models.User = Security(get_current_user, scopes=[Roles.ADMIN.name, Roles.SUPER_ADMIN.name]),
) -> models.User:
    return current_user


def get_current_active_super_admin(
        current_user: models.User = Security(get_current_user, scopes=[Roles.SUPER_ADMIN.name]),
) -> models.User:
    return current_user


def get_cache(
        current_user: models.User = Depends(get_current_user),
) -> Generator:
    try:
        cache_client = app_cache.CacheClient(settings.BACKEND_REDIS_URL, current_user.id)
        yield cache_client
    finally:
        cache_client.close()
