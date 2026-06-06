"""User ORM model."""

import enum
import uuid as uuid_mod
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, String, TypeDecorator, CHAR
from sqlalchemy.orm import relationship

from app.db.base import Base


class GUID(TypeDecorator):
    """Platform-independent UUID type. Uses CHAR(36) on SQLite, native UUID on PostgreSQL."""
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid_mod.UUID):
                return str(value)
            return str(uuid_mod.UUID(value))
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid_mod.UUID(str(value))
        return value


class UserRole(str, enum.Enum):
    """Allowed user roles."""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """Represents an application user with role-based access."""

    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid_mod.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assigned_to")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
