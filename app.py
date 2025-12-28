import streamlit as st
from streamlit_js_eval import get_geolocation
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

# --- ESTILOS VISUALES ORIGINALES ---
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #000; }
    .sub-title { font-size: 25px; font-weight: bold; text-align: center; color: #E91E63; margin-top: -10px; margin-bottom: 20px; }
    .step-header { font-size: 18px; font-weight: bold; margin-top: 20px; color: #333; }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<div class="main-title">🚖 TAXI SEGURO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📍 COCA</div>', unsafe_allow_html=True)
st.divider()

# ==========================================
# SECCIÓN 1: PEDIR TAXI (CLIENTE)
# ==========================================
st.markdown('<div class="step-header">🛰️ PASO 1: ACTIVAR UBICACIÓN</div>', unsafe_allow_html=True)
loc = get_geolocation()
if loc:
    st.success("✅ GPS ACTIVADO: Podemos ver tu ubicación real.")
else:
    st.info("📍 Por favor activa tu GPS para localizar la unidad más cercana.")

st.markdown('<div class="step-header">📝 PASO 2: DATOS DEL VIAJE</div>', unsafe_allow_html=True)
with st.form("form_pedido"):
    nombre_cliente = st.text_input("Nombre del cliente:")
    referencia = st.text_input("Dirección o Referencia exacta:")
    tipo_unidad = st.selectbox("Tipo de unidad:", ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"])
    
    boton_pedido = st.form_submit_button("💰 COTIZAR VIAJE")

if boton_pedido:
    st.info("🔍 Buscando conductores disponibles en el sector...")
    st.balloons()

# ==========================================
# SECCIÓN 2: REGISTRO DE SOCIOS (COMO ANTES)
# ==========================================
st.write("---")
st.markdown("<h3 style='text-align: center;'>📝 REGISTRO DE NUEVOS SOCIOS</h3>", unsafe_allow_html=True)

with st.expander("Haz clic aquí para registrarte como conductor"):
    with st.form("registro_conductor"):
        st.write("Completa tus datos básicos para la base de datos:")
        nombre_chof = st.text_input("Nombres y Apellidos:")
        cedula_chof = st.text_input("Número de Cédula:")
        placa_chof = st.text_input("Placa del Vehículo:")
        clave_chof = st.text_input("Crea una contraseña:", type="password")
        
        enviar_reg = st.form_submit_button("🚀 GUARDAR Y CONTINUAR")
        
        if enviar_reg:
            if nombre_chof and cedula_chof and placa_chof:
                st.success(f"✅ ¡Datos guardados, {nombre_chof}! Ahora envía tus documentos por correo.")
            else:
                st.error("❌ Por favor completa los campos principales.")

st.markdown("<p style='text-align: center; color: gray;'>Taxi Seguro Coca v1.0</p>", unsafe_allow_html=True)
