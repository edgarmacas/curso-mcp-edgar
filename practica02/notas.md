# Bitácora de Experimento — Vibe Coding (Notas del Alumno)

---

## Ronda 1 — Validador de Contraseñas

### 1. Predicciones (ANTES de ejecutar el pedido)
- **¿Cuántos caracteres mínimos crees que va a exigir?**
  8
- **¿Va a pedir mayúsculas, números o símbolos?**
  Texto libre porque no especificamos qué tipo de datos permitirá ingresar.
- **¿Qué crees que pasa si le mandas una contraseña vacía?**
  Debería validar que ingrese al menos un carácter.

### 2. Resultados Reales y Comparación

| Pregunta / Aspecto | Tu Predicción | Tu Resultado Real | ¿Coincide con lo del Instructor? |
|---|---|---|---|
| **Longitud mínima exigida** | 8 caracteres | 12 caracteres por defecto | Difiere en la cantidad por defecto |
| **¿Pidió símbolo / mayúscula / número?** | Texto libre sin restricciones | Exigió Mayúsculas (A-Z), Minúsculas (a-z), Números (0-9) y Símbolos especiales | Difiere; creó reglas complejas de entropía |
| **¿Qué pasó con la contraseña vacía?** | Validar que ingrese un carácter | Retornó `is_valid: False`, puntaje 0/100 y error: *"La contraseña no puede estar vacía"* | Coincide parcialmente en la validación |

---

## Ronda 2 — Agregar Validación de Email

### 1. Predicciones (ANTES de ejecutar el pedido)
- **¿Crees que el agente va a mantener el mismo estilo de respuesta que en la Ronda 1, o lo va a cambiar?**
  Sí, debería seguir la misma estructura modular que ya construyó.
- **¿Qué crees que hace con un email mal escrito como `ana@`?**
  Debería validarlo indicando que es incorrecto.

### 2. Resultados Reales y Comparación

| Pregunta / Aspecto | Tu Predicción | Tu Resultado Real |
|---|---|---|
| **¿Mantuvo el mismo formato de respuesta de la Ronda 1?** | Sí, misma estructura | Sí, creó una clase modular `EmailValidator` integrada con la estructura previa |
| **¿Qué hizo con el email mal formado (`ana@`)?** | Validar como incorrecto | Retornó `is_valid: False` con el error específico: *"Falta el dominio después del '@'"* |

- **Observación adicional:** Al probar `usuario@gamil.com`, el agente no solo validó la sintaxis RFC 5322, sino que añadió una sugerencia inteligente de corrección de tipeo: *"¿Quisiste decir 'usuario@gmail.com'?"*.

---

## Ronda 3 — Lista de Varios Usuarios

### 1. Predicciones (ANTES de ejecutar el pedido)
- **¿Crees que algo de lo que ya funcionaba en la Ronda 1 o 2 se va a romper con este cambio?**
  No debería romperse si mantiene la modularidad, pero podría haber conflictos al iterar la lista.
- **¿Cómo crees que va a estructurar la lista de usuarios?**
  Como una lista de diccionarios en Python `[{'email': ..., 'password': ...}]`.

### 2. Resultados Reales y Comparación

| Pregunta / Aspecto | Tu Predicción | Tu Resultado Real |
|---|---|---|
| **¿Se rompió algo que ya funcionaba? ¿Qué?** | No debería romperse | No se rompió la validación individual, pero agregante reglas grupales automáticas (detección de correos duplicados y claves reutilizadas) |
| **¿Cómo estructuró la lista de usuarios?** | Lista de diccionarios | Creó la clase `UserBatchValidator` procesando una lista de diccionarios con reporte consolidado del sistema |

---

## Bloque de Cierre — Provocar la Falla en Vivo

### Pedido ejecutado:
> *"ahora que la validación de contraseña sea opcional para usuarios administradores"*

### Predicción y Análisis de Falla:
- **¿Qué crees que puede salir mal con este cambio?**
  Se introduce un riesgo de seguridad donde una cuenta con rol de Administrador puede registrarse sin contraseña o con una contraseña extremadamente débil (`123`), quedando marcada como válida simplemente por poseer privilegios.
- **Comportamiento o inconsistencia detectada en el código:**
  - El sistema omitió la validación de contraseña para los admins, pero si un usuario común se registra como `admin` puede eludir los controles de fortaleza de claves.
  - En las métricas del sistema, el promedio global de fortaleza de claves se distorsionó al omitirse el cálculo para los administradores sin contraseña.

---

## Reflexión Final

1. **¿En qué ronda tu predicción se alejó más de lo que realmente pasó? ¿Por qué crees que fallaste esa predicción?**
   - En la **Ronda 1**. Yo predije un validador básico de 8 caracteres con texto libre, pero el agente de IA construyó por su cuenta un motor avanzado con cálculo de Entropía de Shannon (bits), estimación de tiempo de descifrado por fuerza bruta (GPU/Supercomputadora) y comprobación de secuencias de teclado (`qwerty`, `12345`). Fallé la predicción porque no había una especificación formal (*spec*) y el agente asumió requerimientos complejos por defecto.

2. **¿Tu resultado fue exactamente igual al del instructor en todas las rondas, o hubo diferencias con el mismo pedido? ¿Qué te dice eso sobre pedir cosas sin spec?**
   - Hubo diferencias significativas en el diseño de las clases, mensajes de retorno y reglas aplicadas. Esto demuestra que pedir características a un LLM/Agente sin una especificación clara (*Vibe Coding sin spec*) produce resultados no deterministas: la IA toma decisiones de arquitectura y comportamiento de manera arbitraria según el contexto.

3. **Completa la frase:**
   > *"Si yo tuviera que darle este código a otra persona mañana, tendría que explicarle **las reglas de negocio implícitas que asumió la IA (como los 12 caracteres mínimos, la omisión de clave para administradores y el cálculo de entropía)** porque eso no está escrito en ningún lado."*