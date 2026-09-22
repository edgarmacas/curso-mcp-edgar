from app.services.exceptions import (
    ReglaNegocioError,
    LimitePrioridadAltaExcedidoError,
    LimiteWIPExcedidoError,
    TransicionEstadoInvalidaError,
    RecursoAjenoError,
    RecursoNoEncontradoError,
    EmailDuplicadoError,
    CredencialesInvalidasError,
)


def test_exception_inheritance_and_messages():
    exceptions = [
        LimitePrioridadAltaExcedidoError(),
        LimiteWIPExcedidoError(),
        TransicionEstadoInvalidaError(),
        RecursoAjenoError(),
        RecursoNoEncontradoError(),
        EmailDuplicadoError(),
        CredencialesInvalidasError(),
    ]

    for exc in exceptions:
        assert isinstance(exc, ReglaNegocioError)
        assert isinstance(exc, Exception)
        assert str(exc) == exc.mensaje
        assert len(exc.mensaje) > 0
