import streamlit as st
from streamlit_js_eval import get_geolocation
import urllib.parse

# Configuración básica
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

# Estilos visuales para que se vea como tus fotos
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #000; }
    .sub-title { font-size: 25px; font-weight: bold; text-align: center; color: #E91E63; margin-top: -10px; }
    .step-header { font-size: 18px; font-weight: bold; margin-top: 20px; color: #333; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚖 TAXI SEGURO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📍 COCA</div>', unsafe_allow_html=True)
st.divider()

# PASO 1
st.markdown('<div class="step-header">🛰️ PASO 1: ACTIVAR UBICACIÓN</div>', unsafe_allow_html=True)
loc = get_geolocation()
if loc:
    st.success("✅ GPS ACTIVADO: Podemos ver tu ubicación real.")
else:
    st.info("📍 Por favor activa tu GPS.")

# PASO 2
st.markdown('<div class="step-header">📝 PASO 2: DATOS DEL VIAJE</div>', unsafe_allow_html=True)
with st.form("form_pedido"):
    nombre = st.text_input("Nombre del cliente:")
    ref = st.text_input("Dirección/Referencia exacta:")
    tipo = st.selectbox("Tipo de unidad:", ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"])
    
    # El botón que solicitaste
    enviar = st.form_submit_button("💰 COTIZAR VIAJE")

if enviar:
    st.info("Buscando conductor libre...")
