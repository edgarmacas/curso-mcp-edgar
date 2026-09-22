"""Dependencias reutilizables para los routers de FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.repositories.usuarios_repository import usuarios_repository, UsuariosRepository
from app.services.auth_service import decode_access_token
from app.services.exceptions import CredencialesInvalidasError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/token")


def get_usuarios_repo() -> UsuariosRepository:
    """Proveedor de dependencia para UsuariosRepository."""
    return usuarios_repository


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    repo: UsuariosRepository = Depends(get_usuarios_repo),
) -> Usuario:
    """Extrae y valida el token Bearer JWT y retorna el usuario autenticado (Artículo IV.4)."""
    # Si se invoca directamente en tests unitarios sin resolución de FastAPI Depends
    if not isinstance(repo, UsuariosRepository):
        repo = usuarios_repository

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except CredencialesInvalidasError:
        raise credentials_exception

    usuario = repo.obtener_por_email(db, email=email)
    if usuario is None:
        raise credentials_exception
    return usuario
