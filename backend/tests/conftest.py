"""
Shared test setup (pytest reads this file automatically).

The key idea: tests must never touch the real storymap.db. So we create a
separate in-memory SQLite database and tell the app to use it by overriding
the get_db dependency. Each test gets a fresh, empty database.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app

# import every model so create_all knows about all the tables
from app.models import (  # noqa: F401
    comment_model,
    like_model,
    story_model,
    tag_model,
    user_model,
)

# In-memory database. StaticPool keeps a single shared connection so all
# requests in a test see the same data (normally in-memory DBs vanish per
# connection).
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def client():
    # build a fresh, empty schema for this test
    Base.metadata.create_all(bind=test_engine)

    # replacement for get_db that hands out test-database sessions
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # clean up so the next test starts empty
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


# ── small helpers used across tests ──────────────────────────────────────────

def register(client, name="Test", email="test@example.com", password="pass123"):
    return client.post(
        "/register",
        data={"name": name, "email": email, "password": password},
    )


def login(client, email="test@example.com", password="pass123"):
    return client.post("/login", data={"email": email, "password": password})


def auth_header(client, email="test@example.com", password="pass123"):
    """Register + log in, return an Authorization header dict with the token."""
    register(client, email=email, password=password)
    token = login(client, email=email, password=password).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
