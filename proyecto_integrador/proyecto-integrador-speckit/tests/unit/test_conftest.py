from sqlalchemy import text
from sqlalchemy.orm import Session
from tests.fakes.fake_tareas_repository import FakeTareasRepository


def test_db_session_fixture(db_session: Session):
    assert isinstance(db_session, Session)
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_fake_tareas_repo_fixture(fake_tareas_repo: FakeTareasRepository):
    assert isinstance(fake_tareas_repo, FakeTareasRepository)
    tarea = fake_tareas_repo.crear_tarea({"titulo": "Fixture task"}, usuario_id=1)
    assert tarea["id"] == 1
