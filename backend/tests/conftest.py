"""Shared test fixtures — in-memory SQLite test database + test client."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Use in-memory SQLite for tests (no PostgreSQL required)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Yield a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Return a FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture
def admin_token(client: TestClient) -> str:
    """Register an admin user and return their access token."""
    client.post("/api/auth/register", json={
        "name": "Admin User",
        "email": "admin@test.com",
        "password": "admin123",
        "role": "admin",
    })
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123",
    })
    return response.json()["access_token"]


@pytest.fixture
def user_token(client: TestClient) -> str:
    """Register a regular user and return their access token."""
    client.post("/api/auth/register", json={
        "name": "Regular User",
        "email": "user@test.com",
        "password": "user1234",
        "role": "user",
    })
    response = client.post("/api/auth/login", json={
        "email": "user@test.com",
        "password": "user1234",
    })
    return response.json()["access_token"]


@pytest.fixture
def user_id(client: TestClient) -> str:
    """Return the ID of the registered regular user."""
    resp = client.post("/api/auth/register", json={
        "name": "Regular User",
        "email": "user2@test.com",
        "password": "user1234",
        "role": "user",
    })
    return str(resp.json()["id"])
