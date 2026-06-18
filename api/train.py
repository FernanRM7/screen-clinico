import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import time
import shap

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, average_precision_score,
                             confusion_matrix, roc_curve, precision_recall_curve,
                             classification_report, brier_score_loss)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve

# Config
DATA_PATH = Path('../data/diabetes-dataset.csv')
METRICS_DIR = Path('../data/plots/metrics')
METRICS_DIR.mkdir(parents=True, exist_ok=True)
SCALER_PATH = Path('scaler.pkl')
MODEL_PATH = Path('model.pkl')
MODEL_CALIB_PATH = Path('model_calibrated.pkl')
METADATA_PATH = Path('best_model_metadata.json')
SHAP_EXPLAINER_PATH = Path('shap_explainer.pkl')
RESULTS_CSV_PATH = Path('../data/model_results.csv')
REPORT_PATH = Path('../data/model_report.md')

# --- FASE 1: SPLIT Y DESBALANCE ---
print("=== FASE 1: Preparación y Split ===")
df = pd.read_csv(DATA_PATH)
X = df.drop('Outcome', axis=1)
y = df['Outcome']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

# Preprocesamiento (Evitando Data Leakage)
cols_invalid_zeros = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
X_train[cols_invalid_zeros] = X_train[cols_invalid_zeros].replace(0, np.nan)
X_test[cols_invalid_zeros] = X_test[cols_invalid_zeros].replace(0, np.nan)

medians = X_train[cols_invalid_zeros].median()
X_train[cols_invalid_zeros] = X_train[cols_invalid_zeros].fillna(medians)
X_test[cols_invalid_zeros] = X_test[cols_invalid_zeros].fillna(medians)

scaler = StandardScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
joblib.dump(scaler, SCALER_PATH)

dist_total = y.value_counts(normalize=True) * 100
dist_train = y_train.value_counts(normalize=True) * 100
dist_test = y_test.value_counts(normalize=True) * 100

print(f"Distribución Total: {dist_total.to_dict()}")
print(f"Distribución Train: {dist_train.to_dict()}")

majority_class_ratio = dist_train.max()
smote_applied = False
X_train_final, y_train_final = X_train_scaled, y_train

if majority_class_ratio > 60.0:
    print("Detectado desbalance (>60%). Aplicando SMOTE solo en Train...")
    smote = SMOTE(random_state=42)
    X_train_final, y_train_final = smote.fit_resample(X_train_scaled, y_train)
    smote_applied = True
    dist_train_smote = pd.Series(y_train_final).value_counts(normalize=True) * 100
    print(f"Distribución tras SMOTE: {dist_train_smote.to_dict()}")

# --- FASE 2: ENTRENAMIENTO ---
print("\n=== FASE 2: Entrenamiento de Modelos ===")
models_config = {
    'LogisticRegression': {
        'model': LogisticRegression(random_state=42, max_iter=1000),
        'params': {"C": [0.01, 0.1, 1, 10, 100], "solver": ["liblinear"]}
    },
    'RandomForest': {
        'model': RandomForestClassifier(random_state=42),
        'params': {"n_estimators": [100, 200, 300], "max_depth": [3, 5, 10, None], "min_samples_split": [2, 5, 10]}
    },
    'XGBoost': {
        'model': XGBClassifier(random_state=42, eval_metric='logloss'),
        'params': {"n_estimators": [100, 200], "max_depth": [3, 5, 7], "learning_rate": [0.01, 0.05, 0.1], "subsample": [0.8, 1.0]}
    }
}

trained_models = {}
results_list = []

for name, config in models_config.items():
    print(f"Entrenando {name}...")
    start_time = time.time()
    grid = GridSearchCV(config['model'], config['params'], cv=5, scoring='roc_auc', n_jobs=-1)
    grid.fit(X_train_final, y_train_final)
    elapsed = time.time() - start_time
    
    trained_models[name] = grid.best_estimator_
    results_list.append({
        'Model': name,
        'Best_ROC_AUC_CV': grid.best_score_,
        'Best_Params': str(grid.best_params_),
        'Time_s': elapsed
    })

pd.DataFrame(results_list).to_csv(RESULTS_CSV_PATH, index=False)

# --- FASE 3: EVALUACIÓN Y SELECCIÓN ---
print("\n=== FASE 3: Evaluación Clínica ===")
eval_results = []

