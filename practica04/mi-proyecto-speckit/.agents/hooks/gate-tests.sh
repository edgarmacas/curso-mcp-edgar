#!/bin/bash
# agy ejecuta este script con cwd = .agents/ (la carpeta que contiene hooks.json),
# no la raíz del proyecto — por eso subimos un nivel antes de correr pytest.
cd ..
if uv run pytest --tb=no -q > /tmp/gate-tests-agy.log 2>&1; then
  echo '{}'
else
  echo '{"decision":"continue","reason":"Hay tests fallando. No te detengas -- corrige el código antes de terminar."}'
fi
