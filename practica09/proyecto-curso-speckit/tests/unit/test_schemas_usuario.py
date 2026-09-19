import pytest
from pydantic import ValidationError
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioOut, Token
from app.models.usuario import Usuario

def test_usuario_create_valid():
    data = UsuarioCreate(email="valid@example.com", password="SecurePassword123")
    assert data.email == "valid@example.com"
    assert data.password == "SecurePassword123"

def test_usuario_create_invalid_email():
    with pytest.raises(ValidationError):
        UsuarioCreate(email="not-an-email", password="SecurePassword123")

def test_usuario_response_from_orm():
    orm_user = Usuario(id=10, email="user10@example.com", hashed_password="some_hashed_pass")
    resp = UsuarioResponse.model_validate(orm_user)
    assert resp.id == 10
    assert resp.email == "user10@example.com"
    # Never exposes password
    assert not hasattr(resp, "password")
    assert not hasattr(resp, "hashed_password")

def test_token_schema():
    tok = Token(access_token="fake.jwt.token", token_type="bearer")
    assert tok.access_token == "fake.jwt.token"
    assert tok.token_type == "bearer"
