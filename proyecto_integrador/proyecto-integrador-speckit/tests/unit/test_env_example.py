import os
from pathlib import Path

def test_env_example_contains_all_required_variables():
    project_root = Path(__file__).resolve().parent.parent.parent
    env_example_path = project_root / ".env.example"

    assert env_example_path.exists(), ".env.example must exist in project root"

    content = env_example_path.read_text()
    required_keys = [
        "DATABASE_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "MCP_USER_EMAIL",
    ]

    for key in required_keys:
        assert f"{key}=" in content, f"Key '{key}' is missing from .env.example"

def test_gitignore_excludes_env_file():
    project_root = Path(__file__).resolve().parent.parent.parent
    gitignore_path = project_root / ".gitignore"

    assert gitignore_path.exists(), ".gitignore must exist in project root"

    content = gitignore_path.read_text().splitlines()
    assert any(line.strip() == ".env" for line in content), ".env must be explicitly ignored in .gitignore"
