import importlib
import pytest
import bcrypt

CRITICAL_MODULES = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "alembic",
    "jwt",
    "passlib",
    "bcrypt",
    "pydantic_settings",
    "email_validator",
    "multipart",
    "mcp",
    "pytest_cov",
    "httpx",
]

@pytest.mark.parametrize("module_name", CRITICAL_MODULES)
def test_dependency_import(module_name):
    mod = importlib.import_module(module_name)
    assert mod is not None

def test_bcrypt_version_compatibility():
    # Constitution Art. IV.1 requires passlib compatibility (bcrypt < 4.1)
    version_tuple = tuple(map(int, bcrypt.__version__.split(".")[:2]))
    assert version_tuple < (4, 1), f"bcrypt version {bcrypt.__version__} must be < 4.1 for passlib 1.7.4 compatibility"