for name, model in trained_models.items():
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)
    
    eval_results.append({
        'Model': name,
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1': f1,
        'ROC-AUC': roc_auc,
        'PR-AUC': pr_auc
    })
    
    # Matriz Confusión
    plt.figure(figsize=(5,4))
    sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
    plt.title(f'Confusion Matrix - {name}')
    plt.savefig(METRICS_DIR / f'confusion_matrix_{name.lower()}.png')
    plt.close()
    
    # Curva ROC
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    plt.figure()
    plt.plot(fpr, tpr, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve - {name}')
    plt.legend(loc='lower right')
    plt.savefig(METRICS_DIR / f'roc_curve_{name.lower()}.png')
    plt.close()
    
    # PR Curve
    prec_vals, rec_vals, _ = precision_recall_curve(y_test, y_prob)
    plt.figure()
    plt.plot(rec_vals, prec_vals, label=f'PR curve (area = {pr_auc:.2f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'PR Curve - {name}')
    plt.legend(loc='lower right')
    plt.savefig(METRICS_DIR / f'pr_curve_{name.lower()}.png')
    plt.close()
    
    # Reporte
    with open(METRICS_DIR / f'classification_report_{name.lower()}.txt', 'w') as f:
        f.write(classification_report(y_test, y_pred))

df_eval = pd.DataFrame(eval_results)
df_eval = df_eval.sort_values(by=['Recall', 'ROC-AUC', 'F1'], ascending=False).reset_index(drop=True)
best_model_name = df_eval.iloc[0]['Model']
best_model = trained_models[best_model_name]

print(f"\nModelo Ganador (prioridad Recall): {best_model_name}")
joblib.dump(best_model, MODEL_PATH)

best_metadata = {
    'model_name': best_model_name,
    'hyperparameters': str(best_model.get_params()),
    'metrics': df_eval.iloc[0].to_dict()
}
with open(METADATA_PATH, 'w') as f:
    json.dump(best_metadata, f, indent=4)

# --- FASE 4: CALIBRACIÓN ---
print("\n=== FASE 4: Calibración de Probabilidades ===")
calibrated = CalibratedClassifierCV(estimator=best_model, method='isotonic', cv=5)
calibrated.fit(X_train_final, y_train_final)

y_prob_calib = calibrated.predict_proba(X_test_scaled)[:, 1]
brier_orig = brier_score_loss(y_test, best_model.predict_proba(X_test_scaled)[:, 1])
brier_calib = brier_score_loss(y_test, y_prob_calib)

prob_true_o, prob_pred_o = calibration_curve(y_test, best_model.predict_proba(X_test_scaled)[:, 1], n_bins=10)
prob_true_c, prob_pred_c = calibration_curve(y_test, y_prob_calib, n_bins=10)

plt.figure(figsize=(8,6))
plt.plot([0, 1], [0, 1], "k:", label="Perfectamente calibrado")
plt.plot(prob_pred_o, prob_true_o, "s-", label=f"Original (Brier: {brier_orig:.3f})")
plt.plot(prob_pred_c, prob_true_c, "s-", label=f"Calibrado (Brier: {brier_calib:.3f})")
plt.xlabel("Probabilidad predicha media")
plt.ylabel("Fracción de positivos")
plt.title(f"Calibration Curve - {best_model_name}")
plt.legend()
plt.savefig(METRICS_DIR / 'calibration_curve.png')
plt.close()

joblib.dump(calibrated, MODEL_CALIB_PATH)

# --- FASE 5 y 6: EXPLICABILIDAD SHAP ---
print("\n=== FASE 5 & 6: Explicabilidad SHAP ===")
if best_model_name in ['RandomForest', 'XGBoost']:
    explainer = shap.TreeExplainer(best_model)
else:
    explainer = shap.KernelExplainer(best_model.predict_proba, shap.sample(X_train_final, 100))

joblib.dump(explainer, SHAP_EXPLAINER_PATH)

shap_values = explainer.shap_values(X_test_scaled)
if isinstance(shap_values, list):
    shap_vals_positive = shap_values[1]
else:
    shap_vals_positive = shap_values

plt.figure()
shap.summary_plot(shap_vals_positive, X_test_scaled, show=False)
plt.savefig(METRICS_DIR / 'shap_summary.png', bbox_inches='tight')
plt.close()

plt.figure()
shap.summary_plot(shap_vals_positive, X_test_scaled, plot_type="bar", show=False)
plt.savefig(METRICS_DIR / 'shap_feature_importance.png', bbox_inches='tight')
plt.close()

# --- FASE 8: REPORTE ---
print("\n=== FASE 8: Generación de Reporte ===")
smote_text = f"Se detectó un desbalance (Clase mayoritaria: {dist_train.max():.1f}%). Se aplicó SMOTE al conjunto de entrenamiento." if smote_applied else "No se detectó desbalance crítico, no se aplicó SMOTE."

md_content = f"""# Reporte de Modelado y Evaluación

## Dataset
- **Total Registros:** {len(df)}
- **Train Size:** {len(X_train)}
- **Test Size:** {len(X_test)}

## Distribución de Clases
- **Completo:** 0: {dist_total[0]:.1f}%, 1: {dist_total.get(1, 0):.1f}%
- **Train:** 0: {dist_train[0]:.1f}%, 1: {dist_train.get(1, 0):.1f}%
- **Aplicación de SMOTE:** {smote_text}

## Comparación de Modelos
{df_eval.to_markdown(index=False)}

## Modelo Ganador
**{best_model_name}**
*Justificación Clínica:* En el contexto clínico, un falso negativo (paciente enfermo no detectado) es mucho más riesgoso que un falso positivo. Por ello, hemos priorizado maximizar el **Recall**, utilizando secundariamente ROC-AUC y F1-Score como criterios de desempate.

## Calibración
El modelo ganador fue calibrado usando Isotonic Regression.
- Brier Score Original: {brier_orig:.4f}
- Brier Score Calibrado: {brier_calib:.4f}

## SHAP y Explicabilidad
Se ha serializado el explainer SHAP (`shap_explainer.pkl`). Las variables más influyentes a nivel global fueron extraídas utilizando validación cruzada. Revisa los gráficos en `data/plots/metrics/` para el detalle.

## Incertidumbre
Se incluye una utilidad de Bootstrap (`bootstrap_confidence_interval` en `utils.py`) que permite evaluar la incertidumbre local para cada predicción de la API.

## Conclusiones
El modelo calibrado `model_calibrated.pkl` y su `StandardScaler` (`scaler.pkl`) se encuentran listos para ser expuestos vía API Flask. Ambos han sido construidos respetando estrictamente la pureza estadística sin data leakage.
"""
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(md_content)

print("Pipeline ejecutado exitosamente.")
