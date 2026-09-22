"""Modelo ORM para Usuario."""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.date_utils import now_utc


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    creado_en = Column(DateTime(timezone=True), default=now_utc, nullable=False)

    tareas = relationship("Tarea", back_populates="usuario", cascade="all, delete-orphan")

