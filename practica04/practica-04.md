# Guía Práctica — Pruebas, Cobertura y Seguridad (con Skills, Agentes y Hooks)
## Sesión 5 · Jueves · Programación de Backend y MCP en Python para IA Generativa

**Duración de la práctica:** ~80 min en la ruta recomendada (saltando los Bloques C y D manuales, ver nota bajo el cronograma); ~98 min si haces los 5 bloques completos a mano.
**Punto de partida:** el código del miércoles (`mi-proyecto-speckit/`).

**Novedad de hoy:** van a construir una pequeña jerarquía de agentes especializados sobre la base que ya dejó Spec Kit el miércoles.

> 🧑‍🏫 **Nota técnica antes de empezar:** `agy` es el CLI de Google Antigravity, no Claude Code — su formato de agentes y de hooks es distinto, y esta versión de la guía ya está escrita y probada contra ese formato real (no el de Claude Code). Si en algún momento algo no calza con lo que ves en pantalla, revisa primero esta nota antes de improvisar.

## La arquitectura (léela antes de empezar)

```
SKILLS  →  son capacidades puntuales (una tarea, sin criterio propio)
AGENTES →  tienen un rol y un criterio; usan skills específicas para cumplirlo
TÚ (vía agy) → orquestas, invocando a cada agente en el momento correcto
```

Un agente **no es** una skill — un agente **llama** a una o varias skills, con un criterio propio sobre cuándo y cómo usarlas. Hoy van a construir:

- 7 **skills** (`qa-unit`, `qa-integration`, `qa-e2e`, `qa-coverage`, `qa-security`, `qa-report`, `qa-orchestrate`) — escritas a mano, para que entiendan exactamente qué le piden a cada una.
- 3 **agentes** (`tester-agent`, `security-agent`, `report-agent`) — cada uno con un rol acotado **en su propio prompt** (qué hace y qué no hace). Importante: `agy` no tiene una allowlist técnica de "este agente solo puede usar estas skills" — no existe un campo `tools:` ni un sandbox por agente. El límite es disciplina declarada en el texto del agente, no una restricción forzada por la herramienta. Lo vas a comprobar tú mismo en el Bloque C.
- Ustedes, invocando a cada agente en secuencia, hacen de orquestador.

### Cómo se invoca cada cosa (importante, no se mezclan)

| Qué es | Cómo se invoca | Confirmado |
|---|---|---|
| Skill | `/nombre-de-la-skill` | ✅ Sí — así funcionó `/speckit-specify` el miércoles, y así funciona cualquier skill propia en `.agents/skills/` |
| Agente | Lenguaje natural: *"Usa el agente nombre-agente para..."* | ✅ Sí — dispara una invocación real del agente. La primera vez que lo hagas en la sesión, `agy` puede mostrarte un prompt pidiendo aprobar esa acción (es la misma lógica de permisos que ya viste con `run_command`) — apruébalo, o marca "permitir siempre" para no volver a verlo. |
| Agente con `/nombre-agente` | — | ❌ **No funciona.** A diferencia de las skills, `agy` no resuelve `/tester-agent` como una invocación — lo trata como texto suelto y responde de forma genérica, ignorando el agente. No lo intenten. |

Las skills usan `/` porque así lo comprobaste con Spec Kit. Los agentes se invocan en lenguaje natural porque son un concepto de otra capa (un rol con reglas, no un comando suelto) — y a diferencia de las skills, no tienen atajo con `/`.

## Cronograma

| Bloque | Tiempo | Acumulado |
|---|---|---|
| Setup — localizar spec + skills + agentes (con su tarea ya adentro) | 26 min | 26 min |
| A — Invocar al `tester-agent` | 12 min | 38 min |
| Descanso | 5 min | 43 min |
| B — Provocar fallo, ver el hook bloquear, corregir | 15 min | 58 min |
| C — Invocar al `security-agent` | 10 min | 68 min |
| D — Invocar al `report-agent` | 8 min | 76 min |
| E — Automatizar todo: `/qa-orchestrate` | 12 min | 88 min |
| Reflexión sobre la orquestación | 5 min | 93 min |
| Cierre | 5 min | 98 min |

