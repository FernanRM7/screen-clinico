import joblib
import numpy as np
import pandas as pd
from pathlib import Path

EXPLAINER_PATH = Path(__file__).parent / 'shap_explainer.pkl'
explainer = None

def load_explainer():
    global explainer
    if explainer is None:
        explainer = joblib.load(EXPLAINER_PATH)
    return explainer

def explain_prediction(features_df):
    """
    Explica la predicción de una instancia individual.
    
    Args:
        features_df (pd.DataFrame): Dataframe con 1 fila y las características escaladas, 
                                    incluyendo los nombres de las columnas.
    
    Returns:
        dict: top 5 positivas, top 5 negativas y valores crudos.
    """
    exp = load_explainer()
    
    # Calcular valores SHAP
    shap_values = exp.shap_values(features_df)
    
    # Manejar estructura según el tipo de explainer (TreeExplainer puede devolver lista)
    if isinstance(shap_values, list):
        shap_vals_positive = shap_values[1][0]
    else:
        # Algunos explainer devuelven array 3D o 2D
        if len(shap_values.shape) == 3:
            shap_vals_positive = shap_values[0, :, 1]
        else:
            shap_vals_positive = shap_values[0]

    feature_names = features_df.columns.tolist()
    
    contributions = []
    for name, val in zip(feature_names, shap_vals_positive):
        contributions.append({
            "feature": name,
            "value": float(val),
            "abs_value": abs(float(val))
        })
        
    # Ordenar por magnitud absoluta (impacto total)
    contributions.sort(key=lambda x: x["abs_value"], reverse=True)
    
    top_positive = [c for c in contributions if c["value"] > 0][:5]
    top_negative = [c for c in contributions if c["value"] < 0][:5]
    
    # Limpiar abs_value para el retorno
    for c in top_positive + top_negative:
        del c["abs_value"]

    return {
        "top_positive": top_positive,
        "top_negative": top_negative,
        "shap_values": [float(v) for v in shap_vals_positive]
    }
