"""Pydantic schemas for task endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class TaskCreate(BaseModel):
    """Request body for creating a new task."""
    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed)$")
    due_at: datetime
    assigned_to: UUID | None = None


class TaskUpdate(BaseModel):
    """Request body for updating a task (all fields optional)."""
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")
    status: str | None = Field(default=None, pattern="^(pending|in_progress|completed)$")
    due_at: datetime | None = None
    assigned_to: UUID | None = None


class StatusUpdate(BaseModel):
    """Request body for user status transition (forward-only)."""
    status: str = Field(..., pattern="^(pending|in_progress|completed)$")


class TaskResponse(BaseModel):
    """Task representation returned by the API."""
    id: UUID
    title: str
    description: str | None
    priority: str
    status: str
    due_at: datetime
    assigned_to: UUID | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime | None
    assignee: UserResponse | None = None
    creator: UserResponse | None = None

    model_config = {"from_attributes": True}
