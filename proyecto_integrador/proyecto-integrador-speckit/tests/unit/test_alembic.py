"""Tests unitarios para la configuración y ejecución de migraciones con Alembic."""

import os
import tempfile
import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect


def test_alembic_configuration_and_migration_cycle():
    """Valida que Alembic pueda aplicar y revertir migraciones sobre una base de datos limpia."""
    ini_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../alembic.ini"))
    assert os.path.exists(ini_path), "El archivo alembic.ini debe existir en la raíz"

    with tempfile.NamedTemporaryFile(suffix=".db") as tmp_db:
        tmp_db_url = f"sqlite:///{tmp_db.name}"

        # Configurar Alembic con la base de datos temporal
        alembic_cfg = Config(ini_path)
        alembic_cfg.set_main_option("sqlalchemy.url", tmp_db_url)

        # 1. Ejecutar upgrade head
        command.upgrade(alembic_cfg, "head")

        engine = create_engine(tmp_db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Verificar que las tablas esperadas fueron creadas
        assert "usuarios" in tables
        assert "tareas" in tables
        assert "alembic_version" in tables

        # Verificar columnas de usuarios
        user_cols = [c["name"] for c in inspector.get_columns("usuarios")]
        assert "id" in user_cols
        assert "email" in user_cols
        assert "password_hash" in user_cols
        assert "creado_en" in user_cols

        # Verificar columnas de tareas
        task_cols = [c["name"] for c in inspector.get_columns("tareas")]
        assert "id" in task_cols
        assert "usuario_id" in task_cols
        assert "titulo" in task_cols
        assert "prioridad" in task_cols
        assert "estado" in task_cols

        # 2. Ejecutar downgrade base
        command.downgrade(alembic_cfg, "base")

        inspector_post_downgrade = inspect(engine)
        tables_post = inspector_post_downgrade.get_table_names()
        assert "usuarios" not in tables_post
        assert "tareas" not in tables_post
