"""User routes — list users (admin-only, for assignee dropdown)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[UserResponse]:
    """List all users (admin only). Used to populate assignee dropdown."""
    return db.query(User).order_by(User.name).all()
