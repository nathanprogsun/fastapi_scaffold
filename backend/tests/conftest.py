import json
from typing import Dict, Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api import deps
from src.config import settings
from src.db.session import SessionLocal
from src.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_admin_token_headers, get_super_admin_token_headers


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def api_key_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return {"api_key": settings.APP_SECRET_KEY}


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(client=client, email=settings.EMAIL_TEST_USER, db=db)


@pytest.fixture(scope="module")
def admin_token_headers(client: TestClient) -> Dict[str, str]:
    return get_admin_token_headers(client)


@pytest.fixture()
def user_id(mock, client: TestClient, normal_user_token_headers: Dict[str, str]):
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()["result"]
    return current_user["id"]
