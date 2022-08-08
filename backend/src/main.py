import asyncio
import logging

import aioredis

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_socketio import SocketManager
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, Response

from src.api.api_v1.api import api_router
from src.api.errors import errors
from src.config import settings
from src.libs.redis_stream import RedisStream
from src.libs.tasks import batch_update_task_status

app = FastAPI(
    docs_url=None,
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# todo staticFiles directory->relative path
app.mount("/static", StaticFiles(directory="static"), name="static")

if settings.SENTRY_DSN:
    # add sentry middleware
    ...

if settings.BACKEND_CORS_ORIGINS:
    allow_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    socket_manager = SocketManager(app=app, cors_allowed_origins=allow_origins)
else:
    socket_manager = SocketManager(app=app)


@app.get("/", tags=["home"])
def index() -> str:
    """
    Welcome to fastapi_scaffold!
    """
    return "Welcome to fastapi_scaffold! If you want to learn more, please visit the /docs page"


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,  # type: ignore
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # type: ignore
async def swagger_ui_redirect() -> HTMLResponse:
    return get_swagger_ui_oauth2_redirect_html()


redis_stream = RedisStream(settings.BACKEND_REDIS_URL)


@app.on_event("startup")
async def startup() -> None:
    if settings.REDIS_TESTING:
        return
    redis = aioredis.from_url(settings.BACKEND_REDIS_URL, encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="app-cache")
    asyncio.create_task(redis_stream.consume(batch_update_task_status))


@app.on_event("shutdown")
async def shutdown() -> None:
    if settings.REDIS_TESTING:
        return
    asyncio.create_task(redis_stream.disconnect())


app.include_router(api_router, prefix=settings.API_V1_STR)

app.add_exception_handler(HTTPException, errors.http_error_handler)
app.add_exception_handler(RequestValidationError, errors.http422_error_handler)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")
logger.propagate = False

# gunicorn_error_logger = logging.getLogger("gunicorn.error")
# gunicorn_logger = logging.getLogger("gunicorn")
# uvicorn_access_logger = logging.getLogger("uvicorn.access")
# uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
# logging.getLogger("multipart").setLevel(logging.WARNING)

if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(app=app, host="0.0.0.0", port=5000)
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True, debug=True)
