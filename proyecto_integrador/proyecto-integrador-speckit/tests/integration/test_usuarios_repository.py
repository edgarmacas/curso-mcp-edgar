from sqlalchemy.orm import Session
from app.repositories.usuarios_repository import usuarios_repository


def test_usuarios_repository_crud(db_session: Session):
    # 1. Crear usuario
    user = usuarios_repository.crear_usuario(
        db=db_session,
        email="repo_test@ejemplo.com",
        password_hash="hash_seguro_123",
    )
    assert user.id is not None
    assert user.email == "repo_test@ejemplo.com"

    # 2. Obtener por email
    found_email = usuarios_repository.obtener_por_email(db_session, "repo_test@ejemplo.com")
    assert found_email is not None
    assert found_email.id == user.id

    # 3. Obtener por ID
    found_id = usuarios_repository.obtener_por_id(db_session, user.id)
    assert found_id is not None
    assert found_id.email == "repo_test@ejemplo.com"

    # 4. Inexistente
    assert usuarios_repository.obtener_por_email(db_session, "noexiste@ejemplo.com") is None
    assert usuarios_repository.obtener_por_id(db_session, 9999) is None
