"""FastAPI application — entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, tasks, users
from app.core.config import settings
from app.core.exceptions import generic_exception_handler, validation_exception_handler
from app.db.base import Base
from app.db.session import engine

# Import models so Base.metadata knows about them
from app.models.user import User  # noqa: F401
from app.models.task import Task  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup (for SQLite dev mode)."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Task Management System",
    description="Role-based task management API with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/api/health", tags=["Health"])
def health_check() -> dict:
    """Simple health-check endpoint."""
    return {"status": "healthy"}
