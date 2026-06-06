from fastapi.testclient import TestClient

def test_admin_can_list_users(client: TestClient, admin_token: str):
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 1
    # Verify the keys in the user response (must match UserResponse schema)
    user_keys = users[0].keys()
    assert "id" in user_keys
    assert "name" in user_keys
    assert "email" in user_keys
    assert "role" in user_keys
    assert "is_active" in user_keys

def test_user_cannot_list_users(client: TestClient, user_token: str):
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]

def test_unauthenticated_cannot_list_users(client: TestClient):
    response = client.get("/api/users")
    assert response.status_code == 401
