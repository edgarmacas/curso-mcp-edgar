from app.models.usuario import Usuario
from app.database import Base

def test_usuario_model_definition():
    assert issubclass(Usuario, Base)
    assert Usuario.__tablename__ == "usuarios"
    u = Usuario(id=1, email="user@ejemplo.com", hashed_password="hashed_val_123")
    assert u.id == 1
    assert u.email == "user@ejemplo.com"
    assert u.hashed_password == "hashed_val_123"

def test_usuario_in_db(db_session):
    u = Usuario(email="db_user@ejemplo.com", hashed_password="hashed_val_456")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    assert u.id is not None
    assert u.email == "db_user@ejemplo.com"
