"""Pruebas unitarias para las dependencias de routers en app/routers/deps.py."""

from datetime import timedelta
import pytest
from fastapi import HTTPException, status
from app.routers.deps import get_current_user
from app.services.auth_service import create_access_token, hash_password
from app.models.usuario import Usuario


def test_get_current_user_valid_token(db_session):
    """Verifica que un token válido retorna el usuario correspondiente."""
    usuario = Usuario(
        email="test_deps@example.com",
        password_hash=hash_password("Password123!"),
    )
    db_session.add(usuario)
    db_session.commit()

    token = create_access_token(data={"sub": "test_deps@example.com"})
    current_user = get_current_user(token=token, db=db_session)

    assert current_user is not None
    assert current_user.id == usuario.id
    assert current_user.email == "test_deps@example.com"


def test_get_current_user_expired_token(db_session):
    """Verifica que un token expirado lanza HTTP 401."""
    token = create_access_token(
        data={"sub": "expired@example.com"},
        expires_delta=timedelta(minutes=-5),
    )
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Credenciales inválidas" in exc_info.value.detail


def test_get_current_user_invalid_token(db_session):
    """Verifica que un token con firma incorrecta o corrupto lanza HTTP 401."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid.token.payload", db=db_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_missing_sub(db_session):
    """Verifica que un token válido pero sin claim 'sub' lanza HTTP 401."""
    token = create_access_token(data={"other_claim": "value"})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_user_not_found(db_session):
    """Verifica que un token con un email que no existe en BD lanza HTTP 401."""
    token = create_access_token(data={"sub": "nonexistent@example.com"})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
