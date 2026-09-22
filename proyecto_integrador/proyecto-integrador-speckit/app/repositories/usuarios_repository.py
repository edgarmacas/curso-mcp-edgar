"""Repositorio de persistencia para usuarios."""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


class UsuariosRepository:
    """Operaciones de base de datos para la entidad Usuario."""

    def crear_usuario(self, db: Session, email: str, password_hash: str) -> Usuario:
        usuario = Usuario(
            email=email,
            password_hash=password_hash,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    def obtener_por_email(self, db: Session, email: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.email == email).first()

    def obtener_por_id(self, db: Session, usuario_id: int) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()


usuarios_repository = UsuariosRepository()
