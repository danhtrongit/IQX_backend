"""Authentication dependencies."""
from typing import Annotated
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.entities import User
from app.domain.user.errors import UserInactiveError, UserNotFoundError
from app.infrastructure.security.jwt import JWTProvider
from app.infrastructure.repositories.user_repo import SQLAlchemyUserRepository
from app.presentation.deps.db_deps import get_db

security = HTTPBearer()
jwt_provider = JWTProvider()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = jwt_provider.decode_access_token(token)
    
    user_id = int(payload["sub"])
    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise UserNotFoundError(user_id)
    
    if not user.can_login:
        raise UserInactiveError()
    
    return user


def get_client_info(
    user_agent: str | None = Header(None, alias="User-Agent"),
    x_forwarded_for: str | None = Header(None, alias="X-Forwarded-For"),
    x_real_ip: str | None = Header(None, alias="X-Real-IP"),
) -> tuple[str | None, str | None]:
    """Get client user agent and IP."""
    ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else x_real_ip
    return user_agent, ip


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
ClientInfo = Annotated[tuple[str | None, str | None], Depends(get_client_info)]