> 🧑‍🏫 **Nota de tiempo:** la versión completa (los 5 bloques a mano, A a E) corre ~98 min, por encima del bloque de práctica habitual. Si vas corto de tiempo, **salta los Bloques C y D manuales** (invocar `security-agent` y `report-agent` uno por uno) e ir directo del Bloque B al Bloque E: la orquestación automática ya los ejecuta a ambos, así que no se pierde contenido — solo la demostración paso a paso de cada uno por separado. Esa ruta corta suma **Setup(26) + A(12) + Descanso(5) + B(15) + E(12) + Reflexión(5) + Cierre(5) = 80 min**, mucho más cerca del bloque habitual.

## Antes de empezar

- [ ] Tu carpeta `mi-proyecto-speckit/` del miércoles con código funcionando.
- [ ] `agy` instalado y autenticado.
- [ ] Instala dependencias:
  ```bash
  cd mi-proyecto-speckit
  uv add --dev pytest pytest-cov pytest-json-report
  ```

---

## Setup — Construir la estructura completa (26 min)

### Paso 1 — Confirmar que tu código corre (2 min)

```bash
uv run python -c "import [tu_modulo]"
```

### Paso 2 — Explorar lo que Spec Kit ya dejó (2 min)

```bash
ls .agents/skills/
```

Ya deberías ver las carpetas de Spec Kit del miércoles (`speckit-specify`, `speckit-plan`, etc.). Hoy agregamos **más skills propias** dentro de esa misma estructura, y por primera vez, una carpeta nueva: `.agents/agents/`.

### Paso 3 — Localizar la spec real, no escribir una nueva (2 min)

Aquí está el punto que evita el vibe coding en las pruebas: si le piden al agente "genera tests" sin más, él decide qué probar — y puede improvisar, igual que el lunes. Pero hoy **no hace falta escribir una spec de pruebas aparte** — Spec Kit ya generó una el miércoles, con más detalle del que ustedes escribirían a mano:

```bash
ls specs/*/spec.md
```

Ábrela y confirma que tiene estas tres secciones — son la fuente de verdad para todo lo que viene hoy:

- **Acceptance Scenarios** (Given/When/Then con valores concretos) → base de los tests unitarios y de integración.
- **Edge Cases** → casos borde, la mayoría ya son tests unitarios de límites.
- **Functional Requirements** (FR-001, FR-002, ...) → cada uno debería tener un test que lo verifique. Revisa si hay algún FR agregado en una revisión posterior (sección `## Clarifications`, si existe) — esos son los candidatos más probables a no estar cubiertos todavía por el código de ayer.

Un `test-spec.md` escrito a mano hoy repetiría lo mismo con menos precisión — sería vibe coding sobre la spec, no anti-vibe-coding. Las skills de hoy leen directo de `specs/*/spec.md`.

> 🧑‍🏫 **Si ya tienen un `tests/integration/` de ayer que usa `subprocess`:** en realidad ya es un test e2e, no de integración — nombrarlo "integración" fue un error de clasificación de ayer, no algo que haya que rehacer. En el Paso 4, la skill `qa-e2e` se encarga de detectarlo y moverlo a `tests/e2e/` sin reescribirlo.

### Paso 4 — Crear las 7 skills de QA, explicadas una por una (13 min)

Vas a escribir cada `SKILL.md` a mano — esto es intencional: cada archivo es corto, y entender exactamente qué le estás pidiendo a la skill es más valioso hoy que generarlas automáticamente.

```bash
mkdir -p .agents/skills/qa-unit .agents/skills/qa-integration .agents/skills/qa-e2e .agents/skills/qa-coverage .agents/skills/qa-security .agents/skills/qa-report .agents/skills/qa-orchestrate
```

**`.agents/skills/qa-unit/SKILL.md`**
```markdown
---
name: qa-unit
description: Audita los tests unitarios existentes contra specs/*/spec.md (Acceptance Scenarios, Edge Cases, Functional Requirements) y agrega solo lo que falta, sin improvisar qué probar ni duplicar lo ya cubierto.
---
# Instrucciones
1. Lee `specs/*/spec.md` — secciones "Acceptance Scenarios", "Edge Cases" y "Functional Requirements" (revisa también `## Clarifications` si existe: ahí suelen vivir los requisitos agregados después de la implementación original). Si no existe ningún `specs/*/spec.md`, DETENTE y pide que se corra Spec Kit primero — no inventes criterios propios.
2. Si existe `tests/unit/`, revisa los tests que ya hay ahí antes de escribir nada.
3. Para cada escenario, caso borde o FR que corresponda a una función aislada: si ya hay un test que lo cubre, repórtalo como "ya cubierto en `<archivo>`" y no lo dupliques. Si no está cubierto, agrégalo con un assert real — dentro del archivo de `tests/unit/` que corresponda por tema, o en uno nuevo si no encaja en ninguno.
4. No agregues tests para casos que no estén en la spec — si crees que falta algo importante, sugiérelo al final, no lo generes por tu cuenta.
5. Corre `uv run pytest tests/unit/ -v` y reporta cuántos pasaron, cuántos fallaron, y cuántos tests eran nuevos.
```

