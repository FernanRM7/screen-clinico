import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:5001"

st.set_page_config(page_title="Screen Clínico", layout="centered")
st.title("Screen Clínico")
st.markdown("Evaluación de riesgo de diabetes")

if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.form_data = {}
    st.session_state.result = None

def next_step():
    data = collect_step_data()
    if validate_step(data):
        st.session_state.form_data.update(data)
        st.session_state.step += 1
        st.rerun()

def prev_step():
    data = collect_step_data()
    st.session_state.form_data.update(data)
    st.session_state.step -= 1
    st.rerun()

def go_to_step(n):
    data = collect_step_data()
    st.session_state.form_data.update(data)
    st.session_state.step = n
    st.rerun()

def collect_step_data():
    d = {}
    for k, v in st.session_state.items():
        if k.startswith("input_"):
            d[k.replace("input_", "")] = v
    return d

def validate_step(data):
    return True

step = st.session_state.step
form = st.session_state.form_data

progress = step / 4
st.progress(progress, text=f"Fase {step} de 4")

if step == 1:
    st.header("Fase 1: Datos Personales")

    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Edad", min_value=1, max_value=120, value=form.get("edad", 30), key="input_edad")
        st.selectbox("Sexo", options=["Seleccione", "Masculino", "Femenino", "Otro"],
                      index=0 if "sexo" not in form else ["Seleccione", "Masculino", "Femenino", "Otro"].index(form["sexo"]),
                      key="input_sexo")
    with col2:
        st.number_input("Peso (kg)", min_value=20.0, max_value=300.0, value=form.get("peso", 70.0), step=0.1, key="input_peso")
        st.number_input("Altura (cm)", min_value=50.0, max_value=250.0, value=form.get("altura", 170.0), step=0.1, key="input_altura")

    st.subheader("Datos Familiares")
    st.radio("¿Tiene familiares con diabetes?", options=["Seleccione", "Sí", "No"],
              index=0 if "tiene_familiares" not in form else ["Seleccione", "Sí", "No"].index(form["tiene_familiares"]),
              key="input_tiene_familiares")
    if st.session_state.get("input_tiene_familiares") == "Sí":
        st.multiselect("¿Quiénes?", options=["Padres", "Hermanos", "Hijos", "Abuelos", "Tíos", "Otros"],
                        default=form.get("familiares_diabetes", []), key="input_familiares_diabetes")

    st.subheader("Datos Médicos")
    cols = st.columns(2)
    with cols[0]:
        st.radio("¿Tiene colesterol alto?", options=["Seleccione", "Sí", "No", "No sabe"],
                  index=0 if "colesterol_alto" not in form else ["Seleccione", "Sí", "No", "No sabe"].index(form["colesterol_alto"]),
                  key="input_colesterol_alto")
        st.radio("¿Consume medicamentos regularmente?", options=["Seleccione", "Sí", "No"],
                  index=0 if "medicamentos" not in form else ["Seleccione", "Sí", "No"].index(form["medicamentos"]),
                  key="input_medicamentos")
    with cols[1]:
        st.radio("¿Tiene enfermedades cardiovasculares?", options=["Seleccione", "Sí", "No"],
                  index=0 if "enfermedades_cv" not in form else ["Seleccione", "Sí", "No"].index(form["enfermedades_cv"]),
                  key="input_enfermedades_cv")
        st.radio("¿Padece hipertensión arterial?", options=["Seleccione", "Sí", "No"],
                  index=0 if "hipertension" not in form else ["Seleccione", "Sí", "No"].index(form["hipertension"]),
                  key="input_hipertension")

    col1, col2, col3 = st.columns([1, 1, 4])
    with col2:
        if st.button("Siguiente", type="primary", use_container_width=True):
            next_step()

