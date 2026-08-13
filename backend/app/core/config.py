"""
Application configuration settings.
Uses pydantic-settings to read from environment variables or defaults.
Centralizes configuration validation and directory initialization.
"""
from pathlib import Path
from typing import List, Union, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "LegalAId Backend"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development")

    DATABASE_URL: str = Field(default="sqlite:///./data/legalaid.db")

    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    FAISS_INDEX_PATH: str = Field(default="./data/faiss_index.bin")
    LOG_LEVEL: str = Field(default="INFO")

    AI_API_KEY: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")
    AI_MODEL: str = Field(default="gemini-2.0-flash")

    SECRET_KEY: str = Field(default="dev_secret_key_change_me_in_production")
    
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Allow CORS_ORIGINS to be given as a comma-separated env string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in {"production", "prod"}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def api_key(self) -> str:
        return self.AI_API_KEY or self.GEMINI_API_KEY or ""

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate configuration at startup.
        Ensure required directories exist and report optional service status.
        """
        # Ensure data directory exists
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        backups_dir = data_dir / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)

        eval_dir = data_dir / "evaluation"
        eval_dir.mkdir(parents=True, exist_ok=True)

        has_ai = bool(self.api_key.strip())
        
        return {
            "valid": True,
            "environment": self.ENVIRONMENT,
            "database_url": self.DATABASE_URL.split("@")[-1] if "@" in self.DATABASE_URL else self.DATABASE_URL,
            "ai_configured": has_ai,
            "ai_model": self.AI_MODEL if has_ai else "disabled",
            "embedding_model": self.EMBEDDING_MODEL,
            "cors_origins_count": len(self.CORS_ORIGINS)
        }


settings = Settings()
