"""Task routes — CRUD for admins, filtered read + status update for users."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.task import Task, TaskPriority, TaskStatus, VALID_STATUS_TRANSITIONS
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, StatusUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ---------------------------------------------------------------------------
# Admin-only endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> TaskResponse:
    """Create a new task (admin only)."""
    # Validate assignee exists if provided
    if body.assigned_to:
        assignee = db.query(User).filter(User.id == body.assigned_to).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found",
            )

    task = Task(
        title=body.title,
        description=body.description,
        priority=TaskPriority(body.priority),
        status=TaskStatus(body.status),
        due_at=body.due_at,
        assigned_to=body.assigned_to,
        created_by=admin.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Reload with relationships
    task = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator))
        .filter(Task.id == task.id)
        .first()
    )
    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    task_status: str | None = Query(default=None, alias="status"),
    priority: str | None = None,
    assigned_to: UUID | None = None,
) -> list[TaskResponse]:
    """List all tasks with optional filters (admin only)."""
    query = db.query(Task).options(joinedload(Task.assignee), joinedload(Task.creator))

    if task_status:
        query = query.filter(Task.status == TaskStatus(task_status))
    if priority:
        query = query.filter(Task.priority == TaskPriority(priority))
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    return query.order_by(Task.created_at.desc()).all()


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    body: TaskUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> TaskResponse:
    """Update a task (admin only). All fields are optional."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = body.model_dump(exclude_unset=True)

    # Validate assignee if changing
    if "assigned_to" in update_data and update_data["assigned_to"]:
        assignee = db.query(User).filter(User.id == update_data["assigned_to"]).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found",
            )

    # Convert string enums to ORM enum values
    if "priority" in update_data and update_data["priority"]:
        update_data["priority"] = TaskPriority(update_data["priority"])
    if "status" in update_data and update_data["status"]:
        update_data["status"] = TaskStatus(update_data["status"])

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    task = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator))
        .filter(Task.id == task.id)
        .first()
    )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> None:
    """Delete a task (admin only)."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()


# ---------------------------------------------------------------------------
# User endpoints (any authenticated user)
# ---------------------------------------------------------------------------

@router.get("/my", response_model=list[TaskResponse])
def list_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskResponse]:
    """List tasks assigned to the current user (server-filtered)."""
    tasks = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator))
        .filter(Task.assigned_to == current_user.id)
        .order_by(Task.due_at.asc())
        .all()
    )
    return tasks


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: UUID,
    body: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Update only the status of an assigned task (forward-only transitions)."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Users can only update their own assigned tasks
    if task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update tasks assigned to you",
        )

    current_status = task.status
    new_status = TaskStatus(body.status)

    # Enforce forward-only transitions
    allowed = VALID_STATUS_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition: {current_status.value} → {new_status.value}. "
                   f"Allowed transitions: {[s.value for s in allowed] or 'none (terminal state)'}",
        )

    task.status = new_status
    db.commit()
    db.refresh(task)

    task = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator))
        .filter(Task.id == task.id)
        .first()
    )
    return task
