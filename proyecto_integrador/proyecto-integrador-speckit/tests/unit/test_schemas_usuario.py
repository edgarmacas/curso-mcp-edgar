import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.schemas.token import TokenOut, TokenData
from app.models.usuario import Usuario


def test_usuario_create_validation():
    # Válido
    u = UsuarioCreate(email="valido@ejemplo.com", password="password123")
    assert u.email == "valido@ejemplo.com"
    assert u.password == "password123"

    # Email inválido
    with pytest.raises(ValidationError):
        UsuarioCreate(email="invalido", password="password123")

    # Contraseña muy corta (< 8)
    with pytest.raises(ValidationError):
        UsuarioCreate(email="valido@ejemplo.com", password="123")


def test_usuario_out_does_not_expose_password():
    now = datetime.now(timezone.utc)
    usuario_model = Usuario(
        id=1,
        email="test@ejemplo.com",
        password_hash="secreto_hasheado_12345",
        creado_en=now,
    )

    out = UsuarioOut.model_validate(usuario_model)
    data = out.model_dump()

    assert data["id"] == 1
    assert data["email"] == "test@ejemplo.com"
    assert "password_hash" not in data
    assert "password" not in data


def test_token_schemas():
    t = TokenOut(access_token="fake_token_abc")
    assert t.access_token == "fake_token_abc"
    assert t.token_type == "bearer"

    td = TokenData(sub="usuario@ejemplo.com")
    assert td.sub == "usuario@ejemplo.com"
