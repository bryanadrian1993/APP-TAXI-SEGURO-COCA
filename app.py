import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials
from streamlit_js_eval import get_geolocation

# 1. DISEÑO Y CONFIGURACIÓN (IDÉNTICO AL ORIGINAL)
st.set_page_config(page_title="Taxi Seguro - PRUEBAS", page_icon="🚖")

# Función para conectar (Apuntando a BD_TAXI_PRUEBAS)
def conectar_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    # Aquí mantenemos tu hoja de pruebas
    hoja = client.open("BD_TAXI_PRUEBAS").sheet1
    return hoja

# Estilos CSS para que los botones se vean igual
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FFD700;
        color: black;
        font-weight: bold;
        border: none;
    }
    .wa-btn {
        background-color: #25D366;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚖 Sistema de Taxi Seguro")
st.write("Configuración de Pruebas")

# Ubicación
location = get_geolocation()

# Formulario (Con tus etiquetas originales)
nombre = st.text_input("👤 Tu Nombre:")
celular = st.text_input("📱 Tu WhatsApp:")
tipo = st.selectbox("🚗 Tipo de unidad:", ["Auto Normal", "Camioneta", "VIP"])
referencia = st.text_area("📍 ¿Dónde te recogemos? (Referencia):")

if st.button("PEDIR UNIDAD AHORA"):
    if not nombre or not celular:
        st.error("❌ Por favor llena tu nombre y celular.")
    else:
        # Lógica de guardado
        hoja = conectar_sheets()
        if hoja:
            try:
                fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                # GPS
                if location:
                    lat = location['coords']['latitude']
                    lon = location['coords']['longitude']
                    mapa_link = f"https://www.google.com/maps?q={lat},{lon}"
                else:
                    mapa_link = "No determinada"

                # Guardar en Sheets
                hoja.append_row([fecha, nombre, celular, tipo, referencia, mapa_link, "PENDIENTE"])

                # Mensaje de WhatsApp (Idéntico al tuyo)
                mensaje_texto = (
                    f"🚖 *PEDIDO DE UNIDAD*\n\n"
                    f"👤 *Cliente:* {nombre}\n"
                    f"📱 *WhatsApp:* {celular}\n"
                    f"🚖 *Servicio:* {tipo}\n"
                    f"🏠 *Referencia:* {referencia}\n"
                    f"📍 *UBICACIÓN:* {mapa_link}"
                )
                
                msg_encoded = urllib.parse.quote(mensaje_texto)
                link_final = f"https://wa.me/593962384356?text={msg_encoded}"

                st.success("✅ ¡Datos guardados!")
                st.markdown(f'<a href="{link_final}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error: {e}")
