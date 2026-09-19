import os
from app.config import Settings

def test_settings_default_values():
    custom_settings = Settings(
        SECRET_KEY="test_secret_key_1234567890_32bytes_min",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        DATABASE_URL="sqlite:///:memory:",
        DEMO_USER_EMAIL="test@example.com",
    )
    assert custom_settings.SECRET_KEY == "test_secret_key_1234567890_32bytes_min"
    assert custom_settings.ALGORITHM == "HS256"
    assert custom_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert custom_settings.DATABASE_URL == "sqlite:///:memory:"
    assert custom_settings.DEMO_USER_EMAIL == "test@example.com"

def test_settings_reads_from_env():
    from app.config import settings
    assert settings.SECRET_KEY is not None
    assert len(settings.SECRET_KEY) > 0
    assert settings.ALGORITHM == "HS256"
    assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
