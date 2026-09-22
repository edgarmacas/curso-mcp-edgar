import pytest
from datetime import timedelta
from sqlalchemy.orm import Session
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    registrar_usuario,
    autenticar_usuario,
)
from app.schemas.usuario import UsuarioCreate
from app.services.exceptions import EmailDuplicadoError, CredencialesInvalidasError


def test_password_hashing_and_verification():
    raw_pass = "super_password_123"
    hashed = hash_password(raw_pass)

    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_creation_and_decoding():
    token = create_access_token({"sub": "test@usuario.com"})
    payload = decode_access_token(token)

    assert payload["sub"] == "test@usuario.com"
    assert "exp" in payload
    assert "iat" in payload


def test_expired_jwt_raises_error():
    # Token expirado
    token = create_access_token({"sub": "expired@usuario.com"}, expires_delta=timedelta(seconds=-10))
    with pytest.raises(CredencialesInvalidasError):
        decode_access_token(token)


def test_registrar_y_autenticar_usuario(db_session: Session):
    datos = UsuarioCreate(email="auth_test@ejemplo.com", password="password123")
    user = registrar_usuario(db_session, datos)

    assert user.id is not None
    assert user.email == "auth_test@ejemplo.com"
    assert verify_password("password123", user.password_hash) is True

    # Error en duplicado
    with pytest.raises(EmailDuplicadoError):
        registrar_usuario(db_session, datos)

    # Login exitoso
    auth_user = autenticar_usuario(db_session, "auth_test@ejemplo.com", "password123")
    assert auth_user.id == user.id

    # Login contraseña incorrecta
    with pytest.raises(CredencialesInvalidasError):
        autenticar_usuario(db_session, "auth_test@ejemplo.com", "wrong_pass")

    # Login usuario inexistente
    with pytest.raises(CredencialesInvalidasError):
        autenticar_usuario(db_session, "noexiste@ejemplo.com", "password123")