**`.agents/skills/qa-integration/SKILL.md`**
```markdown
---
name: qa-integration
description: Audita el test de integración EN MEMORIA (sin subprocess) existente contra specs/*/spec.md y agrega solo lo que falta, sin improvisar el flujo a probar ni duplicar lo ya cubierto.
---
# Instrucciones
1. Lee `specs/*/spec.md`, sección "Acceptance Scenarios" — identifica los escenarios que requieren que 2+ módulos de tu propio código se conecten (ej. tu CLI llamando a tu lógica de negocio). Si no existe ningún `specs/*/spec.md`, DETENTE y pide que se corra Spec Kit primero.
2. Si existe `tests/integration/`, revisa qué flujo ya prueba antes de escribir nada. Si algún archivo ahí usa `subprocess` para lanzar el programa completo, NO es integración — es un test e2e mal clasificado. No lo toques ni lo dupliques: repórtalo, la skill `qa-e2e` se encarga de reubicarlo.
3. Si el escenario ya está cubierto por un test real en memoria, repórtalo como "ya cubierto en `<archivo>`" y no lo dupliques.
4. Si falta, agrega un test **en memoria** (llama directamente a las funciones que conectan tus módulos, sin lanzar el programa como proceso aparte) en el archivo existente o en uno nuevo dentro de `tests/integration/`.
5. Corre `uv run pytest tests/integration/ -v` y reporta el resultado.
```

**`.agents/skills/qa-e2e/SKILL.md`**
```markdown
---
name: qa-e2e
description: Audita los tests end-to-end existentes (proceso completo, vía subprocess) contra specs/*/spec.md y agrega solo lo que falta, sin improvisar el flujo ni duplicar lo ya cubierto.
---
# Instrucciones
1. Lee `specs/*/spec.md`, sección "Acceptance Scenarios" — identifica los escenarios que describen el uso real de punta a punta, como lo usaría la persona que opera el programa. Si no existe ningún `specs/*/spec.md`, DETENTE y pide que se corra Spec Kit primero.
2. Revisa `tests/e2e/` (créala si no existe). Además, revisa si `tests/integration/` tiene algún archivo que en realidad use `subprocess` para lanzar el programa completo — si lo encuentras, muévelo a `tests/e2e/` con `git mv` (no lo reescribas, solo reubícalo) y avisa que lo hiciste.
3. Para cada escenario que no esté cubierto, agrega un test e2e nuevo: invoca el programa completo como lo haría un usuario real (vía `subprocess`, verificando stdout y código de salida), nunca llamando a una función interna directamente.
4. Corre `uv run pytest tests/e2e/ -v` y reporta el resultado.
```

**`.agents/skills/qa-coverage/SKILL.md`**
```markdown
---
name: qa-coverage
description: Ejecuta y resume el reporte de cobertura de tests del proyecto, señalando líneas sin probar.
---
# Instrucciones
1. Corre `uv run pytest --cov=src --cov-report=term-missing` (ajusta `src` si tu código no vive bajo esa carpeta).
2. Resume: porcentaje total, y qué líneas "Missing" son casos borde olvidados vs. código no usado.
3. No agregues tests automáticamente — solo diagnostica.
```

**`.agents/skills/qa-security/SKILL.md`**
```markdown
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
```

**`.agents/skills/qa-report/SKILL.md`**
```markdown
---
name: qa-report
description: Ejecuta el script de reporte de calidad y genera reporte-qa.html.
---
# Instrucciones
1. Corre: `uv run python .agents/skills/qa-report/generar_reporte.py`
2. Abre `reporte-qa.html` y reporta solo el veredicto final y un resumen de una línea.
3. Si "REQUIERE CORRECCIÓN", lista los 2-3 problemas más importantes.
```

Guarda también el script `.agents/skills/qa-report/generar_reporte.py` — genera tests, cobertura y seguridad en un HTML consolidado con **Python puro**, sin gastar tokens de IA en redactarlo. El veredicto usa un umbral explícito (no lo inventa el agente): 0 tests fallando + cobertura ≥50% + sin secretos quemados en código + `.env.example`/`.gitignore` en orden = APROBADO.

