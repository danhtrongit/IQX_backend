"""User domain errors."""
from app.core.errors import AppError, NotFoundError, ConflictError, AuthenticationError


class UserNotFoundError(NotFoundError):
    """User not found."""
    
    def __init__(self, identifier: str | int | None = None):
        super().__init__("User", identifier)


class UserAlreadyExistsError(ConflictError):
    """User already exists."""
    
    def __init__(self, field: str = "email"):
        super().__init__(
            message=f"User with this {field} already exists",
            details={"field": field},
        )


class InvalidCredentialsError(AuthenticationError):
    """Invalid login credentials."""
    
    def __init__(self):
        super().__init__("Invalid email/username or password")


class InvalidTokenError(AuthenticationError):
    """Invalid or expired token."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message)


class UserInactiveError(AuthenticationError):
    """User account is inactive."""
    
    def __init__(self):
        super().__init__("User account is inactive or deleted")


class WeakPasswordError(AppError):
    """Password does not meet requirements."""
    
    def __init__(self, message: str):
        super().__init__(
            code="WEAK_PASSWORD",
            message=message,
            status_code=422,
        )
