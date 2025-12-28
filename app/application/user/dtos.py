"""User DTOs (Data Transfer Objects) for application layer."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.security_constants import PASSWORD_PATTERN, PASSWORD_POLICY_MESSAGE


# === Request DTOs ===

class RegisterRequest(BaseModel):
    """User registration request."""
    
    email: EmailStr
    password: str = Field(..., min_length=8)
    fullname: Optional[str] = Field(None, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_PATTERN.match(v):
            raise ValueError(PASSWORD_POLICY_MESSAGE)
        return v


class LoginRequest(BaseModel):
    """User login request."""
    
    email: EmailStr
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """Token refresh request."""
    
    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request."""
    
    refresh_token: Optional[str] = None
    all: bool = False


# === Response DTOs ===

class UserProfile(BaseModel):
    """User profile response."""
    
    id: int
    email: str
    fullname: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime


class TokenPair(BaseModel):
    """Access and refresh token pair."""
    
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    """Authentication response with tokens and profile."""
    
    user: UserProfile
    tokens: TokenPair


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str