```python
"""Genera reporte-qa.html combinando resultados de tests, cobertura y una
revisión de seguridad simple. Es Python puro: no usa IA para redactar el
reporte, solo para invocar esta skill."""

import json
import re
import subprocess
from pathlib import Path

UMBRAL_COBERTURA = 50.0  # % mínimo para aprobar
PATRONES_SECRETOS = [
    r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{6,}['\"]",
]


def correr_tests():
    subprocess.run(
        [
            "uv", "run", "pytest",
            "--json-report", "--json-report-file=.report.json",
            "--cov=src", "--cov-report=json:.coverage.json",
            "-q",
        ],
        capture_output=True,
    )
    reporte = json.loads(Path(".report.json").read_text()) if Path(".report.json").exists() else {}
    cobertura = json.loads(Path(".coverage.json").read_text()) if Path(".coverage.json").exists() else {}
    resumen = reporte.get("summary", {})
    total_pct = cobertura.get("totals", {}).get("percent_covered", 0.0)
    return {
        "pasaron": resumen.get("passed", 0),
        "fallaron": resumen.get("failed", 0),
        "cobertura_pct": round(total_pct, 1),
    }


def buscar_secretos():
    hallazgos = []
    for archivo in Path("src").rglob("*.py"):
        texto = archivo.read_text(errors="ignore")
        for patron in PATRONES_SECRETOS:
            for m in re.finditer(patron, texto):
                hallazgos.append(f"{archivo}: {m.group(0)}")
    return hallazgos


def revisar_higiene_secretos():
    """No confía en leer .gitignore como texto — usa git como fuente de verdad,
    porque un .gitignore puede decir cualquier cosa sin que git realmente lo respete
    (o puede perder una línea sin que se note a simple vista)."""
    tiene_env_example = Path(".env.example").exists()
    env_existe = Path(".env").exists()

    env_tracked = False
    if env_existe:
        r = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"], capture_output=True)
        env_tracked = r.returncode == 0

    if env_existe:
        r = subprocess.run(["git", "check-ignore", "-q", ".env"], capture_output=True)
        env_ignorado = r.returncode == 0
    elif Path(".gitignore").exists():
        # todavía no hay .env, pero igual conviene que la regla ya exista para cuando aparezca
        env_ignorado = ".env" in Path(".gitignore").read_text()
    else:
        env_ignorado = False

    return {
        "env_example": tiene_env_example,
        "env_existe": env_existe,
        "env_tracked": env_tracked,
        "gitignore_ok": env_ignorado,
    }


def construir_html(tests, secretos, higiene):
    # env_tracked es la peor señal: el secreto puede ya estar en el historial de git,
    # no alcanza con arreglar .gitignore a futuro.
    higiene_ok = higiene["env_example"] and higiene["gitignore_ok"] and not higiene["env_tracked"]
    aprobado = (
        tests["fallaron"] == 0
        and tests["cobertura_pct"] >= UMBRAL_COBERTURA
        and not secretos
        and higiene_ok
    )
    veredicto = "APROBADO" if aprobado else "REQUIERE CORRECCIÓN"
    color = "#1a7f37" if aprobado else "#c0341d"
    filas_secretos = "".join(f"<li>{h}</li>" for h in secretos) or "<li>Sin hallazgos</li>"

    if higiene["env_tracked"]:
        higiene_msg = "🔴 CRÍTICO: .env está trackeado por git — el secreto puede ya estar en el historial. No alcanza con arreglar .gitignore, hay que sacarlo del historial."
    elif higiene["env_existe"] and not higiene["gitignore_ok"]:
        higiene_msg = "🟡 .env existe y NO está ignorado — riesgo de que se cuele en el próximo commit."
    elif not higiene["env_example"]:
        higiene_msg = "🟡 Falta .env.example."
    else:
        higiene_msg = "✅ En orden."

    html = f"""<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>Reporte QA</title>
<style>body{{font-family:sans-serif;margin:2rem}}h1{{color:{color}}}</style></head>
<body>
<h1>{veredicto}</h1>
<h2>Tests</h2>
<p>Pasaron: {tests['pasaron']} · Fallaron: {tests['fallaron']}</p>
<h2>Cobertura</h2>
<p>{tests['cobertura_pct']}% (umbral: {UMBRAL_COBERTURA}%)</p>
<h2>Secretos expuestos</h2>
<ul>{filas_secretos}</ul>
<h2>Higiene de secretos</h2>
<p>.env.example: {"✅" if higiene["env_example"] else "❌ falta"} · .env ignorado por git: {"✅" if higiene["gitignore_ok"] else "❌"} · .env trackeado: {"🔴 SÍ" if higiene["env_tracked"] else "✅ no"}</p>
<p>{higiene_msg}</p>
</body></html>"""
    Path("reporte-qa.html").write_text(html)
    print(veredicto)


if __name__ == "__main__":
    resultados_tests = correr_tests()
    hallazgos_secretos = buscar_secretos()
    higiene_secretos = revisar_higiene_secretos()
    construir_html(resultados_tests, hallazgos_secretos, higiene_secretos)
```

