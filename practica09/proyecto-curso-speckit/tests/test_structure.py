import importlib
import pytest

PACKAGES = [
    "app",
    "app.models",
    "app.schemas",
    "app.repositories",
    "app.services",
    "app.routers",
    "app.utils",
    "app.mcp",
]

@pytest.mark.parametrize("package_name", PACKAGES)
def test_package_import(package_name):
    mod = importlib.import_module(package_name)
    assert mod is not None
