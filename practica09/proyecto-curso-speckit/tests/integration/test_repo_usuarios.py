import pytest
from app.repositories import usuarios as usuarios_repo
from app.models.usuario import Usuario

def test_guardar_y_obtener_usuario(db_session):
    # Guardar usuario
    usuario = usuarios_repo.guardar(db_session, "nuevo@test.com", "hash_seguro_123")
    assert isinstance(usuario, Usuario)
    assert usuario.id is not None
    assert usuario.email == "nuevo@test.com"
    assert usuario.hashed_password == "hash_seguro_123"

    # Obtener por email existente
    recuperado = usuarios_repo.obtener_por_email(db_session, "nuevo@test.com")
    assert recuperado is not None
    assert recuperado.id == usuario.id
    assert recuperado.email == "nuevo@test.com"

    # Obtener por email inexistente
    inexistente = usuarios_repo.obtener_por_email(db_session, "noexiste@test.com")
    assert inexistente is None
