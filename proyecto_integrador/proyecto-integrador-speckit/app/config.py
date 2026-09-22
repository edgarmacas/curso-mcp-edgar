"""Configuración de la aplicación mediante Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./tareas.db"
    SECRET_KEY: str = "default_insecure_key_for_testing_only_1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    MCP_USER_EMAIL: str = "usuario@ejemplo.com"
    APP_NAME: str = "Sistema de Gestión de Tareas"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
