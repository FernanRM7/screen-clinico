#!/bin/bash
set -euo pipefail

FLASK_PID=""

cleanup() {
    echo ""
    echo "=== Deteniendo servicios ==="
    if [ -n "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null || true
    fi
    echo "Servicios detenidos."
    exit 0
}

# Manejar Ctrl+C u otras señales
trap cleanup SIGINT SIGTERM

echo "=== Iniciando API Flask ==="
source api/.venv/bin/activate
python api/test.py &
FLASK_PID=$!
deactivate

echo "Esperando a que la API inicie..."
sleep 3

echo "=== Iniciando Streamlit ==="
source frontend/.venv/bin/activate
streamlit run frontend/app.py

cleanup
