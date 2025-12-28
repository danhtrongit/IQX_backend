"""Global exception handlers."""
import asyncio

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.errors import AppError
from app.presentation.middleware.request_id import get_request_id


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    details: dict | None = None,
) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
            "request_id": get_request_id(),
        },
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle application errors."""
    return create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        loc = ".".join(str(x) for x in error["loc"])
        errors.append({
            "field": loc,
            "message": error["msg"],
        })
    
    return create_error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=422,
        details={"errors": errors},
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    # Ignore CancelledError - client disconnected (don't log as error)
    if isinstance(exc, (asyncio.CancelledError, asyncio.exceptions.CancelledError)):
        return JSONResponse(status_code=499, content={"error": "Client closed request"})
    
    # Check for CancelledError in exception chain
    if exc.__cause__ and isinstance(exc.__cause__, (asyncio.CancelledError, asyncio.exceptions.CancelledError)):
        return JSONResponse(status_code=499, content={"error": "Client closed request"})
    
    return create_error_response(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        status_code=500,
    )
