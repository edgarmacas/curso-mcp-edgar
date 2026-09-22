"""Servicio de autenticación, hashing y manejo de tokens JWT."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.repositories.usuarios_repository import usuarios_repository, UsuariosRepository
from app.services.exceptions import EmailDuplicadoError, CredencialesInvalidasError

# Contexto de hashing con bcrypt (Artículo IV.1)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Genera un hash seguro para la contraseña."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT firmado con HS256 y tiempo de expiración finito (Artículo IV.2)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decodifica y valida la firma y expiración de un token JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except jwt.PyJWTError as e:
        raise CredencialesInvalidasError(f"Token inválido o expirado: {str(e)}")


def registrar_usuario(
    db: Session,
    datos: UsuarioCreate,
    repo: UsuariosRepository = usuarios_repository,
) -> Usuario:
    """Registra un nuevo usuario en el sistema verificando que el email sea único."""
    existente = repo.obtener_por_email(db, datos.email)
    if existente:
        raise EmailDuplicadoError("El correo electrónico ya se encuentra registrado.")

    hashed = hash_password(datos.password)
    return repo.crear_usuario(db, email=datos.email, password_hash=hashed)


def autenticar_usuario(
    db: Session,
    email: str,
    password: str,
    repo: UsuariosRepository = usuarios_repository,
) -> Usuario:
    """Autentica un usuario verificando su email y contraseña."""
    usuario = repo.obtener_por_email(db, email)
    if not usuario:
        raise CredencialesInvalidasError("Credenciales de autenticación inválidas.")
    if not verify_password(password, usuario.password_hash):
        raise CredencialesInvalidasError("Credenciales de autenticación inválidas.")
    return usuario
