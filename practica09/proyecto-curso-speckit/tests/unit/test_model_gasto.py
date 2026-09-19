from app.models.gasto import Gasto
from app.models.usuario import Usuario
from app.database import Base

def test_gasto_model_definition():
    assert issubclass(Gasto, Base)
    assert Gasto.__tablename__ == "gastos"
    g = Gasto(id=1, usuario_id=10, descripcion="Almuerzo", monto=25.0, categoria="comida")
    assert g.id == 1
    assert g.usuario_id == 10
    assert g.descripcion == "Almuerzo"
    assert g.monto == 25.0
    assert g.categoria == "comida"

def test_gasto_in_db(db_session):
    u = Usuario(email="gasto_user@test.com", hashed_password="hashed_val")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    g = Gasto(usuario_id=u.id, descripcion="Cena", monto=50.0, categoria="comida")
    db_session.add(g)
    db_session.commit()
    db_session.refresh(g)
    assert g.id is not None
    assert g.usuario_id == u.id
