import os
from app.config import Settings


def test_default_settings():
    test_settings = Settings()
    assert test_settings.DATABASE_URL.startswith("sqlite")
    assert test_settings.ALGORITHM == "HS256"
    assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    assert test_settings.MCP_USER_EMAIL == "usuario@ejemplo.com"


def test_custom_settings_override(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "custom_secret_key_12345")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
    monkeypatch.setenv("MCP_USER_EMAIL", "custom@empresa.com")

    custom_settings = Settings()
    assert custom_settings.SECRET_KEY == "custom_secret_key_12345"
    assert custom_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 120
    assert custom_settings.MCP_USER_EMAIL == "custom@empresa.com"
