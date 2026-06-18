import numpy as np

def bootstrap_confidence_interval(model_calibrated, scaler, features_df, n_iterations=1000, confidence_level=0.95):
    """
    Calcula el intervalo de confianza de una predicción individual usando bootstrap.
    Dado que el modelo final es un CalibratedClassifierCV entrenado con cv=5, 
    este funciona como un ensamble de 5 modelos calibrados. 
    El método de bootstrap consiste en muestrear estos modelos base con reemplazo,
    recalcular la probabilidad promedio para cada iteración y extraer los percentiles.
    
    Args:
        model_calibrated: Modelo CalibratedClassifierCV ya entrenado.
        scaler: StandardScaler entrenado.
        features_df: DataFrame con la instancia a predecir (ya escalada).
        n_iterations: Número de iteraciones bootstrap.
        confidence_level: Nivel de confianza deseado (ej. 0.95).
        
    Returns:
        dict: Diccionario con la predicción puntual, límites inferior/superior y el margen.
    """
    if not hasattr(model_calibrated, 'calibrated_classifiers_'):
        raise ValueError("El modelo debe ser un CalibratedClassifierCV ajustado.")
        
    classifiers = model_calibrated.calibrated_classifiers_
    n_clfs = len(classifiers)
    
    bootstrap_preds = []
    
    # 1. Muestrear con reemplazo y 2. Recalcular probabilidades
    for _ in range(n_iterations):
        # Muestreamos índices de los clasificadores con reemplazo
        sampled_indices = np.random.choice(n_clfs, size=n_clfs, replace=True)
        
        prob_sum = 0.0
        for idx in sampled_indices:
            clf = classifiers[idx]
            # Obtener probabilidad de la clase positiva (1)
            prob = clf.predict_proba(features_df)[0, 1]
            prob_sum += prob
            
        # Promedio del ensamble bootstrap
        bootstrap_preds.append(prob_sum / n_clfs)
        
    bootstrap_preds = np.array(bootstrap_preds)
    
    # 3. Obtener distribución y 4. Calcular percentiles
    lower_percentile = (1.0 - confidence_level) / 2.0 * 100
    upper_percentile = (confidence_level + (1.0 - confidence_level) / 2.0) * 100
    
    lower_bound = np.percentile(bootstrap_preds, lower_percentile)
    upper_bound = np.percentile(bootstrap_preds, upper_percentile)
    
    # Predicción puntual original (usando todos los modelos sin reemplazo)
    point_prediction = model_calibrated.predict_proba(features_df)[0, 1]
    
    # Calcular el margen (usamos la diferencia máxima hacia los límites como margen conservador)
    margin = max(point_prediction - lower_bound, upper_bound - point_prediction)
    
    return {
        "prediction": round(point_prediction, 2),
        "lower": round(lower_bound, 2),
        "upper": round(upper_bound, 2),
        "margin": round(margin, 2),
        "formatted_text": f"Riesgo estimado: {round(point_prediction*100)}% ± {round(margin*100)}%"
    }
