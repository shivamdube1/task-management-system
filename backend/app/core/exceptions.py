"""Global exception handlers for the FastAPI application."""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return structured 422 responses for Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler to prevent leaking internal details."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
