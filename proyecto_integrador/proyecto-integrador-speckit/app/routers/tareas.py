"""Router para gestión de tareas de usuarios."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.routers.deps import get_current_user
from app.schemas.tarea import TareaCreate, TareaOut, TareaUpdateEstado, PrioridadEnum, EstadoEnum
from app.services.tareas_service import (
    crear_tarea,
    cambiar_estado_tarea,
    listar_tareas,
    obtener_tarea_por_id,
    eliminar_tarea,
)
from app.services.exceptions import (
    LimitePrioridadAltaExcedidoError,
    LimiteWIPExcedidoError,
    TransicionEstadoInvalidaError,
    RecursoAjenoError,
    RecursoNoEncontradoError,
)

router = APIRouter(prefix="/tareas", tags=["tareas"])


@router.post("/", response_model=TareaOut, status_code=status.HTTP_201_CREATED)
def crear_nueva_tarea(
    datos: TareaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea una nueva tarea para el usuario autenticado (Artículo IV.4)."""
    try:
        return crear_tarea(datos=datos, usuario_id=current_user.id, db=db)
    except LimitePrioridadAltaExcedidoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[TareaOut])
def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    estado: Optional[EstadoEnum] = None,
    prioridad: Optional[PrioridadEnum] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista las tareas pertenecientes al usuario autenticado con paginación y filtros opcionales."""
    return listar_tareas(
        usuario_id=current_user.id,
        skip=skip,
        limit=limit,
        estado=estado,
        prioridad=prioridad,
        db=db,
    )


@router.get("/{id}", response_model=TareaOut)
def obtener_detalle(
    id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene el detalle de una tarea por ID para el usuario autenticado."""
    try:
        return obtener_tarea_por_id(tarea_id=id, usuario_id=current_user.id, db=db)
    except RecursoAjenoError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except RecursoNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch("/{id}/estado", response_model=TareaOut)
def actualizar_estado_tarea(
    id: int,
    datos: TareaUpdateEstado,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el estado de una tarea aplicando reglas de negocio de transición y WIP."""
    try:
        return cambiar_estado_tarea(
            tarea_id=id,
            nuevo_estado=datos.estado,
            usuario_id=current_user.id,
            db=db,
        )
    except (LimiteWIPExcedidoError, TransicionEstadoInvalidaError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RecursoAjenoError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except RecursoNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_tarea(
    id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina permanentemente una tarea perteneciente al usuario autenticado (Artículo IV.4)."""
    try:
        eliminar_tarea(tarea_id=id, usuario_id=current_user.id, db=db)
    except RecursoAjenoError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except RecursoNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
