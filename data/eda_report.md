# Reporte Académico de EDA

## Introducción
El dataset contiene 768 registros clínicos para predecir la aparición de diabetes (Outcome). 

## Calidad de datos
Se identificaron ceros inválidos que representaban datos faltantes:
| Variable      |   Total Registros |   Cantidad Ceros |   Porcentaje (%) |
|:--------------|------------------:|-----------------:|-----------------:|
| Glucose       |               768 |                5 |             0.65 |
| BloodPressure |               768 |               35 |             4.56 |
| SkinThickness |               768 |              227 |            29.56 |
| Insulin       |               768 |              374 |            48.7  |
| BMI           |               768 |               11 |             1.43 |

## Limpieza realizada
- Reemplazo de ceros biológicamente imposibles por `NaN`.
- Imputación mediante la mediana de la columna correspondiente para evitar el impacto de outliers.
- Estandarización de todas las características predictivas usando `StandardScaler`. El scaler fue guardado para producción en `api/scaler.pkl`.

## Correlaciones
Las variables más positivamente correlacionadas con Outcome son:
- Glucose: 0.49
- BMI: 0.31

## Balance de clases
- Cantidad de Outcome=0: 500 (65.1%)
- Cantidad de Outcome=1: 268 (34.9%)
Existe un moderado desbalance de clases (cerca de 2:1), lo cual es común en dominios médicos pero debe tenerse en cuenta para las métricas del modelo (ej. preferir F1-Score sobre Accuracy).

## Hallazgos principales
1. **Datos faltantes ocultos:** Una gran proporción de registros en variables como SkinThickness (29.56%) e Insulin (48.7%) estaban en cero.
2. **Alta correlación Glucose-Outcome:** La glucosa es la variable individual más discriminatoria.
3. **Distribución asimétrica:** Múltiples variables presentaban colas pesadas antes del preprocesamiento.
4. **Relación Edad y Glucosa:** Existen patrones visibles donde pacientes con altos valores de glucosa tienden a pertenecer a Outcome=1.
5. **Outliers persistentes:** Los boxplots evidencian la existencia de algunos valores atípicos que el StandardScaler no elimina.

## Conclusiones
La limpieza profunda ha resultado en un set de datos libre de valores fisiológicamente imposibles. Las variables están escaladas y listas para alimentar algoritmos como SVM, Regresión Logística o Redes Neuronales. El scaler está preservado para su consumo en la API.