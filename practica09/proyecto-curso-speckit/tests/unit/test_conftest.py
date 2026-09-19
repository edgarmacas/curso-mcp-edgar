from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.utils.security import decodificar_token

def test_db_session_fixture(db_session):
    assert isinstance(db_session, Session)
    # Check that it's SQLite in-memory
    assert "sqlite" in str(db_session.bind.url)

def test_client_fixture(client):
    assert isinstance(client, TestClient)

def test_auth_headers_fixture(auth_headers):
    headers = auth_headers(usuario_id=99, email="user99@test.com")
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")
    token = headers["Authorization"].split(" ")[1]
    payload = decodificar_token(token)
    assert payload["user_id"] == 99
    assert payload["sub"] == "user99@test.com"
