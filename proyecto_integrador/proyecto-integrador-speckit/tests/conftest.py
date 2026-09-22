"""Fixtures compartidas de prueba con SQLite en memoria y repositorios falsos."""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.database import Base
from tests.fakes.fake_tareas_repository import FakeTareasRepository

# Motor SQLite en memoria aislado para pruebas de integración (Artículo VII.1)
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="function")
def db_session(monkeypatch) -> Generator[Session, None, None]:
    """Crea un esquema de base de datos limpio en memoria para cada test de integración (Artículo VII.1)."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    import app.database as db_mod
    import app.repositories.tareas_repository as tr_mod
    import app.repositories.usuarios_repository as ur_mod

    monkeypatch.setattr(db_mod, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(tr_mod, "SessionLocal", TestingSessionLocal)

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def fake_tareas_repo() -> FakeTareasRepository:
    """Provee una instancia limpia de FakeTareasRepository para tests unitarios DIP (Artículo II.3, VII.2)."""
    return FakeTareasRepository()
