#!/bin/bash
set -euo pipefail

echo "=== Verificando Python ==="
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python no está instalado."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python encontrado: $($PYTHON_CMD --version)"

echo "=== Configurando Backend (api) ==="
if [ ! -d "api/.venv" ]; then
    echo "Creando entorno virtual para api..."
    $PYTHON_CMD -m venv api/.venv
else
    echo "Entorno virtual de api ya existe."
fi

echo "Instalando dependencias de backend..."
source api/.venv/bin/activate
pip install -r api/requirements.txt
deactivate

echo "=== Configurando Frontend (frontend) ==="
if [ ! -d "frontend/.venv" ]; then
    echo "Creando entorno virtual para frontend..."
    $PYTHON_CMD -m venv frontend/.venv
else
    echo "Entorno virtual de frontend ya existe."
fi

echo "Instalando dependencias de frontend..."
source frontend/.venv/bin/activate
pip install -r frontend/requirements.txt
deactivate

echo "=== Setup completado con éxito ==="
echo "Para ejecutar la aplicación, usa:"
echo "./run.sh"