elif step == 2:
    st.header("Fase 2: Hábitos de Vida")

    st.radio("¿Realiza actividad física regularmente?", options=["Seleccione", "Sí", "No"],
              index=0 if "actividad_fisica" not in form else ["Seleccione", "Sí", "No"].index(form["actividad_fisica"]),
              key="input_actividad_fisica")

    if st.session_state.get("input_actividad_fisica") == "Sí":
        col1, col2 = st.columns(2)
        with col1:
            st.slider("¿Cuántos días por semana?", 1, 7, value=form.get("dias_ejercicio", 3), key="input_dias_ejercicio")
        with col2:
            st.selectbox("¿Cuánto tiempo al día?", options=["Seleccione", "Menos de 30 min", "30 - 60 min", "Más de 60 min"],
                          index=0 if "tiempo_ejercicio" not in form else ["Seleccione", "Menos de 30 min", "30 - 60 min", "Más de 60 min"].index(form["tiempo_ejercicio"]),
                          key="input_tiempo_ejercicio")

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("¿Consume bebidas azucaradas?", options=["Seleccione", "Nunca", "Rara vez", "A veces", "Frecuentemente", "Diario"],
                      index=0 if "bebidas_azucaradas" not in form else ["Seleccione", "Nunca", "Rara vez", "A veces", "Frecuentemente", "Diario"].index(form["bebidas_azucaradas"]),
                      key="input_bebidas_azucaradas")
    with col2:
        st.selectbox("¿Fuma?", options=["Seleccione", "Nunca", "Ocasionalmente", "Diariamente"],
                      index=0 if "fuma" not in form else ["Seleccione", "Nunca", "Ocasionalmente", "Diariamente"].index(form["fuma"]),
                      key="input_fuma")

    st.slider("¿Cuántas horas duerme por noche?", 4, 12, value=form.get("horas_sueno", 7), key="input_horas_sueno")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Anterior", use_container_width=True):
            prev_step()
    with col2:
        if st.button("Siguiente", type="primary", use_container_width=True):
            next_step()

elif step == 3:
    st.header("Fase 3: Síntomas Asociados a la Diabetes")

    cols = st.columns(2)
    with cols[0]:
        st.radio("¿Siente sed excesiva con frecuencia?", options=["Sí", "No"],
                  index=0 if "sed_excesiva" not in form else ["Sí", "No"].index(form["sed_excesiva"]),
                  key="input_sed_excesiva")
        st.radio("¿Ha experimentado pérdida de peso inexplicable?", options=["Sí", "No"],
                  index=0 if "perdida_peso" not in form else ["Sí", "No"].index(form["perdida_peso"]),
                  key="input_perdida_peso")
        st.radio("¿Tiene visión borrosa?", options=["Sí", "No"],
                  index=0 if "vision_borrosa" not in form else ["Sí", "No"].index(form["vision_borrosa"]),
                  key="input_vision_borrosa")
    with cols[1]:
        st.radio("¿Orina más veces de lo habitual?", options=["Sí", "No"],
                  index=0 if "orina_frecuente" not in form else ["Sí", "No"].index(form["orina_frecuente"]),
                  key="input_orina_frecuente")
        st.radio("¿Presenta fatiga constante?", options=["Sí", "No"],
                  index=0 if "fatiga" not in form else ["Sí", "No"].index(form["fatiga"]),
                  key="input_fatiga")
        st.radio("¿Presenta hormigueo en manos o pies?", options=["Sí", "No"],
                  index=0 if "hormigueo" not in form else ["Sí", "No"].index(form["hormigueo"]),
                  key="input_hormigueo")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Anterior", use_container_width=True):
            prev_step()
    with col2:
        if st.button("Siguiente", type="primary", use_container_width=True):
            next_step()

