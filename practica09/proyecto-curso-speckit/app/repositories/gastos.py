from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.gasto import Gasto


def guardar(db: Session, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict:
    gasto = Gasto(usuario_id=usuario_id, descripcion=descripcion, monto=monto, categoria=categoria)
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return {
        "id": gasto.id,
        "usuario_id": gasto.usuario_id,
        "descripcion": gasto.descripcion,
        "monto": gasto.monto,
        "categoria": gasto.categoria,
        "fecha": gasto.fecha.isoformat() if getattr(gasto, "fecha", None) else None,
    }


def listar(db: Session, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
    gastos = (
        db.query(Gasto)
        .filter(Gasto.usuario_id == usuario_id)
        .order_by(Gasto.fecha.desc(), Gasto.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": g.id,
            "usuario_id": g.usuario_id,
            "descripcion": g.descripcion,
            "monto": g.monto,
            "categoria": g.categoria,
            "fecha": g.fecha.isoformat() if getattr(g, "fecha", None) else None,
        }
        for g in gastos
    ]


def total_por_categoria(db: Session, usuario_id: int, categoria: str) -> float:
    total = (
        db.query(func.sum(Gasto.monto))
        .filter(Gasto.usuario_id == usuario_id, Gasto.categoria == categoria)
        .scalar()
    )
    return float(total) if total is not None else 0.0
