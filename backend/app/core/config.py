from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from cryptography.fernet import Fernet
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_PLACEHOLDER_MARKERS = ("change-me", "changeme", "example")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "IZILens API"
    app_version: str = "0.1.0"
    environment: Literal["development", "test", "production"] = "development"
    docs_enabled: bool = True
    log_level: str = "INFO"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    database_url: str
    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_echo: bool = False

    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    access_token_minutes: int = Field(default=30, ge=1, le=240)
    refresh_token_days: int = Field(default=7, ge=1, le=30)
    api_key_pepper: str = Field(min_length=32)
    data_encryption_keys: str
    login_max_attempts: int = Field(default=5, ge=3, le=20)
    login_lockout_minutes: int = Field(default=15, ge=1, le=1440)

    rate_limit_enabled: bool = True
    rate_limit_login_per_minute: int = 10
    rate_limit_cases_per_minute: int = 60
    max_request_mb: int = Field(default=20, ge=1, le=100)

    storage_dir: Path = Path("./var/storage")
    max_upload_mb: int = Field(default=8, ge=1, le=25)
    min_image_long_side: int = 800
    min_image_short_side: int = 450

    ocr_lang: str = "fr"
    ocr_preload: bool = False
    ocr_review_threshold: float = Field(default=0.90, ge=0.0, le=1.0)
    ocr_min_line_score: float = Field(default=0.30, ge=0.0, le=1.0)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def encryption_keys(self) -> list[str]:
        return [key.strip() for key in self.data_encryption_keys.split(",") if key.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def _check_consistency(self) -> "Settings":
        keys = self.encryption_keys
        if not keys:
            raise ValueError("DATA_ENCRYPTION_KEYS doit contenir au moins une clé Fernet")
        for key in keys:
            try:
                Fernet(key.encode())
            except ValueError as exc:
                raise ValueError("DATA_ENCRYPTION_KEYS contient une clé Fernet invalide") from exc
        if self.environment != "test" and not self.database_url.startswith("postgresql"):
            raise ValueError("DATABASE_URL doit pointer vers PostgreSQL")
        if self.is_production:
            secrets_in_use = (self.jwt_secret, self.api_key_pepper, self.data_encryption_keys)
            if any(marker in secret.lower() for secret in secrets_in_use for marker in _PLACEHOLDER_MARKERS):
                raise ValueError("Secrets de démonstration interdits en production")
            if "*" in self.cors_origins:
                raise ValueError("CORS_ORIGINS ne peut pas contenir '*' en production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
