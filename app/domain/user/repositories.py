"""Repository protocols (interfaces) for user domain."""
from typing import Protocol, Optional
from datetime import datetime
from app.domain.user.entities import User, RefreshToken


class UserRepository(Protocol):
    """User repository interface."""
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        ...
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        ...
    
    async def create(
        self,
        email: str,
        password_hash: str,
        role: str,
        fullname: Optional[str] = None,
    ) -> User:
        """Create a new user."""
        ...
    
    async def update_last_login(self, user_id: int, login_time: datetime) -> None:
        """Update user's last login time."""
        ...
    
    async def email_exists(self, email: str) -> bool:
        """Check if email exists."""
        ...


class RefreshTokenRepository(Protocol):
    """Refresh token repository interface."""
    
    async def create(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> RefreshToken:
        """Create a new refresh token."""
        ...
    
    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Get refresh token by hash."""
        ...
    
    async def revoke(self, token_id: int) -> None:
        """Revoke a refresh token."""
        ...
    
    async def revoke_all_for_user(self, user_id: int) -> None:
        """Revoke all refresh tokens for a user."""
        ...
