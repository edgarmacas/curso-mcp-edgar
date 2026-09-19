---
name: qa-security
description: Revisa el proyecto en busca de secretos expuestos, validación de entradas insuficiente y manejo de excepciones riesgoso.
---
# Instrucciones
1. Busca claves/contraseñas escritas directamente en el código.
2. Revisa validación de entradas (tipo, formato, longitud, rango).
3. Busca `except:` genérico o `except: pass`.
4. Reporta en esta tabla:

| Caso | Lo que se encontró | Corrección sugerida |
|---|---|---|
| 🔑 Secreto expuesto | [hallazgo o "sin hallazgos"] | [sugerencia] |
| 🧪 Validación de entradas | [hallazgo o "sin hallazgos"] | [sugerencia] |
| 🚪 Manejo de excepciones | [hallazgo o "sin hallazgos"] | [sugerencia] |

5. Sin importar si encontraste un secreto quemado en código o no, asegúrate de que exista el patrón correcto para manejarlos en el futuro. **No confíes en leer `.gitignore` como texto — verifica con git directamente**, porque el archivo puede decir cualquier cosa sin que git realmente lo respete, o puede perder una línea entre una corrida y otra sin que se note a simple vista:
   - Si no existe `.env.example`, créalo (con las claves esperadas del proyecto, **sin valores reales** — solo el nombre).
   - Si existe `.env`, corre `git check-ignore -q .env`. Si el código de salida no es 0, `.env` NO está ignorado de verdad — agrega la línea a `.gitignore` y vuelve a verificar, no des por hecho que quedó bien solo por haberla escrito.
   - Si existe `.env`, corre también `git ls-files --error-unmatch .env`. Si el código de salida es 0, `.env` ya está trackeado por git — esto es mucho más grave que solo faltar en `.gitignore`: el secreto puede ya estar en el historial. Repórtalo como hallazgo crítico aparte, no lo mezcles con "sin hallazgos".
   - Si sí encontraste un secreto quemado, la corrección sugerida en la tabla debe ser explícita: moverlo a una variable de entorno leída con `os.environ.get(...)` (o `python-dotenv`), nunca dejarlo como valor literal en el código.
6. Debajo de la tabla (no dentro — la tabla se queda en exactamente 3 filas), agrega una sección `## Acciones de higiene aplicadas` listando cada cosa que hiciste en el punto 5 (ej. "Agregué `.env` a `.gitignore`, no estaba ignorado") o "Ninguna, ya estaba en orden" si no hiciste nada. Una corrección real que no se reporta es tan mala como si no se hubiera hecho.
7. Guarda la tabla completa MÁS la sección de acciones en `hallazgos-seguridad.md` (sobrescribiendo si ya existe) — no te quedes solo con mostrarlo en el chat, el archivo es el entregable.
8. No corrijas el código de negocio automáticamente — la única acción que sí tomas por tu cuenta es la del punto 5 (higiene de `.env.example`/`.gitignore`), el resto solo lo diagnosticas.
