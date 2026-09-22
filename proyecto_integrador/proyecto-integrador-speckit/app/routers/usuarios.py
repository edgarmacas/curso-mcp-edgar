"""Router para gestión y autenticación de usuarios."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.schemas.token import TokenOut
from app.services.auth_service import (
    registrar_usuario,
    autenticar_usuario,
    create_access_token,
)
from app.services.exceptions import EmailDuplicadoError, CredencialesInvalidasError

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
):
    """Registra un nuevo usuario en el sistema."""
    try:
        return registrar_usuario(db=db, datos=datos)
    except EmailDuplicadoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/token", response_model=TokenOut)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Autentica a un usuario y genera un token de acceso JWT."""
    try:
        usuario = autenticar_usuario(
            db=db,
            email=form_data.username,
            password=form_data.password,
        )
    except CredencialesInvalidasError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": usuario.email})
    return TokenOut(access_token=access_token, token_type="bearer")
