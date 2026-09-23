# Environment Check — Class 1

| Component | Status | Detail |
| :--- | :---: | :--- |
| **Python 3.12** | `OK` | 3.12.3 |
| **uv** | `OK` | uv 0.11.7 (x86_64-unknown-linux-gnu) |
| **Git** | `OK` | git version 2.43.0 |
| **Docker** | `OK` | Docker version 29.7.2, build a7dcaa6 |
| **.gitignore protects .env** | `OK` | protects `.env` |

> **Status:** Environment ready. See you in Class 2.

---

## Clase 2 — APIs de IA Generativa y memoria conversacional

### Conversación de 8 turnos (Paso 7)

Ver evidencia en [`entregas/s02/evidencia/memoria.png`](entregas/s02/evidencia/memoria.png) y [`entregas/s02/evidencia/memoria.txt`](entregas/s02/evidencia/memoria.txt).

```text
=== INICIANDO CONVERSACIÓN DE 8 TURNOS ===

--- Turno 1 ---
Usuario : Me llamo Edgar y mi color favorito es el azul.
[48 tokens | finish=FinishReason.STOP]
Modelo  : ¡Hola, Edgar! Un gusto. El azul es un excelente color. ¿En qué te puedo ayudar hoy?

--- Turno 2 ---
Usuario : ¿Qué framework de Python vimos en la Clase 1?
[503] Error del servidor. Reintentando en 1s...
[503] Error del servidor. Reintentando en 2s...
[93 tokens | finish=FinishReason.STOP]
Modelo  : No me lo has mencionado antes. ¿De qué curso o clase estamos hablando? Si me das un poco más de contexto, con gusto te ayudo.

--- Turno 3 ---
Usuario : Dame un ejemplo de dato que no cabe en un int.
[503] Error del servidor. Reintentando en 1s...
[227 tokens | finish=FinishReason.STOP]
Modelo  : En Python, los `int` tienen precisión ilimitada, por lo que cualquier entero cabe. 

Sin embargo, en **lenguajes tradicionales** (como C, C++ o Java) donde un `int` es de 32 bits, el valor máximo es **2,147,483,647**. 

Un ejemplo de dato que **no cabe** en ese `int` es:

**`2,147,483,648`** (o cualquier número decimal como `3.14`).

--- Turno 4 ---
Usuario : ¿Qué hace el comando uv init?
[503] Error del servidor. Reintentando en 1s...
[349 tokens | finish=FinishReason.STOP]
Modelo  : El comando `uv init` inicializa un **nuevo proyecto de Python** usando *uv* (el gestor de paquetes de Cargo/Rust para Python). 

Al ejecutarlo, crea automáticamente la estructura básica del proyecto:
* Un archivo `pyproject.toml` (para configurar el proyecto y sus dependencias).
* Un archivo `.python-version` (para fijar la versión de Python).
* Un archivo `hello.py` (o `main.py`) como punto de entrada.
* Un archivo `.gitignore`.

--- Turno 5 ---
Usuario : Explica en una frase qué es un token.
[402 tokens | finish=FinishReason.STOP]
Modelo  : En procesamiento de lenguaje e IA, un **token** es la unidad básica de texto (como una palabra, parte de ella o un símbolo) que un modelo utiliza para procesar y comprender el lenguaje.

--- Turno 6 ---
Usuario : ¿Qué significa que una API sea stateless?
[451 tokens | finish=FinishReason.STOP]
Modelo  : Significa que la API **no guarda ninguna información del usuario ni del contexto entre peticiones**; cada solicitud del cliente debe contener todos los datos necesarios para ser procesada de forma independiente.

--- Turno 7 ---
Usuario : ¿Para qué sirve un archivo .env?
[499 tokens | finish=FinishReason.STOP]
Modelo  : Sirve para almacenar **variables de entorno y datos sensibles** (como claves de API, contraseñas o configuraciones) de forma segura y separada del código fuente del proyecto.

--- Turno 8 ---
Usuario : ¿Cómo me llamo y cuál es mi color favorito?
[528 tokens | finish=FinishReason.STOP]
Modelo  : Te llamas **Edgar** y tu color favorito es el **azul**.
```

### Por qué elegí ventana deslizante

Elegí guardar solo los últimos mensajes (ventana deslizante) porque es la forma más sencilla y rápida de darle memoria al chat sin complicarnos. Si usáramos otras alternativas, como pedirle a la IA que haga un resumen de la conversación a cada momento, gastaríamos tokens de más y las respuestas tardarían más tiempo. Y usar una base de datos externa para una charla corta era demasiado rollo. Así solo conservamos los últimos turnos en una lista simple: el modelo recuerda lo reciente y evitamos pasarnos del límite de tokens.

### Límite de solicitudes provocado (Paso 9)

Ver evidencia en [`entregas/s02/evidencia/rate_limit.png`](entregas/s02/evidencia/rate_limit.png) y [`entregas/s02/evidencia/rate_limit.txt`](entregas/s02/evidencia/rate_limit.txt).

Provocamos el error 429 a propósito mandando varias preguntas seguidas para superar el límite de 5 peticiones por minuto del plan gratuito. En lugar de que el script se cayera con un error feo, el código atrapó el fallo y fue esperando unos segundos (1s, 2s, 4s...) para reintentar la llamada automáticamente sin romperse.

---

## Proyecto Integrador — Sesión 10: De la arquitectura a los agentes

Sistema de Gestión de Tareas Personales con Límite de Capacidad (WIP Limits) desarrollado mediante **Spec-Driven Development** con **Spec Kit** y **Google Antigravity**.

* **Código y documentación:** [`proyecto_integrador/proyecto-integrador-speckit/`](proyecto_integrador/proyecto-integrador-speckit/)
* **Instrucciones de ejecución con `uv`:** [`proyecto_integrador/proyecto-integrador-speckit/README.md`](proyecto_integrador/proyecto-integrador-speckit/README.md)
* **Evidencias fotográficas (Capturas 1 a 25):** [`proyecto_integrador/evidencias/`](proyecto_integrador/evidencias/)