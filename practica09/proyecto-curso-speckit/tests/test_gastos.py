import pytest
from app.services import gastos as gastos_service
from app.services.gastos import LimiteExcedidoError, CategoriaInvalidaError


class RepositorioFalso:
    """Test double: mismo contrato que app/repositories/gastos.py, sin persistencia real."""

    def __init__(self, total_inicial_por_categoria: float = 0.0):
        self._gastos: list[dict] = []
        self._total_inicial = total_inicial_por_categoria

    def guardar(self, db, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict:
        gasto = {
            "id": len(self._gastos) + 1,
            "usuario_id": usuario_id,
            "descripcion": descripcion,
            "monto": monto,
            "categoria": categoria,
        }
        self._gastos.append(gasto)
        return gasto

    def listar(self, db, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
        return self._gastos[skip: skip + limit]

    def total_por_categoria(self, db, usuario_id: int, categoria: str) -> float:
        return self._total_inicial + sum(
            g["monto"] for g in self._gastos if g["categoria"] == categoria
        )


def test_registrar_gasto_exitoso():
    repo = RepositorioFalso()

    resultado = gastos_service.registrar_gasto(None, 1, "Almuerzo", 12.50, "comida", repo=repo)

    assert resultado["descripcion"] == "Almuerzo"
    assert repo.listar(None, 1) == [resultado]


def test_registrar_gasto_monto_invalido_lanza_error():
    # Caso de Error 1: monto <= 0
    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "Café", -5.0, "comida", repo=RepositorioFalso())

    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "Café", 0.0, "comida", repo=RepositorioFalso())


def test_registrar_gasto_descripcion_vacia_lanza_error():
    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "", 10.0, "comida", repo=RepositorioFalso())

    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "   ", 10.0, "comida", repo=RepositorioFalso())


def test_registrar_gasto_categoria_invalida_lanza_error():
    # Caso de Error 2: categoría inexistente
    with pytest.raises(CategoriaInvalidaError):
        gastos_service.registrar_gasto(
            None, 1, "Cine", 20.0, "categoria-inventada", repo=RepositorioFalso()
        )


def test_registrar_gasto_excede_limite_categoria_lanza_error():
    # Caso de Error 3: excede el límite de 500 en su categoría
    repo = RepositorioFalso(total_inicial_por_categoria=490.0)

    with pytest.raises(LimiteExcedidoError):
        gastos_service.registrar_gasto(None, 1, "Cena cara", 50.0, "comida", repo=repo)


def test_registrar_gasto_limite_exacto_500():
    repo = RepositorioFalso(total_inicial_por_categoria=450.0)
    resultado = gastos_service.registrar_gasto(None, 1, "Cena justa", 50.0, "comida", repo=repo)
    assert resultado["monto"] == 50.0
