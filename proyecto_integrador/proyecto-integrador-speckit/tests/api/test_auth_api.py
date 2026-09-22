"""Pruebas de integración API para autenticación y registro en /usuarios/."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.usuarios import router as usuarios_router
from app.database import get_db


@pytest.fixture
def client(db_session):
    """Cliente de prueba FastAPI con base de datos en memoria inyectada."""
    app = FastAPI()
    app.include_router(usuarios_router)
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client


def test_registrar_usuario_exitoso(client):
    """Verifica el registro exitoso (HTTP 201) y que no se exponga la contraseña."""
    payload = {
        "email": "nuevo@ejemplo.com",
        "password": "PasswordSegura123!",
    }
    response = client.post("/usuarios/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "nuevo@ejemplo.com"
    assert "id" in data
    assert "creado_en" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_registrar_usuario_email_duplicado(client):
    """Verifica que registrar un email existente responda HTTP 400 Bad Request."""
    payload = {
        "email": "duplicado@ejemplo.com",
        "password": "PasswordSegura123!",
    }
    # Primer registro exitoso
    res1 = client.post("/usuarios/", json=payload)
    assert res1.status_code == 201

    # Segundo registro con el mismo correo
    res2 = client.post("/usuarios/", json=payload)
    assert res2.status_code == 400
    assert "El correo electrónico ya se encuentra registrado" in res2.json()["detail"]


def test_registrar_usuario_validacion_fallida(client):
    """Verifica que datos inválidos (email no válido o contraseña corta) retornen HTTP 422."""
    # Email inválido
    res_email = client.post(
        "/usuarios/",
        json={"email": "no-es-un-email", "password": "Password123!"},
    )
    assert res_email.status_code == 422

    # Contraseña corta (< 8 caracteres)
    res_pass = client.post(
        "/usuarios/",
        json={"email": "valido@ejemplo.com", "password": "corta"},
    )
    assert res_pass.status_code == 422


def test_login_exitoso(client):
    """Verifica obtención de token JWT (HTTP 200) con credenciales válidas."""
    # Registrar usuario
    client.post(
        "/usuarios/",
        json={"email": "login@ejemplo.com", "password": "Password123!"},
    )

    # Iniciar sesión vía form urlencoded
    res = client.post(
        "/usuarios/token",
        data={"username": "login@ejemplo.com", "password": "Password123!"},
    )
    assert res.status_code == 200
    token_data = res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert len(token_data["access_token"]) > 20


def test_login_credenciales_invalidas(client):
    """Verifica que credenciales inválidas (password incorrecto o email inexistente) retornen HTTP 401."""
    # Registrar usuario
    client.post(
        "/usuarios/",
        json={"email": "existente@ejemplo.com", "password": "Password123!"},
    )

    # Password incorrecto
    res_pass = client.post(
        "/usuarios/token",
        data={"username": "existente@ejemplo.com", "password": "PasswordIncorrecto!"},
    )
    assert res_pass.status_code == 401
    assert "Credenciales inválidas" in res_pass.json()["detail"]

    # Usuario inexistente
    res_user = client.post(
        "/usuarios/token",
        data={"username": "noexiste@ejemplo.com", "password": "Password123!"},
    )
    assert res_user.status_code == 401
    assert "Credenciales inválidas" in res_user.json()["detail"]
