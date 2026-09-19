import pytest
from app.utils.security import hash_password, verify_password, crear_access_token, decodificar_token
from app.utils.validadores import categoria_valida, CATEGORIAS_PERMITIDAS
from app.utils.formato import formatear_moneda

def test_password_hashing_and_verification():
    import app.security as sec
    raw_pass = "SuperSecretPassword123!"
    hashed = sec.hash_password(raw_pass)
    assert hashed != raw_pass
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert sec.verify_password(raw_pass, hashed) is True
    assert sec.verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation_and_decoding():
    data = {"sub": "user@test.com", "user_id": 42}
    token = crear_access_token(data)
    assert isinstance(token, str)
    decoded = decodificar_token(token)
    assert decoded["sub"] == "user@test.com"
    assert decoded["user_id"] == 42
    assert "exp" in decoded

def test_categoria_valida():
    assert categoria_valida("comida") is True
    assert categoria_valida("transporte") is True
    assert categoria_valida("entretenimiento") is True
    assert categoria_valida("otros") is True
    assert categoria_valida("viajes") is False
    assert categoria_valida("invalida") is False

def test_formatear_moneda():
    assert formatear_moneda(1234.5) == "$1,234.50"
    assert formatear_moneda(50.0) == "$50.00"