**`.agents/skills/qa-orchestrate/SKILL.md`** *(esta es especial — no la usen todavía, la activan en el Bloque E)*
```markdown
---
name: qa-orchestrate
description: Ejecuta el flujo completo de calidad invocando en orden a tester-agent, security-agent y report-agent, sin pedir confirmación entre cada uno.
---
# Instrucciones
1. Verifica que exista `specs/*/spec.md`. Si falta, detente y pide que se corra Spec Kit primero.
2. Invoca al agente tester-agent (su propia tarea vive en su `agent.md`). Espera a que termine por completo.
3. Invoca al agente security-agent (su propia tarea vive en su `agent.md`). Espera a que termine por completo.
4. Invoca al agente report-agent (su propia tarea vive en su `agent.md`).
5. Presenta al usuario el veredicto final, con un resumen de 1 línea de qué hizo cada agente en el camino.

No pidas confirmación entre fase y fase — este es un flujo automático de punta a punta. Si `agy` te pide aprobar el permiso de invocación de cada agente, apruébalo y sigue.
```

> 🧑‍🏫 **Al explicar cada skill, señala el patrón repetido:** frontmatter (`name` + `description`) → sección de Instrucciones numeradas → un paso final que dice qué reportar. Una vez que ven ese patrón en la primera skill, las siguientes 6 se explican solas.

> Nota la diferencia: `qa-orchestrate` **no es un agente** — no tiene rol propio ni "personalidad". Es una receta de secuencia que la sesión principal de `agy` sigue, delegando el trabajo real a los 3 agentes especializados.

### Paso 5 — Crear los 3 agentes que USAN esas skills, con su propia tarea (7 min)

En `agy`, un agente vive en su **propia carpeta** dentro de `.agents/agents/`, con un archivo `agent.md` adentro (no un `.md` suelto):

```bash
mkdir -p .agents/agents/tester-agent .agents/agents/security-agent .agents/agents/report-agent
```

**`.agents/agents/tester-agent/agent.md`**
```markdown
---
name: tester-agent
description: Especialista en calidad funcional. Úsalo para generar o correr tests unitarios, de integración, end-to-end, y medir cobertura.
subagent: true
---
# Tester Agent

Eres el Tester-Agent. Tu única responsabilidad es la calidad funcional del código:
que existan tests en las tres capas (unitaria, integración en memoria, end-to-end), que pasen, y que la cobertura sea razonable.

Nunca improvises qué probar. Siempre exige que exista `specs/*/spec.md` antes de generar tests —
si no existe, detente y pide que se corra Spec Kit primero. No te ocupes de seguridad — eso lo hace otro agente.
No generes el reporte final — eso también es de otro agente.

Cuando te invoquen:
1. Verifica que exista `specs/*/spec.md`.
2. Usa la skill qa-unit.
3. Usa la skill qa-integration.
4. Usa la skill qa-e2e.
5. Usa la skill qa-coverage.
6. Resume tus hallazgos en 3-5 líneas, sin extenderte.

## Tarea
Verificar la calidad funcional de este proyecto.

## Criterios de aceptación
- [ ] Genera y corre tests unitarios según specs/*/spec.md
- [ ] Genera y corre el test de integración (en memoria) según specs/*/spec.md
- [ ] Genera y corre el test end-to-end (proceso completo) según specs/*/spec.md
- [ ] Reporta el % de cobertura y qué líneas quedaron sin probar

## Entregable esperado
Resumen de 3-5 líneas, sin código completo pegado en el chat.
```

**`.agents/agents/security-agent/agent.md`**
```markdown
---
name: security-agent
description: Especialista en seguridad básica. Úsalo para revisar secretos expuestos, validación de entradas y manejo de excepciones.
subagent: true
---
# Security Agent

