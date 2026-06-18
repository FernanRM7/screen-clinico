from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!. Hello from Flask</p>"


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400

    puntuacion = 0

    puntuacion += _puntuar_edad(data.get("edad", 0))

    imc = _calcular_imc(data.get("peso", 0), data.get("altura", 0))
    puntuacion += _puntuar_imc(imc)

    if data.get("tiene_familiares") == "Sí":
        puntuacion += 8
    if data.get("colesterol_alto") == "Sí":
        puntuacion += 5
    if data.get("enfermedades_cv") == "Sí":
        puntuacion += 5
    if data.get("hipertension") == "Sí":
        puntuacion += 6

    if data.get("actividad_fisica") == "No":
        puntuacion += 4
    freq_bebidas = {"Nunca": 0, "Rara vez": 1, "A veces": 3, "Frecuentemente": 5, "Diario": 8}
    puntuacion += freq_bebidas.get(data.get("bebidas_azucaradas", "Nunca"), 0)
    freq_fuma = {"Nunca": 0, "Ocasionalmente": 4, "Diariamente": 8}
    puntuacion += freq_fuma.get(data.get("fuma", "Nunca"), 0)
    horas = data.get("horas_sueno", 7)
    if horas < 6 or horas > 9:
        puntuacion += 3

    sintomas_map = {"Sí": 4, "No": 0}
    for key in ["sed_excesiva", "orina_frecuente", "perdida_peso", "fatiga", "vision_borrosa", "hormigueo"]:
        puntuacion += sintomas_map.get(data.get(key, "No"), 0)

    glucosa = data.get("glucosa", 0)
    if glucosa > 0:
        if glucosa >= 126:
            puntuacion += 15
        elif glucosa >= 100:
            puntuacion += 8

    hba1c = data.get("hba1c", 0)
    if hba1c > 0:
        if hba1c >= 6.5:
            puntuacion += 15
        elif hba1c >= 5.7:
            puntuacion += 8

    col_total = data.get("colesterol_total", 0)
    if col_total >= 240:
        puntuacion += 4
    elif col_total >= 200:
        puntuacion += 2

    trig = data.get("trigliceridos", 0)
    if trig >= 200:
        puntuacion += 4
    elif trig >= 150:
        puntuacion += 2

    sistolica = data.get("presion_sistolica", 0)
    diastolica = data.get("presion_diastolica", 0)
    if sistolica >= 140 or diastolica >= 90:
        puntuacion += 5
    elif sistolica >= 130 or diastolica >= 85:
        puntuacion += 3

    puntuacion = min(puntuacion, 100)

    if puntuacion >= 50:
        nivel = "Alto"
        recomendacion = (
            "Su evaluación muestra un riesgo alto de diabetes. "
            "Le recomendamos acudir a un médico para realizarse pruebas de confirmación."
        )
    elif puntuacion >= 25:
        nivel = "Moderado"
        recomendacion = (
            "Su evaluación muestra un riesgo moderado. "
            "Considere mejorar sus hábitos alimenticios, realizar actividad física "
            "y consultar a un especialista si los síntomas persisten."
        )
    else:
        nivel = "Bajo"
        recomendacion = (
            "Su evaluación muestra un riesgo bajo. "
            "Mantenga un estilo de vida saludable y realice chequeos periódicos."
        )

    return jsonify({
        "nivel_riesgo": nivel,
        "puntuacion": puntuacion,
        "recomendacion": recomendacion,
    })


def _calcular_imc(peso_kg, altura_cm):
    if altura_cm <= 0:
        return 0
    return round(peso_kg / ((altura_cm / 100) ** 2), 1)


def _puntuar_edad(edad):
    if edad >= 65:
        return 8
    if edad >= 55:
        return 6
    if edad >= 45:
        return 4
    if edad >= 35:
        return 2
    return 0


def _puntuar_imc(imc):
    if imc <= 0:
        return 0
    if imc >= 40:
        return 8
    if imc >= 35:
        return 6
    if imc >= 30:
        return 5
    if imc >= 25:
        return 3
    return 0


if __name__ == "__main__":
    app.run(port=5001, debug=True)
