"""Task ORM model."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.user import GUID


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, enum.Enum):
    """Task status values — transitions are forward-only."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# Valid forward-only transitions
VALID_STATUS_TRANSITIONS: dict[TaskStatus, list[TaskStatus]] = {
    TaskStatus.PENDING: [TaskStatus.IN_PROGRESS],
    TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED],
    TaskStatus.COMPLETED: [],  # Terminal state
}


class Task(Base):
    """Represents a task that can be assigned to a user."""

    __tablename__ = "tasks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    due_at = Column(DateTime(timezone=True), nullable=False)
    assigned_to = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])

