"""User application services - orchestrate use cases."""
from datetime import datetime
from typing import Optional, Protocol

from app.domain.user.entities import User
from app.domain.user.repositories import UserRepository, RefreshTokenRepository
from app.domain.user.errors import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserInactiveError,
)
from app.application.user.dtos import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    UserProfile,
    TokenPair,
    AuthResponse,
)
from app.core.config import settings
from app.core.security_constants import ROLE_USER


class PasswordHasher(Protocol):
    """Password hasher interface."""
    
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, hash: str) -> bool: ...


class JWTProvider(Protocol):
    """JWT provider interface."""
    
    def create_access_token(self, user_id: int, role: str) -> str: ...
    def create_refresh_token(self) -> str: ...
    def decode_access_token(self, token: str) -> dict: ...
    def hash_refresh_token(self, token: str) -> str: ...


class AuthService:
    """Authentication service."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        password_hasher: PasswordHasher,
        jwt_provider: JWTProvider,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.password_hasher = password_hasher
        self.jwt_provider = jwt_provider
    
    async def register(
        self,
        request: RegisterRequest,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> AuthResponse:
        """Register a new user."""
        # Check email uniqueness
        if await self.user_repo.email_exists(request.email):
            raise UserAlreadyExistsError("email")
        
        # Create user
        password_hash = self.password_hasher.hash(request.password)
        user = await self.user_repo.create(
            email=request.email,
            password_hash=password_hash,
            role=ROLE_USER,
            fullname=request.fullname,
        )
        
        # Generate tokens
        tokens = await self._create_tokens(user, user_agent, ip)
        
        return AuthResponse(
            user=self._to_profile(user),
            tokens=tokens,
        )
    
    async def login(
        self,
        request: LoginRequest,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> AuthResponse:
        """Login user."""
        user = await self.user_repo.get_by_email(request.email)
        
        if not user:
            raise InvalidCredentialsError()
        
        if not user.can_login:
            raise UserInactiveError()
        
        if not self.password_hasher.verify(request.password, user.password_hash):
            raise InvalidCredentialsError()
        
        # Update last login
        await self.user_repo.update_last_login(user.id, datetime.utcnow())
        
        # Generate tokens
        tokens = await self._create_tokens(user, user_agent, ip)
        
        return AuthResponse(
            user=self._to_profile(user),
            tokens=tokens,
        )
    
    async def refresh(
        self,
        request: RefreshRequest,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> TokenPair:
        """Refresh tokens."""
        token_hash = self.jwt_provider.hash_refresh_token(request.refresh_token)
        stored_token = await self.token_repo.get_by_token_hash(token_hash)
        
        if not stored_token or not stored_token.is_valid:
            raise InvalidTokenError()
        
        # Get user
        user = await self.user_repo.get_by_id(stored_token.user_id)
        if not user or not user.can_login:
            raise UserInactiveError()
        
        # Revoke old token (rotation)
        await self.token_repo.revoke(stored_token.id)
        
        # Create new tokens
        return await self._create_tokens(user, user_agent, ip)
    
    async def logout(
        self,
        user_id: int,
        refresh_token: Optional[str] = None,
        logout_all: bool = False,
    ) -> None:
        """Logout user."""
        if logout_all:
            await self.token_repo.revoke_all_for_user(user_id)
        elif refresh_token:
            token_hash = self.jwt_provider.hash_refresh_token(refresh_token)
            stored_token = await self.token_repo.get_by_token_hash(token_hash)
            if stored_token:
                await self.token_repo.revoke(stored_token.id)
    
    async def get_current_user(self, user_id: int) -> UserProfile:
        """Get current user profile."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return self._to_profile(user)
    
    async def _create_tokens(
        self,
        user: User,
        user_agent: Optional[str],
        ip: Optional[str],
    ) -> TokenPair:
        """Create access and refresh tokens."""
        from datetime import timedelta
        
        access_token = self.jwt_provider.create_access_token(user.id, user.role)
        refresh_token = self.jwt_provider.create_refresh_token()
        
        # Store refresh token hash
        token_hash = self.jwt_provider.hash_refresh_token(refresh_token)
        expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRES_DAYS)
        
        await self.token_repo.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip,
        )
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_EXPIRES_MIN * 60,
        )
    
    @staticmethod
    def _to_profile(user: User) -> UserProfile:
        """Convert user entity to profile DTO."""
        return UserProfile(
            id=user.id,
            email=user.email,
            fullname=user.fullname,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
        )
