from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base, get_db


def test_database_engine_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        assert result == 1


def test_session_lifecycle():
    session = SessionLocal()
    assert isinstance(session, Session)
    try:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        session.close()


def test_get_db_generator():
    db_gen = get_db()
    db = next(db_gen)
    assert isinstance(db, Session)
    try:
        assert db.is_active
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass
