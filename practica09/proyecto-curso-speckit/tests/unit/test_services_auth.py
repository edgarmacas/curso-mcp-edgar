import pytest
from app.services.auth import (
    registrar_usuario,
    autenticar_usuario,
    EmailYaRegistradoError,
    CredencialesInvalidasError,
)
from app.models.usuario import Usuario
from app.utils.security import hash_password


class RepositorioFalsoUsuarios:
    """Implementación falsa en memoria para pruebas unitarias de services (Art. II.3, VII.2). Prohibido unittest.mock."""

    def __init__(self):
        self.usuarios = {}
        self._next_id = 1

    def obtener_por_email(self, db, email: str):
        return self.usuarios.get(email)

    def guardar(self, db, email: str, hashed_password: str):
        usuario = Usuario(id=self._next_id, email=email, hashed_password=hashed_password)
        self.usuarios[email] = usuario
        self._next_id += 1
        return usuario


def test_registrar_usuario_exito():
    repo = RepositorioFalsoUsuarios()
    user = registrar_usuario(None, "user@test.com", "Password123!", repo=repo)
    assert user.id == 1
    assert user.email == "user@test.com"
    assert user.hashed_password != "Password123!"


def test_registrar_usuario_email_duplicado():
    repo = RepositorioFalsoUsuarios()
    registrar_usuario(None, "duplicado@test.com", "Password123!", repo=repo)
    with pytest.raises(EmailYaRegistradoError):
        registrar_usuario(None, "duplicado@test.com", "OtraPassword456!", repo=repo)


def test_autenticar_usuario_exito():
    repo = RepositorioFalsoUsuarios()
    registrar_usuario(None, "login@test.com", "Password123!", repo=repo)
    user = autenticar_usuario(None, "login@test.com", "Password123!", repo=repo)
    assert user.email == "login@test.com"


def test_autenticar_usuario_credenciales_invalidas():
    repo = RepositorioFalsoUsuarios()
    registrar_usuario(None, "login@test.com", "Password123!", repo=repo)

    # Contraseña incorrecta
    with pytest.raises(CredencialesInvalidasError):
        autenticar_usuario(None, "login@test.com", "WrongPassword", repo=repo)

    # Usuario no existente
    with pytest.raises(CredencialesInvalidasError):
        autenticar_usuario(None, "noexiste@test.com", "Password123!", repo=repo)


def test_services_usuarios_alias():
    import app.services.usuarios as su
    repo = RepositorioFalsoUsuarios()
    u = su.registrar_usuario(None, "alias@test.com", "pass123", repo=repo)
    assert u.email == "alias@test.com"
    auth = su.autenticar_usuario(None, "alias@test.com", "pass123", repo=repo)
    assert auth.id == u.id
