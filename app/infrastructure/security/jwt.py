"""JWT token provider implementation."""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any

import jwt

from app.core.config import settings
from app.domain.user.errors import InvalidTokenError


class JWTProvider:
    """JWT token provider."""
    
    def __init__(
        self,
        secret: str = settings.JWT_SECRET,
        algorithm: str = settings.JWT_ALGORITHM,
        access_expires_min: int = settings.JWT_ACCESS_EXPIRES_MIN,
        refresh_expires_days: int = settings.JWT_REFRESH_EXPIRES_DAYS,
    ):
        self.secret = secret
        self.algorithm = algorithm
        self.access_expires_min = access_expires_min
        self.refresh_expires_days = refresh_expires_days
    
    def create_access_token(self, user_id: int, role: str) -> str:
        """Create an access token."""
        now = datetime.utcnow()
        payload = {
            "sub": str(user_id),
            "role": role,
            "iat": now,
            "exp": now + timedelta(minutes=self.access_expires_min),
            "type": "access",
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def create_refresh_token(self) -> str:
        """Create a refresh token (random string)."""
        return secrets.token_urlsafe(32)
    
    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decode and validate an access token."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            if payload.get("type") != "access":
                raise InvalidTokenError("Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    def hash_refresh_token(self, token: str) -> str:
        """Hash a refresh token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()
