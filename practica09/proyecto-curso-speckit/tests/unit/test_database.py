from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base, get_db, connect_args

def test_database_components():
    assert engine is not None
    assert SessionLocal is not None
    assert Base is not None

def test_get_db_yields_session():
    generator = get_db()
    session = next(generator)
    assert isinstance(session, Session)
    try:
        next(generator)
    except StopIteration:
        pass

def test_conditional_connect_args():
    if engine.url.drivername.startswith("sqlite"):
        assert "check_same_thread" in connect_args
        assert connect_args["check_same_thread"] is False
    else:
        assert "check_same_thread" not in connect_args
