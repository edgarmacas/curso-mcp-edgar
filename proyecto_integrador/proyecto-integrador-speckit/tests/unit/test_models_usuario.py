import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.usuario import Usuario


def test_create_and_query_usuario(db_session: Session):
    usuario = Usuario(
        email="test@ejemplo.com",
        password_hash="fake_hash_value_12345",
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    assert usuario.id is not None
    assert usuario.email == "test@ejemplo.com"
    assert usuario.password_hash == "fake_hash_value_12345"
    assert usuario.creado_en is not None


def test_unique_email_constraint(db_session: Session):
    u1 = Usuario(email="duplicado@ejemplo.com", password_hash="hash1")
    db_session.add(u1)
    db_session.commit()

    u2 = Usuario(email="duplicado@ejemplo.com", password_hash="hash2")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
