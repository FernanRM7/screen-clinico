#!/bin/bash

cleanup() {
    echo ""
    echo "Deteniendo servicios..."
    kill $FLASK_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "=== Iniciando API Flask ==="
source api/.venv/bin/activate
python api/test.py &
FLASK_PID=$!
sleep 2

echo "=== Iniciando Streamlit ==="
streamlit run frontend/app.py

cleanup
