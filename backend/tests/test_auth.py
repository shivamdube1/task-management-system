"""Tests for authentication endpoints."""

from fastapi.testclient import TestClient


class TestRegister:
    """Tests for POST /api/auth/register."""

    def test_register_success(self, client: TestClient):
        response = client.post("/api/auth/register", json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass",
            "role": "user",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "john@example.com"
        assert data["name"] == "John Doe"
        assert data["role"] == "user"
        assert "id" in data

    def test_register_duplicate_email_returns_409(self, client: TestClient):
        payload = {
            "name": "Jane",
            "email": "dupe@example.com",
            "password": "password1",
            "role": "user",
        }
        client.post("/api/auth/register", json=payload)
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_register_invalid_email_returns_422(self, client: TestClient):
        response = client.post("/api/auth/register", json={
            "name": "Bad Email",
            "email": "not-an-email",
            "password": "password1",
        })
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login."""

    def test_login_success_returns_tokens(self, client: TestClient):
        client.post("/api/auth/register", json={
            "name": "Login Test",
            "email": "login@example.com",
            "password": "testpass1",
            "role": "user",
        })
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "testpass1",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self, client: TestClient):
        client.post("/api/auth/register", json={
            "name": "WP User",
            "email": "wp@example.com",
            "password": "correctpass",
            "role": "user",
        })
        response = client.post("/api/auth/login", json={
            "email": "wp@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]

    def test_login_nonexistent_user_returns_401(self, client: TestClient):
        response = client.post("/api/auth/login", json={
            "email": "ghost@example.com",
            "password": "anything",
        })
        assert response.status_code == 401


class TestMe:
    """Tests for GET /api/auth/me."""

    def test_me_without_token_returns_401(self, client: TestClient):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_me_with_valid_token(self, client: TestClient, admin_token: str):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"


class TestRefresh:
    """Tests for POST /api/auth/refresh."""

    def test_refresh_success(self, client: TestClient):
        # Register and login to get refresh token
        client.post("/api/auth/register", json={
            "name": "Refresh User",
            "email": "refresh@test.com",
            "password": "password123",
            "role": "user"
        })
        login_resp = client.post("/api/auth/login", json={
            "email": "refresh@test.com",
            "password": "password123"
        })
        refresh_token = login_resp.json()["refresh_token"]

        response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_refresh_invalid_token_type(self, client: TestClient):
        # Access token is invalid for refreshing
        client.post("/api/auth/register", json={
            "name": "Refresh User 2",
            "email": "refresh2@test.com",
            "password": "password123",
            "role": "user"
        })
        login_resp = client.post("/api/auth/login", json={
            "email": "refresh2@test.com",
            "password": "password123"
        })
        access_token = login_resp.json()["access_token"]

        response = client.post("/api/auth/refresh", json={"refresh_token": access_token})
        assert response.status_code == 401
        assert "Invalid token type" in response.json()["detail"]

    def test_refresh_expired_or_invalid(self, client: TestClient):
        response = client.post("/api/auth/refresh", json={"refresh_token": "completely-invalid-token"})
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]


class TestLogout:
    """Tests for POST /api/auth/logout."""

    def test_logout_success(self, client: TestClient, user_token: str):
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

    def test_logout_without_token_returns_401(self, client: TestClient):
        response = client.post("/api/auth/logout")
        assert response.status_code == 401

