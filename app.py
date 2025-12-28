import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials
from streamlit_js_eval import get_geolocation

# Configuración de la página
st.set_page_config(page_title="Taxi Seguro - PRUEBAS", page_icon="🚖")

# 1. FUNCIÓN DE CONEXIÓN A GOOGLE SHEETS
def conectar_sheets():
    # Usa los secretos configurados en Streamlit Cloud
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # AQUÍ ESTÁ EL CAMBIO DE NOMBRE DE LA HOJA
    hoja = client.open("BD_TAXI_PRUEBAS").sheet1
    return hoja

# 2. OBTENER UBICACIÓN DEL TAXISTA (PRUEBAS)
st.title("🚖 Sistema de Taxi Seguro (Copia de Pruebas)")
st.write("Configuración actual: Guardando en 'BD_TAXI_PRUEBAS'")

location = get_geolocation()

# 3. FORMULARIO DE REGISTRO
with st.form("formulario_taxi"):
    nombre = st.text_input("Nombre del Cliente:")
    celular = st.text_input("Número de WhatsApp (ej: 593...):")
    tipo_viaje = st.selectbox("Tipo de unidad:", ["Auto Normal", "Camioneta", "VIP"])
    referencia = st.text_area("Referencia del lugar de recogida:")
    
    boton_enviar = st.form_submit_button("Pedir Taxi Ahora")

if boton_enviar:
    if nombre and celular and referencia:
        try:
            hoja = conectar_sheets()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Gestionar ubicación
            if location:
                lat = location['coords']['latitude']
                lon = location['coords']['longitude']
                mapa_link = f"https://www.google.com/maps?q={lat},{lon}"
                coords_txt = f"{lat}, {lon}"
            else:
                mapa_link = "No proporcionada"
                coords_txt = "No proporcionada"
            
            # 4. GUARDAR EN GOOGLE SHEETS (Mismo orden que tu original)
            # Orden: Fecha, Nombre, Celular, Tipo, Referencia, Ubicación, Estado
            hoja.append_row([fecha, nombre, celular, tipo_viaje, referencia, mapa_link, "PRUEBA-PENDIENTE"])
            
            st.success("✅ ¡Pedido registrado en la hoja de PRUEBAS!")

            # 5. CREAR MENSAJE PARA WHATSAPP
            mensaje = (
                f"🚖 *NUEVO PEDIDO (PRUEBA)*\n\n"
                f"👤 *Cliente:* {nombre}\n"
                f"📱 *Celular:* {celular}\n"
                f"🚗 *Unidad:* {tipo_viaje}\n"
                f"📍 *Recoger en:* {referencia}\n"
                f"🗺️ *Ubicación:* {mapa_link}"
            )
            
            msg_encoded = urllib.parse.quote(mensaje)
            # Tu número de WhatsApp configurado
            link_wa = f"https://wa.me/593962384356?text={msg_encoded}"
            
            st.markdown(f"""
                <a href="{link_wa}" target="_blank">
                    <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                        Enviar a WhatsApp del Taxista
                    </button>
                </a>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al conectar: {e}")
            st.info("Revisa que hayas compartido la hoja 'BD_TAXI_PRUEBAS' con el correo de servicio.")
    else:
        st.warning("Por favor, llena todos los campos.")

st.write("---")
st.caption("Versión de Respaldo y Pruebas - Taxi Seguro")