Eres el Security-Agent. Tu única responsabilidad es encontrar riesgos de seguridad básicos.
No te importa si los tests pasan o no — eso es del Tester-Agent.

Cuando te invoquen:
1. Usa la skill qa-security.
2. Presenta la tabla de 3 filas tal como la generó la skill, sin resumirla de más.

## Tarea
Revisar riesgos de seguridad básicos en este proyecto.

## Criterios de aceptación
- [ ] Revisa secretos expuestos, validación de entradas, manejo de excepciones
- [ ] Reporta en la tabla de exactamente 3 filas

## Entregable esperado
La tabla, sin agregar hallazgos fuera de esas 3 categorías.
```

**`.agents/agents/report-agent/agent.md`**
```markdown
---
name: report-agent
description: Consolida resultados de calidad en un reporte final. Úsalo al final del proceso, después del Tester y Security.
subagent: true
---
# Report Agent

Eres el Report-Agent. Solo consolidas — no vuelves a analizar nada por tu cuenta,
confías en lo que ya hicieron el Tester-Agent y el Security-Agent.

Cuando te invoquen:
1. Usa la skill qa-report.
2. Presenta el veredicto final de forma clara y breve.

## Tarea
Generar el veredicto final de calidad.

## Criterios de aceptación
- [ ] Ejecuta el script de reporte (no redacta el reporte con IA)
- [ ] Presenta el veredicto y, si aplica, los 2-3 problemas más importantes

