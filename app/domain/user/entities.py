"""User domain entities - pure business objects."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User entity."""
    
    id: int
    email: str
    password_hash: str
    role: str
    fullname: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    last_login_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    
    @property
    def is_admin(self) -> bool:
        return self.role == "ADMIN"
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    @property
    def can_login(self) -> bool:
        return self.is_active and not self.is_deleted


@dataclass
class RefreshToken:
    """Refresh token entity."""
    
    id: int
    user_id: int
    token_hash: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        return (
            self.revoked_at is None
            and self.expires_at > datetime.utcnow()
        )
