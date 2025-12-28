"""User repository implementations."""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.entities import User, RefreshToken
from app.infrastructure.models.user_model import UserModel, RefreshTokenModel


class SQLAlchemyUserRepository:
    """SQLAlchemy implementation of UserRepository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def create(
        self,
        email: str,
        password_hash: str,
        role: str,
        fullname: Optional[str] = None,
    ) -> User:
        model = UserModel(
            email=email,
            password_hash=password_hash,
            role=role,
            fullname=fullname,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)
    
    async def update_last_login(self, user_id: int, login_time: datetime) -> None:
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(last_login_at=login_time)
        )
    
    async def email_exists(self, email: str) -> bool:
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            fullname=model.fullname,
            password_hash=model.password_hash,
            role=model.role,
            is_active=model.is_active,
            is_verified=model.is_verified,
            last_login_at=model.last_login_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )


class SQLAlchemyRefreshTokenRepository:
    """SQLAlchemy implementation of RefreshTokenRepository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> RefreshToken:
        model = RefreshTokenModel(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)
    
    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def revoke(self, token_id: int) -> None:
        await self.session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id)
            .values(revoked_at=datetime.utcnow())
        )
    
    async def revoke_all_for_user(self, user_id: int) -> None:
        await self.session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.utcnow())
        )
    
    @staticmethod
    def _to_entity(model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            revoked_at=model.revoked_at,
            user_agent=model.user_agent,
            ip=model.ip,
        )
