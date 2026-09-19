import pytest
from fastapi import HTTPException
from app.dependencies import get_current_user
from app.utils.security import crear_access_token
from app.repositories import usuarios as usuarios_repo

def test_get_current_user_valido(db_session):
    user = usuarios_repo.guardar(db_session, "autenticado@test.com", "hashed_pass")
    token = crear_access_token({"sub": "autenticado@test.com"})

    resolved_user = get_current_user(token=token, db=db_session)
    assert resolved_user.id == user.id
    assert resolved_user.email == "autenticado@test.com"

def test_get_current_user_token_invalido(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="token.completamente.invalido", db=db_session)
    assert exc_info.value.status_code == 401

def test_get_current_user_no_encontrado(db_session):
    token = crear_access_token({"sub": "noexiste@test.com"})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)
    assert exc_info.value.status_code == 401
