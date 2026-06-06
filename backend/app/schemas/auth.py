"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request body for user registration."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(default="user", pattern="^(admin|user)$")


class LoginRequest(BaseModel):
    """Request body for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response containing JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Request body for token refresh."""
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Response containing only a new access token."""
    access_token: str
    token_type: str = "bearer"
