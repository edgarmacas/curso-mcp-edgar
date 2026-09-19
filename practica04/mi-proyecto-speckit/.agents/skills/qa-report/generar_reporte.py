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