## Entregable esperado
Veredicto + resumen de una línea, no el HTML completo pegado en el chat.
```

> 🧑‍🏫 **Por qué la orden de trabajo vive dentro del `agent.md`, no en un archivo aparte:** cierra el mismo círculo anti-vibe-coding de siempre (tarea + criterios de aceptación + entregable esperado), pero sin un archivo `ordenes-agentes.md` extra que mantener sincronizado con 3 agentes. Cada agente ya trae su propio rol, sus reglas y ahora también su tarea — invocarlo es autocontenido: no hay una orden "afuera" que se pueda desalinear de a quién describe.

---

## BLOQUE A — Invocar al `tester-agent` (12 min)

```
> Usa el agente tester-agent para verificar la calidad funcional de este proyecto.
```

**Observa mientras corre:** ¿el agente se comportó distinto a cuando invocaban skills sueltas? ¿Explicó su rol antes de actuar? ¿Te pidió aprobar algún permiso antes de empezar?

**Checkpoint:** cada escenario/caso borde/FR relevante de `specs/*/spec.md` tiene un test real en `tests/unit/`, `tests/integration/` o `tests/e2e/` según corresponda (nuevo o marcado como "ya cubierto" en uno de ayer) — no hay tests "de más" que ustedes no pidieron, y no hay casos duplicados entre archivos. Si tenías un `tests/integration/test_cli.py` de ayer basado en `subprocess`, ahora vive en `tests/e2e/`. Tienes un resumen de cobertura.

> 🧑‍🏫 **Si `agy` te muestra un prompt de permiso al invocar el agente:** es esperado — invocar un agente por lenguaje natural dispara una acción real que `agy` gatea con su sistema de permisos, igual que con `run_command`. Apruébalo (o "permitir siempre" para no repetirlo el resto de la clase) y sigue. Si en cambio el agente simplemente no reacciona como tal (responde en primera persona sin seguir su prompt), como plan B invoca las 4 skills directamente (`/qa-unit`, `/qa-integration`, `/qa-e2e`, `/qa-coverage`) y explica verbalmente el concepto de agente/rol.

---

## 🔄 DESCANSO (5 min)

---

## BLOQUE B — Provocar un fallo y ver el hook actuar (15 min)

### Paso 1 — Instalar el hook de bloqueo (5 min)

Crea `.agents/hooks/gate-tests.sh`:
```bash
#!/bin/bash
# agy ejecuta este script con cwd = .agents/ (la carpeta que contiene hooks.json),
# no la raíz del proyecto — por eso subimos un nivel antes de correr pytest.
cd ..
if uv run pytest --tb=no -q > /tmp/gate-tests-agy.log 2>&1; then
  echo '{}'
else
  echo '{"decision":"continue","reason":"Hay tests fallando. No te detengas -- corrige el código antes de terminar."}'
fi
```
```bash
chmod +x .agents/hooks/gate-tests.sh
```

Y `.agents/hooks.json` (**en `.agents/` directamente, no en una subcarpeta `hooks/`**):
```json
{
  "gate-tests": {
    "Stop": [
      { "type": "command", "command": "./hooks/gate-tests.sh", "timeout": 30 }
    ]
  }
}
```

> 🧑‍🏫 **Por qué `Stop` y no `PreToolUse` ni `PostToolUse`:** `PostToolUse` no sirve — su contrato de salida es `{}`, no puede bloquear nada. `PreToolUse` sí puede bloquear, pero bloquear la **escritura** mientras los tests fallan crea un candado sin salida: el chequeo corre *antes* de cada escritura y mira el estado *actual* en disco (todavía roto) — así que también bloquearía la escritura que sea la corrección misma, sin importar que esa escritura arregle el problema. El agente quedaría pidiendo permiso para escribir el fix, y cada intento se negaría porque el código, antes de esa escritura, sigue roto. `Stop` evita ese candado: no bloquea ninguna escritura — el agente puede editar todas las veces que necesite — solo le impide **terminar su turno** mientras los tests sigan en rojo. Su contrato de salida (`{"decision":"continue","reason":"..."}`) fuerza al agente a seguir intentando; `{}` (o cualquier otra cosa) lo deja terminar normalmente. Fíjate también en la forma del JSON: a diferencia de `PreToolUse`/`PostToolUse`, `Stop` no usa `matcher` ni el wrapper `hooks` — es una lista plana de comandos.

### Paso 2 — Provocar el fallo (4 min)

```
> Modifica [una función de tu proyecto] para que tenga un bug sutil, sin decirme cuál es.
```

### Paso 3 — Observar el bloqueo y corregir (6 min)

```
> Este test está fallando: [pega el nombre del test y el mensaje de error completo]
> Corrige el código para que pase.
```

> 🧑‍🏫 **Si el hook no fuerza a seguir corrigiendo:** revisa primero que `.agents/hooks.json` esté bien ubicado (no dentro de `.agents/hooks/`) y que el JSON sea válido (`python3 -c "import json; json.load(open('.agents/hooks.json'))"`). Si sigue sin funcionar, sigue el bloque manualmente (`uv run pytest -v`, identifica, corrige) y retómalo como ejercicio de investigación fuera de clase.

---

## BLOQUE C — Invocar al `security-agent` (10 min)

```
> Usa el agente security-agent para revisar riesgos de seguridad básicos en este proyecto.
```

Para cada fila con hallazgo real, corrige:
```
> Corrige [hallazgo específico].
```

**Nota honesta de arquitectura:** el prompt de `security-agent` dice explícitamente que no se ocupa de tests, y en la práctica no debería tocarlos. Pero eso es disciplina declarada en texto, no una restricción técnica — `agy` no tiene una allowlist de skills por agente (no existe el campo `tools:` de otros frameworks). Si le pidieras directamente al `security-agent` que edite un test, probablemente lo haría. El "mínimo privilegio" real de la Agencia de Agentes se logra con otras herramientas (por ejemplo, `commandExecutionPolicy` en el frontmatter del agente, que si quieres puedes explorar por tu cuenta), no con lo que armamos hoy.

---

## BLOQUE D — Invocar al `report-agent` (8 min)

```
> Usa el agente report-agent para generar el veredicto final de calidad.
```

Abre `reporte-qa.html` y revisa el veredicto.

---

## BLOQUE E — Automatizar todo: `/qa-orchestrate` (12 min)

### Qué vas a hacer y por qué

Ya invocaste a los 3 agentes a mano, uno por uno, y viste cómo se conectan por archivos. Ahora vas a activar la skill orquestadora para que ese mismo trabajo ocurra con **un solo comando**, sin que tú decidas el orden cada vez.

### Paso 1 — Provocar un problema nuevo (3 min)

Para que la corrida de hoy no muestre "todo ya está bien" (poco interesante), rompe algo de nuevo:
```
> Modifica [otra función] para que tenga un bug distinto al de antes.
```

### Paso 2 — Correr todo con un solo comando (7 min)

```
/qa-orchestrate
```

Observa: el `tester-agent` corre, encuentra el fallo (o el hook lo bloquea), el `security-agent` corre después, y al final el `report-agent` te da el veredicto — todo sin que tú tengas que invocar cada uno por separado. Si `agy` te pide aprobar el permiso de cada invocación de agente, apruébalo y deja que continúe.

### Paso 3 — Comparar la experiencia (2 min)

Responde:
- ¿Qué se sintió distinto entre invocar cada agente a mano (Bloques A, C, D) y usar `/qa-orchestrate`?
- ¿Perdiste algo de control, o solo perdiste pasos repetitivos?

> 🧑‍🏫 **Si el `tester-agent` no se da por terminado y sigue intentando corregir:** es el comportamiento correcto — el hook (`Stop`) no lo deja concluir su turno mientras los tests sigan en rojo, así que insiste hasta lograrlo. Es una buena oportunidad para señalar que "automático" no significa "sin control".

---

## Cómo se conectan los 3 agentes (léelo antes de la reflexión)

No hay comunicación directa entre agentes — cada uno deja su resultado en un **archivo**, y el siguiente lo lee de ahí (o simplemente vuelve a generarlo). Así de simple:

```
tester-agent    → escribe → tests/unit/, tests/integration/, tests/e2e/ (audita y extiende, no duplica), resultado de cobertura
security-agent  → escribe → hallazgos-seguridad.md, .env.example, .gitignore (higiene de secretos)
report-agent    → LEE      → corre pytest + cobertura + busca hallazgos de nuevo
                → escribe → reporte-qa.html (veredicto final)
```

**Sé honesto contigo mismo sobre el orden:** de los tres agentes, solo el `tester-agent` tiene un efecto de orden real — es el único que *crea* algo que no existía (los tests). El `report-agent` no necesita que le "pasen" nada explícitamente: su skill (`qa-report`) vuelve a correr todo por su cuenta (tests, cobertura, seguridad) y arma el HTML desde cero. Por eso invocarlo antes de que el `tester-agent` haya generado tests no da un error — da un reporte con 0 tests, que es simplemente cierto en ese momento. El orden Tester → Security → Report que seguimos hoy es una secuencia pedagógica razonable, no una dependencia técnica estricta entre Security y Report.

## Reflexión sobre la orquestación (5 min)

Responde:
1. ¿En qué se sintió distinto invocar "agentes" comparado con invocar "skills" sueltas?
2. ¿Qué pasó la primera vez que `agy` te pidió aprobar la invocación de un agente? ¿Qué rol cumple ese prompt de permiso en la cadena de control — sigue siendo automático de punta a punta, o hay un humano en el medio?
3. Tú fuiste el orquestador hoy — invocando a cada agente en el momento correcto. ¿Cómo sería si otro agente (no ustedes) decidiera ese orden?

> Esa última pregunta es exactamente el paso que sigue: un orquestador automático, no ustedes a mano. Es la Agencia de Agentes.

---

## CIERRE (5 min)

Responde en voz alta, sin crear un archivo nuevo — el veredicto ya vive en `reporte-qa.html` y los hallazgos en `hallazgos-seguridad.md`:
1. ¿Cuál fue el veredicto final?
2. Completa: *"El inspector encontró ______ que el cocinero no había visto."*

**Guarda todo tu trabajo**, incluidas las skills, los agentes y el hook — son la base directa del proyecto que viene.

---

## Entregable de la sesión

```
mi-proyecto-speckit/
├── [código corregido hoy]
├── specs/*/spec.md (ya existía — es la fuente de verdad, no se crea un test-spec.md aparte)
├── hallazgos-seguridad.md
├── .agents/
│   ├── skills/qa-unit, qa-integration, qa-e2e, qa-coverage, qa-security, qa-report, qa-orchestrate/
│   ├── agents/tester-agent/agent.md, security-agent/agent.md, report-agent/agent.md (cada uno con su propia tarea y criterios)
│   ├── hooks/gate-tests.sh
│   └── hooks.json
├── tests/unit/, tests/integration/, tests/e2e/ (extendidos hoy, no reescritos)
├── reporte-qa.html
├── .env.example
└── .gitignore (ignora .env)
```

`.env.example` y la línea `.env` en `.gitignore` los crea la skill `qa-security` — este proyecto no tiene secretos reales todavía, pero la higiene de "nunca quemar secretos en código" se establece igual, antes de que haga falta.

- Repositorio con todo lo anterior.
- **Informe de Entrega en PDF** (plantilla del AVAC, Contenido → Inicio) con: captura del hook bloqueando, captura de `reporte-qa.html`, breve explicación de la arquitectura skills→agentes, y enlace al repositorio.
