import pytest

def test_registrar_usuario_api_exito(client):
    response = client.post(
        "/usuarios/",
        json={"email": "api_user@test.com", "password": "Password123!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "api_user@test.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

def test_registrar_usuario_api_email_duplicado(client):
    # Primer registro
    client.post(
        "/usuarios/",
        json={"email": "duplicado_api@test.com", "password": "Password123!"},
    )
    # Segundo registro con mismo email
    response = client.post(
        "/usuarios/",
        json={"email": "duplicado_api@test.com", "password": "OtraPassword123!"},
    )
    assert response.status_code == 400
    assert "ya está registrado" in response.json()["detail"]

def test_registrar_usuario_api_formato_invalido(client):
    response = client.post(
        "/usuarios/",
        json={"email": "formato-invalido", "password": "Password123!"},
    )
    assert response.status_code == 422

def test_login_usuario_api_exito(client):
    client.post(
        "/usuarios/",
        json={"email": "login_api@test.com", "password": "MiPasswordSegura"},
    )
    response = client.post(
        "/usuarios/token",
        data={"username": "login_api@test.com", "password": "MiPasswordSegura"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_usuario_api_credenciales_invalidas(client):
    response = client.post(
        "/usuarios/token",
        data={"username": "desconocido@test.com", "password": "WrongPassword"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()
