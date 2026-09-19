from app.dependencies import get_gastos_repo
from app.repositories import gastos as gastos_repository

def test_get_gastos_repo():
    repo = get_gastos_repo()
    assert repo is gastos_repository
    assert hasattr(repo, "guardar")
    assert hasattr(repo, "listar")
    assert hasattr(repo, "total_por_categoria")
