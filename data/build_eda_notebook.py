import nbformat as nbf
import json

nb = nbf.v4.new_notebook()

text_1 = """# Análisis Exploratorio de Datos (EDA)
Este notebook realiza el análisis exploratorio, limpieza y preprocesamiento de características para la predicción de diabetes."""

code_1 = """# 1. Carga de librerías
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import joblib
from sklearn.preprocessing import StandardScaler"""

text_2 = """# 2. Carga del dataset"""

code_2 = """# Definir rutas
DATA_PATH = Path('diabetes-dataset.csv')
PLOTS_DIR = Path('plots')
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
SCALER_PATH = Path('../api/scaler.pkl')
SCALER_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH = Path('eda_report.md')

# Cargar dataset
df = pd.read_csv(DATA_PATH)
print(f"Dimensiones del dataset: {df.shape}")
display(df.head())
print("Nombres de columnas:", df.columns.tolist())"""

text_3 = """# 3. Inspección inicial"""

code_3 = """df.info()
print("\\nDescripción estadística:")
display(df.describe())
print("\\nValores nulos por columna:")
print(df.isnull().sum())
print("\\nCantidad de duplicados:", df.duplicated().sum())
print("\\nTipos de datos:")
print(df.dtypes)"""

text_4 = """# 4. Detección de ceros inválidos
Biológicamente, variables como `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin` y `BMI` no pueden tener valor 0. Representan valores faltantes."""

code_4 = """cols_invalid_zeros = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
total_records = len(df)

zero_stats = []
for col in cols_invalid_zeros:
    zero_count = (df[col] == 0).sum()
    zero_stats.append({
        'Variable': col,
        'Total Registros': total_records,
        'Cantidad Ceros': zero_count,
        'Porcentaje (%)': round((zero_count / total_records) * 100, 2)
    })

df_zeros = pd.DataFrame(zero_stats)
display(df_zeros)"""

text_5 = """# Limpieza y Preprocesamiento
1. Reemplazar ceros por NaN
2. Imputar con la mediana
3. Separar X, y
4. Aplicar StandardScaler
5. Guardar scaler"""

code_5 = """# 1. Reemplazar ceros por NaN
df[cols_invalid_zeros] = df[cols_invalid_zeros].replace(0, np.nan)

# 2. NaN generados
print("NaN generados por columna:\\n", df[cols_invalid_zeros].isnull().sum())

# 3. Imputar con mediana
for col in cols_invalid_zeros:
    median_val = df[col].median()
    df[col] = df[col].fillna(median_val)

# 4. Validar sin NaN
assert df.isnull().sum().sum() == 0, "Aún hay NaN en el dataset!"
print("\\nNo quedan NaN tras la imputación.")

# 5. Separar features
X = df.drop('Outcome', axis=1)
y = df['Outcome']

# 6. Escalar
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)

# 7. Guardar scaler
joblib.dump(scaler, SCALER_PATH)
print(f"\\nScaler guardado exitosamente en: {SCALER_PATH.resolve()}")

# 8. Verificación
assert SCALER_PATH.exists(), "No se pudo guardar el scaler" """

text_6 = """# Visualizaciones EDA"""

code_6 = """# 1. Heatmap de correlaciones
plt.figure(figsize=(10, 8))
corr = df.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlaciones')
plt.savefig(PLOTS_DIR / 'correlation_heatmap.png', bbox_inches='tight')
plt.show()

# 2. Histogramas por clase
df.groupby('Outcome').hist(figsize=(12, 10), alpha=0.5, bins=20)
plt.suptitle('Histogramas por clase')
plt.savefig(PLOTS_DIR / 'class_histograms.png', bbox_inches='tight')
plt.show()

# 3. Boxplots por feature
plt.figure(figsize=(12, 6))
sns.boxplot(data=X_scaled_df)
plt.xticks(rotation=45)
plt.title('Boxplots por feature (Escalados)')
plt.savefig(PLOTS_DIR / 'boxplots.png', bbox_inches='tight')
plt.show()

# 4. Distribución de clases
plt.figure(figsize=(6,4))
ax = sns.countplot(data=df, x='Outcome')
plt.title('Balance de Clases')
for p in ax.patches:
    ax.annotate(f'{p.get_height()} ({(p.get_height()/len(df))*100:.1f}%)', (p.get_x() + 0.3, p.get_height() + 5))
plt.savefig(PLOTS_DIR / 'class_balance.png', bbox_inches='tight')
plt.show()"""

