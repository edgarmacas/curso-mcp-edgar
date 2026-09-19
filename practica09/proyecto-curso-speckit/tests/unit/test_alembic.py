import os
import importlib.util
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.database import Base

def test_alembic_ini_exists():
    assert os.path.exists("alembic.ini")
    config = Config("alembic.ini")
    assert config.get_main_option("script_location") is not None
    script = ScriptDirectory.from_config(config)
    assert script is not None

def test_alembic_env_file():
    assert os.path.exists("alembic/env.py")
    spec = importlib.util.spec_from_file_location("local_alembic_env", "alembic/env.py")
    assert spec is not None
    assert spec.loader is not None


def test_alembic_initial_migration_exists():
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    head_rev = script.get_current_head()
    assert head_rev is not None
    revision_obj = script.get_revision(head_rev)
    assert revision_obj is not None
    assert "crear_tablas_usuarios_y_gastos" in revision_obj.doc
