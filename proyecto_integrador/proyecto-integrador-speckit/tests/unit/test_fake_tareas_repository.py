from tests.fakes.fake_tareas_repository import FakeTareasRepository


def test_fake_tareas_repository_crud():
    repo = FakeTareasRepository()

    # 1. Crear tareas para usuario 1
    t1 = repo.crear_tarea({"titulo": "Tarea 1", "prioridad": "alta"}, usuario_id=1)
    t2 = repo.crear_tarea({"titulo": "Tarea 2", "prioridad": "alta"}, usuario_id=1)
    t3 = repo.crear_tarea({"titulo": "Tarea Usuario 2", "prioridad": "baja"}, usuario_id=2)

    assert t1["id"] == 1
    assert t2["id"] == 2
    assert t3["id"] == 3

    # 2. Conteo de abiertas por prioridad
    assert repo.contar_abiertas_por_prioridad(usuario_id=1, prioridad="alta") == 2
    assert repo.contar_abiertas_por_prioridad(usuario_id=1, prioridad="baja") == 0
    assert repo.contar_abiertas_por_prioridad(usuario_id=2, prioridad="baja") == 1

    # 3. Aislamiento por usuario
    assert repo.obtener_por_id(tarea_id=1, usuario_id=1) is not None
    assert repo.obtener_por_id(tarea_id=1, usuario_id=2) is None
    assert repo.buscar_por_id_global(tarea_id=1) is not None

    # 4. Actualizar estado y conteo por estado
    assert repo.contar_por_estado(usuario_id=1, estado="en_progreso") == 0
    repo.actualizar_estado(tarea_id=1, usuario_id=1, nuevo_estado="en_progreso")
    assert repo.contar_por_estado(usuario_id=1, estado="en_progreso") == 1

    # 5. Listar tareas con paginación
    tareas_u1 = repo.listar_tareas(usuario_id=1, skip=0, limit=10)
    assert len(tareas_u1) == 2

    # 6. Eliminar tarea
    assert repo.eliminar_tarea(tarea_id=1, usuario_id=2) is False
    assert repo.eliminar_tarea(tarea_id=1, usuario_id=1) is True
    assert repo.obtener_por_id(tarea_id=1, usuario_id=1) is None
