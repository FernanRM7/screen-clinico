# Screen Clínico

Proyecto de predicción de diabetes con Flask API + Streamlit frontend.

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

El script `run.sh` levanta ambos servidores:

```bash
chmod +x run.sh
./run.sh
```

Esto inicia:
- **Flask API** en `http://127.0.0.1:5001`
- **Streamlit** en `http://localhost:8501`

También se pueden ejecutar por separado:

```bash
# Terminal 1 - API
cd api && source .venv/bin/activate && python test.py

# Terminal 2 - Frontend
streamlit run frontend/app.py
```

## Estructura

```
.
├── api/            # Flask API
│   ├── test.py
│   └── requirements.txt
├── frontend/       # Streamlit app
│   ├── app.py
│   └── requirements.txt
├── data/           # Datasets
├── model/          # Modelos entrenados
├── notebook/       # Notebooks de análisis
├── requirements.txt
└── run.sh
```
