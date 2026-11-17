from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    PROJECT_NAME: str = "AI-Powered Placement Coach"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    # Database: Supports SQLite (for immediate out-of-the-box local dev) and PostgreSQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./placement.db"

    # Security & JWT
    SECRET_KEY: str = "placement-coach-insecure-dev-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECURE_COOKIES: bool = False  # Set to True in production HTTPS

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # AI Configuration (Free Tier & Local)
    AI_PROVIDER: str = "gemini"  # "gemini" | "groq" | "ollama"
    GEMINI_API_KEY: str = ""
    AI_MODEL_CHAT: str = "gemini-1.5-flash"
    AI_MODEL_ANALYSIS: str = "gemini-1.5-flash"
    GROQ_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # File Storage
    UPLOAD_DIR: str = str(Path(__file__).resolve().parent.parent.parent / "uploads")
    MAX_UPLOAD_SIZE_MB: int = 5

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()

