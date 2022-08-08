import secrets
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings, EmailStr


class Settings(BaseSettings):
    PROJECT_NAME: str = "fastapi-scaffold"
    FRONTEND_ENTRYPOINT: str = "frontend-url"
    NGINX_PREFIX: str = ""
    API_V1_STR: str = "/api/v1"
    DATABASE_URI: str = "sqlite:///app.db"
    TOKEN_URL: str = "/auth/token"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 40  # 40 hours
    # APP_SECRET_KEY: str = secrets.token_urlsafe(32)
    APP_SECRET_KEY: str = "xg5lUa5TNyebjnt5HGwBOQjzipgCcs6PKQTgYMtl6Ug"
    DEFAULT_LIMIT: int = 20
    STRING_LEN_LIMIT: int = 100
    LONG_STRING_LEN_LIMIT: int = 500
    TEXT_LEN_LIMIT: int = 20000
    SENTRY_DSN: Optional[str]
    REGISTRATION_NEEDS_APPROVAL: bool = False

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    FIRST_ADMIN: EmailStr = "admin@example.com"  # type: ignore
    FIRST_ADMIN_PASSWORD: str = "change_this"

    USE_200_EVERYWHERE: bool = True

    REDIS_TESTING: bool = False
    APP_API_KEY: str = secrets.token_urlsafe(32)

    # redis
    BACKEND_REDIS_URL: str = "redis://192.168.2.153:6379/0"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Online Sheet
    SHARING_TIMEOUT: int = 10
    WUFOO_URL: Optional[str]
    WUFOO_AUTHORIZATION: Optional[str]
    SHARED_DOCKER_IMAGES_URL: Optional[str]
    GITHUB_TIMEOUT: int = 30
    APP_CACHE_EXPIRE_IN_SECONDS: int = 3600

    # tasks
    TASK_TYPES_WHITELIST: List[int] = [3]
    RETRY_INTERVAL_SECONDS: int = 15

    DEBUG: bool = False
    PRINT_SQL: bool = True if DEBUG else False

    # test
    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore


settings = Settings(_env_file="backend/.env")  # type: ignore
