# OCP: agregar una categoría nueva = agregar un valor aquí.
CATEGORIAS_PERMITIDAS = {"comida", "transporte", "entretenimiento", "otros"}


def categoria_valida(categoria: str) -> bool:
    return categoria in CATEGORIAS_PERMITIDAS
