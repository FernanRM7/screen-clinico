# Screen Clínico

Aplicación con backend en Flask y frontend en Streamlit.

### Instalación

Para preparar el entorno de desarrollo automáticamente (requiere Python instalado):

```bash
chmod +x setup.sh
./setup.sh
```

### Ejecución

Para levantar ambos servicios a la vez:

```bash
chmod +x run.sh
./run.sh
```

Esto inicia:
- **Flask API** (Backend)
- **Streamlit** (Frontend)

### Limpieza

Para eliminar archivos temporales y de caché generados por Python:

```bash
./clean.sh
```

Si deseas también eliminar los entornos virtuales de backend y frontend:

```bash
./clean.sh --venv
```

### Estructura del proyecto

```
.
├── api/                  # Backend Flask
│   ├── .venv/            # (Generado automáticamente)
│   ├── requirements.txt
│   └── test.py
├── frontend/             # Frontend Streamlit
│   ├── .venv/            # (Generado automáticamente)
│   ├── requirements.txt
│   └── app.py
├── data/                 # Datasets
├── model/                # Modelos entrenados
├── notebook/             # Notebooks de análisis
├── clean.sh              # Script de limpieza
├── run.sh                # Script de ejecución
└── setup.sh              # Script de instalación
```
