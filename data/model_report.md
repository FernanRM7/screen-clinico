# Reporte de Modelado y Evaluación

## Dataset
- **Total Registros:** 768
- **Train Size:** 614
- **Test Size:** 154

## Distribución de Clases
- **Completo:** 0: 65.1%, 1: 34.9%
- **Train:** 0: 65.1%, 1: 34.9%
- **Aplicación de SMOTE:** Se detectó un desbalance (Clase mayoritaria: 65.1%). Se aplicó SMOTE al conjunto de entrenamiento.

## Comparación de Modelos
| Model              |   Accuracy |   Precision |   Recall |       F1 |   ROC-AUC |   PR-AUC |
|:-------------------|-----------:|------------:|---------:|---------:|----------:|---------:|
| RandomForest       |   0.74026  |    0.612903 | 0.703704 | 0.655172 |  0.813796 | 0.692997 |
| XGBoost            |   0.733766 |    0.606557 | 0.685185 | 0.643478 |  0.815741 | 0.680905 |
| LogisticRegression |   0.707792 |    0.57377  | 0.648148 | 0.608696 |  0.808333 | 0.668264 |

## Modelo Ganador
**RandomForest**
*Justificación Clínica:* En el contexto clínico, un falso negativo (paciente enfermo no detectado) es mucho más riesgoso que un falso positivo. Por ello, hemos priorizado maximizar el **Recall**, utilizando secundariamente ROC-AUC y F1-Score como criterios de desempate.

## Calibración
El modelo ganador fue calibrado usando Isotonic Regression.
- Brier Score Original: 0.1696
- Brier Score Calibrado: 0.1765

## SHAP y Explicabilidad
Se ha serializado el explainer SHAP (`shap_explainer.pkl`). Las variables más influyentes a nivel global fueron extraídas utilizando validación cruzada. Revisa los gráficos en `data/plots/metrics/` para el detalle.

## Incertidumbre
Se incluye una utilidad de Bootstrap (`bootstrap_confidence_interval` en `utils.py`) que permite evaluar la incertidumbre local para cada predicción de la API.

## Conclusiones
El modelo calibrado `model_calibrated.pkl` y su `StandardScaler` (`scaler.pkl`) se encuentran listos para ser expuestos vía API Flask. Ambos han sido construidos respetando estrictamente la pureza estadística sin data leakage.