text_7 = """# Reporte Académico"""

code_7 = """md_content = f\"\"\"# Reporte Académico de EDA

## Introducción
El dataset contiene {total_records} registros clínicos para predecir la aparición de diabetes (Outcome). 

## Calidad de datos
Se identificaron ceros inválidos que representaban datos faltantes:
{df_zeros.to_markdown(index=False)}

## Limpieza realizada
- Reemplazo de ceros biológicamente imposibles por `NaN`.
- Imputación mediante la mediana de la columna correspondiente para evitar el impacto de outliers.
- Estandarización de todas las características predictivas usando `StandardScaler`. El scaler fue guardado para producción en `api/scaler.pkl`.

## Correlaciones
Las variables más positivamente correlacionadas con Outcome son:
- Glucose: {corr['Outcome']['Glucose']:.2f}
- BMI: {corr['Outcome']['BMI']:.2f}

## Balance de clases
- Cantidad de Outcome=0: {len(df[df['Outcome']==0])} ({(len(df[df['Outcome']==0])/total_records)*100:.1f}%)
- Cantidad de Outcome=1: {len(df[df['Outcome']==1])} ({(len(df[df['Outcome']==1])/total_records)*100:.1f}%)
Existe un moderado desbalance de clases (cerca de 2:1), lo cual es común en dominios médicos pero debe tenerse en cuenta para las métricas del modelo (ej. preferir F1-Score sobre Accuracy).

## Hallazgos principales
1. **Datos faltantes ocultos:** Una gran proporción de registros en variables como SkinThickness ({df_zeros.loc[df_zeros['Variable']=='SkinThickness', 'Porcentaje (%)'].values[0]}%) e Insulin ({df_zeros.loc[df_zeros['Variable']=='Insulin', 'Porcentaje (%)'].values[0]}%) estaban en cero.
2. **Alta correlación Glucose-Outcome:** La glucosa es la variable individual más discriminatoria.
3. **Distribución asimétrica:** Múltiples variables presentaban colas pesadas antes del preprocesamiento.
4. **Relación Edad y Glucosa:** Existen patrones visibles donde pacientes con altos valores de glucosa tienden a pertenecer a Outcome=1.
5. **Outliers persistentes:** Los boxplots evidencian la existencia de algunos valores atípicos que el StandardScaler no elimina.

## Conclusiones
La limpieza profunda ha resultado en un set de datos libre de valores fisiológicamente imposibles. Las variables están escaladas y listas para alimentar algoritmos como SVM, Regresión Logística o Redes Neuronales. El scaler está preservado para su consumo en la API.\"\"\"

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(md_content)
    
print(f"Reporte generado en: {REPORT_PATH.resolve()}")"""

nb.cells = [
    nbf.v4.new_markdown_cell(text_1),
    nbf.v4.new_code_cell(code_1),
    nbf.v4.new_markdown_cell(text_2),
    nbf.v4.new_code_cell(code_2),
    nbf.v4.new_markdown_cell(text_3),
    nbf.v4.new_code_cell(code_3),
    nbf.v4.new_markdown_cell(text_4),
    nbf.v4.new_code_cell(code_4),
    nbf.v4.new_markdown_cell(text_5),
    nbf.v4.new_code_cell(code_5),
    nbf.v4.new_markdown_cell(text_6),
    nbf.v4.new_code_cell(code_6),
    nbf.v4.new_markdown_cell(text_7),
    nbf.v4.new_code_cell(code_7),
]

with open('data/eda.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook data/eda.ipynb generado exitosamente.")
