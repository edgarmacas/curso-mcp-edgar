"""Excepciones de dominio y reglas de negocio del sistema."""


class ReglaNegocioError(Exception):
    """Excepción base para violaciones de reglas de negocio."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class LimitePrioridadAltaExcedidoError(ReglaNegocioError):
    """Lanzada cuando un usuario intenta superar el límite de 2 tareas de prioridad alta abiertas."""

    def __init__(
        self,
        mensaje: str = "No se pueden tener más de 2 tareas de prioridad alta abiertas simultáneamente.",
    ):
        super().__init__(mensaje)


class LimiteWIPExcedidoError(ReglaNegocioError):
    """Lanzada cuando un usuario intenta superar el límite de 3 tareas en progreso."""

    def __init__(
        self,
        mensaje: str = "No se pueden tener más de 3 tareas en progreso simultáneamente.",
    ):
        super().__init__(mensaje)


class TransicionEstadoInvalidaError(ReglaNegocioError):
    """Lanzada cuando se intenta una transición no permitida en la máquina de estados."""

    def __init__(
        self,
        mensaje: str = "Transición de estado inválida.",
    ):
        super().__init__(mensaje)


class RecursoAjenoError(ReglaNegocioError):
    """Lanzada cuando un usuario intenta acceder o modificar un recurso que no le pertenece."""

    def __init__(
        self,
        mensaje: str = "No tiene permiso para acceder o modificar este recurso.",
    ):
        super().__init__(mensaje)


class RecursoNoEncontradoError(ReglaNegocioError):
    """Lanzada cuando un recurso solicitado por ID no existe."""

    def __init__(
        self,
        mensaje: str = "El recurso solicitado no fue encontrado.",
    ):
        super().__init__(mensaje)


class EmailDuplicadoError(ReglaNegocioError):
    """Lanzada cuando se intenta registrar un usuario con un correo ya existente."""

    def __init__(
        self,
        mensaje: str = "El correo electrónico ya se encuentra registrado.",
    ):
        super().__init__(mensaje)


class CredencialesInvalidasError(ReglaNegocioError):
    """Lanzada cuando la autenticación falla por credenciales incorrectas."""

    def __init__(
        self,
        mensaje: str = "Credenciales de autenticación inválidas.",
    ):
        super().__init__(mensaje)
