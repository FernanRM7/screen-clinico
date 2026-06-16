import streamlit as st
import requests

API_URL = "http://127.0.0.1:5001"

st.set_page_config(page_title="Screen Clínico - Frontend", layout="centered")
st.title(" Screen Clínico")
st.markdown("Consumiendo la API Flask")

if st.button("Saludar a la API"):
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            st.success(f"Respuesta de la API: {response.text}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error(" No se pudo conectar a la API. ¿Está corriendo Flask en el puerto 5001?")
