"""User authentication endpoints."""
from fastapi import APIRouter

from app.application.user.dtos import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    LogoutRequest,
    AuthResponse,
    TokenPair,
    UserProfile,
    MessageResponse,
)
from app.application.user.services import AuthService
from app.infrastructure.repositories.user_repo import (
    SQLAlchemyUserRepository,
    SQLAlchemyRefreshTokenRepository,
)
from app.infrastructure.security.jwt import JWTProvider
from app.infrastructure.security.password import PasswordHasher
from app.presentation.deps.auth_deps import CurrentUser, DBSession, ClientInfo

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: DBSession) -> AuthService:
    """Create auth service with dependencies."""
    return AuthService(
        user_repo=SQLAlchemyUserRepository(db),
        token_repo=SQLAlchemyRefreshTokenRepository(db),
        password_hasher=PasswordHasher(),
        jwt_provider=JWTProvider(),
    )


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: DBSession,
    client_info: ClientInfo,
) -> AuthResponse:
    """Register a new user."""
    user_agent, ip = client_info
    service = get_auth_service(db)
    return await service.register(request, user_agent, ip)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: DBSession,
    client_info: ClientInfo,
) -> AuthResponse:
    """Login user."""
    user_agent, ip = client_info
    service = get_auth_service(db)
    return await service.login(request, user_agent, ip)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    request: RefreshRequest,
    db: DBSession,
    client_info: ClientInfo,
) -> TokenPair:
    """Refresh access token."""
    user_agent, ip = client_info
    service = get_auth_service(db)
    return await service.refresh(request, user_agent, ip)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: LogoutRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> MessageResponse:
    """Logout user."""
    service = get_auth_service(db)
    await service.logout(current_user.id, request.refresh_token, request.all)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserProfile)
async def get_me(
    db: DBSession,
    current_user: CurrentUser,
) -> UserProfile:
    """Get current user profile."""
    service = get_auth_service(db)
    return await service.get_current_user(current_user.id)
