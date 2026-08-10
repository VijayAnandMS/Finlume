from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://finlume:finlume@localhost:5432/finlume"
    JWT_SECRET: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: Optional[str] = None
    GEMINI_MODEL: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    RATE_LIMIT_AI: str = "10/minute"
    RATE_LIMIT_DEFAULT: str = "60/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