elif step == 4:
    st.header("Fase 4: Datos Clínicos")
    st.caption("Puede dejar los campos en 0 si no dispone del valor.")

    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Nivel de glucosa en ayunas (mg/dL)", min_value=0, max_value=500,
                         value=form.get("glucosa", 0), key="input_glucosa")
        st.number_input("Valor de HbA1c (%)", min_value=0, max_value=20,
                         value=form.get("hba1c", 0), step=1, key="input_hba1c")
        st.number_input("Nivel de colesterol total (mg/dL)", min_value=0, max_value=500,
                         value=form.get("colesterol_total", 0), key="input_colesterol_total")
    with col2:
        st.number_input("Nivel de triglicéridos (mg/dL)", min_value=0, max_value=2000,
                         value=form.get("trigliceridos", 0), key="input_trigliceridos")
        st.number_input("Presión arterial sistólica (mmHg)", min_value=0, max_value=250,
                         value=form.get("presion_sistolica", 0), key="input_presion_sistolica")
        st.number_input("Presión arterial diastólica (mmHg)", min_value=0, max_value=150,
                         value=form.get("presion_diastolica", 0), key="input_presion_diastolica")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Anterior", use_container_width=True):
            prev_step()
    with col2:
        if st.button("Evaluar Riesgo", type="primary", use_container_width=True):
            all_data = collect_step_data()
            all_data.update(st.session_state.form_data)
            st.session_state.form_data = all_data
            submit_screening(all_data)

if st.session_state.get("result"):
    st.divider()
    r = st.session_state.result
    if r.get("error"):
        st.error(r["error"])
    else:
        nivel = r.get("nivel_riesgo", "Bajo")
        color_map = {"Bajo": "green", "Moderado": "orange", "Alto": "red"}
        st.subheader("Resultado de la Evaluación")
        st.markdown(f"**Nivel de riesgo:** :{color_map.get(nivel, 'gray')}[{nivel}]")
        st.markdown(f"**Puntuación:** {r.get('puntuacion', 0)}/100")
        if r.get("recomendacion"):
            st.info(r["recomendacion"])
        st.markdown("---")
        st.markdown("**Datos enviados:**")
        st.json(st.session_state.form_data)
        if st.button("Nueva Evaluación"):
            for k in list(st.session_state.keys()):
                if k.startswith("input_"):
                    del st.session_state[k]
            st.session_state.step = 1
            st.session_state.form_data = {}
            st.session_state.result = None
            st.rerun()

def submit_screening(data):
    payload = {
        "edad": data.get("edad", 0),
        "sexo": data.get("sexo", ""),
        "peso": data.get("peso", 0),
        "altura": data.get("altura", 0),
        "tiene_familiares": data.get("tiene_familiares", "No"),
        "familiares_diabetes": data.get("familiares_diabetes", []),
        "colesterol_alto": data.get("colesterol_alto", "No"),
        "enfermedades_cv": data.get("enfermedades_cv", "No"),
        "medicamentos": data.get("medicamentos", "No"),
        "hipertension": data.get("hipertension", "No"),
        "actividad_fisica": data.get("actividad_fisica", "No"),
        "dias_ejercicio": data.get("dias_ejercicio", 0),
        "tiempo_ejercicio": data.get("tiempo_ejercicio", ""),
        "bebidas_azucaradas": data.get("bebidas_azucaradas", "Nunca"),
        "fuma": data.get("fuma", "Nunca"),
        "horas_sueno": data.get("horas_sueno", 7),
        "sed_excesiva": data.get("sed_excesiva", "No"),
        "orina_frecuente": data.get("orina_frecuente", "No"),
        "perdida_peso": data.get("perdida_peso", "No"),
        "fatiga": data.get("fatiga", "No"),
        "vision_borrosa": data.get("vision_borrosa", "No"),
        "hormigueo": data.get("hormigueo", "No"),
        "glucosa": data.get("glucosa", 0),
        "hba1c": data.get("hba1c", 0),
        "colesterol_total": data.get("colesterol_total", 0),
        "trigliceridos": data.get("trigliceridos", 0),
        "presion_sistolica": data.get("presion_sistolica", 0),
        "presion_diastolica": data.get("presion_diastolica", 0),
    }
    try:
        resp = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        if resp.status_code == 200:
            st.session_state.result = resp.json()
        else:
            st.session_state.result = {"error": f"Error {resp.status_code}: {resp.text}"}
        st.rerun()
    except requests.exceptions.ConnectionError:
        st.session_state.result = {"error": "No se pudo conectar a la API Flask"}
        st.rerun()
