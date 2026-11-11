import os


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "IZILens API")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./izilens_dev.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-only-change-me")


settings = Settings()
