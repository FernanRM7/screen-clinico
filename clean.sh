#!/bin/bash
set -euo pipefail

REMOVE_VENV=false

if [ "${1:-}" == "--venv" ]; then
    REMOVE_VENV=true
fi

echo "=== Limpiando archivos caché de Python ==="
# Evitamos fallos si no se encuentran archivos
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true
echo "Archivos caché eliminados."

if [ "$REMOVE_VENV" == "true" ]; then
    echo "=== Eliminando entornos virtuales ==="
    rm -rf api/.venv
    rm -rf frontend/.venv
    rm -rf .venv
    echo "Entornos virtuales eliminados."
fi

echo "=== Limpieza completada ==="
