import pytest
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings

def test_password_hashing():
    password = "MySuperSecretPassword123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_create_access_token():
    payload = {"sub": "12345", "role": "user"}
    token = create_access_token(payload)
    
    decoded = decode_token(token)
    assert decoded["sub"] == "12345"
    assert decoded["role"] == "user"
    assert decoded["type"] == "access"
    assert "exp" in decoded

def test_create_access_token_with_custom_expiry():
    payload = {"sub": "12345"}
    delta = timedelta(minutes=5)
    token = create_access_token(payload, expires_delta=delta)
    
    decoded = decode_token(token)
    assert decoded["sub"] == "12345"
    
    # Verify the exp time is roughly 5 minutes from now
    exp = decoded["exp"]
    now = datetime.now(timezone.utc).timestamp()
    assert exp - now <= 300
    assert exp - now >= 290

def test_create_refresh_token():
    user_id = "user-uuid-1234"
    token = create_refresh_token(user_id)
    
    decoded = decode_token(token)
    assert decoded["sub"] == user_id
    assert decoded["type"] == "refresh"
    assert "exp" in decoded

def test_decode_token_failures():
    # Invalid token format
    with pytest.raises(JWTError):
        decode_token("invalid.token.here")
        
    # Signature mismatch (decode using a different key)
    payload = {"sub": "test"}
    bad_token = jwt.encode(payload, "different-secret-key", algorithm=settings.ALGORITHM)
    with pytest.raises(JWTError):
        decode_token(bad_token)
        
    # Expired token
    expired_payload = {"sub": "test", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(JWTError):
        decode_token(expired_token)
