"""User use cases - thin wrappers around services for specific operations."""
from typing import Optional
from app.application.user.services import AuthService
from app.application.user.dtos import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    AuthResponse,
    TokenPair,
    UserProfile,
)


class RegisterUseCase:
    """Register a new user."""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    async def execute(
        self,
        request: RegisterRequest,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> AuthResponse:
        return await self.auth_service.register(request, user_agent, ip)


class LoginUseCase:
    """Login user."""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    async def execute(
        self,
        request: LoginRequest,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> AuthResponse:
        return await self.auth_service.login(request, user_agent, ip)


class RefreshTokenUseCase:
    """Refresh access token."""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    async def execute(
        self,
        request: RefreshRequest,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> TokenPair:
        return await self.auth_service.refresh(request, user_agent, ip)


class LogoutUseCase:
    """Logout user."""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    async def execute(
        self,
        user_id: int,
        refresh_token: Optional[str] = None,
        logout_all: bool = False,
    ) -> None:
        await self.auth_service.logout(user_id, refresh_token, logout_all)


class GetCurrentUserUseCase:
    """Get current user profile."""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    async def execute(self, user_id: int) -> UserProfile:
        return await self.auth_service.get_current_user(user_id)
