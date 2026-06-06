import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_admin
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User, UserRole
from app.db.base import Base

def test_get_current_user_valid_token(client, setup_database):
    # Register and login a user to get valid token
    client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "user"
    })
    login_resp = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    
    # We can get the DB session from the overridden dependency
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    try:
        user = get_current_user(token=token, db=db)
        assert user is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.is_active is True
    finally:
        db.close()

def test_get_current_user_deactivated(client, setup_database):
    # Register
    register_resp = client.post("/api/auth/register", json={
        "name": "Deactivated User",
        "email": "deact@example.com",
        "password": "password123",
        "role": "user"
    })
    user_id = register_resp.json()["id"]
    
    # Deactivate the user directly in the database
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        db_user.is_active = False
        db.commit()
        
        # Generate token
        token_data = {"sub": str(db_user.id), "email": db_user.email, "role": db_user.role.value}
        token = create_access_token(data=token_data)
        
        # Call get_current_user which should raise 403 Forbidden
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "deactivated" in exc_info.value.detail
    finally:
        db.close()

def test_get_current_user_invalid_token_type(client, setup_database):
    # Generate a refresh token instead of access token
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    try:
        refresh_token = create_refresh_token(user_id="some-id")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=refresh_token, db=db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    finally:
        db.close()

def test_get_current_user_nonexistent_user(client, setup_database):
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    try:
        # Generate token for a non-existent user ID
        token_data = {"sub": "00000000-0000-0000-0000-000000000000", "email": "ghost@test.com", "role": "user"}
        token = create_access_token(token_data)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    finally:
        db.close()

def test_require_admin():
    # User object
    admin_user = User(role=UserRole.ADMIN)
    regular_user = User(role=UserRole.USER)
    
    # Check success
    res = require_admin(admin_user)
    assert res == admin_user
    
    # Check failure
    with pytest.raises(HTTPException) as exc_info:
        require_admin(regular_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Admin access required" in exc_info.value.detail
