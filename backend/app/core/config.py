"""Application configuration from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # App
    APP_NAME: str = "IQX Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "iqx"
    MYSQL_PASSWORD: str = "iqx_password"
    MYSQL_DATABASE: str = "iqx_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )
    
    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRES_MIN: int = 30
    JWT_REFRESH_EXPIRES_DAYS: int = 7
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # Price Stream
    ENABLE_PRICE_STREAM: bool = False  # Set to True to auto-start WebSocket stream
    
    # AI Chat (Mr.Arix)
    AI_PROXY: str = "https://v98store.com/v1/chat/completions"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-5-nano"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
