import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.utils.security import crear_access_token


@pytest.fixture
def db_session():
    """Motor SQLite real en memoria para tests de integración (Artículo VII.4 y III.2)."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    """Cliente de pruebas para endpoints FastAPI usando dependency_overrides (Artículo VII.5)."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Genera cabeceras con JWT válido para un usuario de prueba."""
    def _make_headers(usuario_id: int = 1, email: str = "test@ejemplo.com"):
        token = crear_access_token({"sub": email, "user_id": usuario_id})
        return {"Authorization": f"Bearer {token}"}
    return _make_headers
