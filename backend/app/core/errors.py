"""Base error classes for the application."""
from typing import Any


class AppError(Exception):
    """Base application error."""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(AppError):
    """Validation error."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details,
        )


class AuthenticationError(AppError):
    """Authentication error."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=message,
            status_code=401,
        )


class AuthorizationError(AppError):
    """Authorization error."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            code="AUTHORIZATION_ERROR",
            message=message,
            status_code=403,
        )


class NotFoundError(AppError):
    """Resource not found error."""
    
    def __init__(self, resource: str, identifier: Any = None):
        details = {"resource": resource}
        if identifier:
            details["identifier"] = str(identifier)
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found",
            status_code=404,
            details=details,
        )


class ConflictError(AppError):
    """Resource conflict error."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            details=details,
        )
