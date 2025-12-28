import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Portal Conductores", layout="wide")
st.title("🚖 PORTAL CONDUCTOR")

# 🔗 ENLACE DIRECTO (Indispensable)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leemos pasando el LINK explícitamente
    df_choferes = conn.read(spreadsheet=URL_HOJA, worksheet="CHOFERES", ttl=2)
    df_viajes = conn.read(spreadsheet=URL_HOJA, worksheet="VIAJES", ttl=2)
    
    if not df_choferes.empty:
        nombres = df_choferes["Nombre"].dropna().unique()
        chofer = st.selectbox("Soy:", nombres)
        if chofer:
            datos = df_choferes[df_choferes["Nombre"] == chofer].iloc[0]
            st.info(f"Hola {chofer}. Vencimiento: {datos.get('Vencimiento_Suscripcion')}")
            
            mis_viajes = df_viajes[df_viajes["Conductor Asignado"] == chofer] if "Conductor Asignado" in df_viajes.columns else pd.DataFrame()
            st.dataframe(mis_viajes)
    else:
        st.warning("No hay choferes en la lista.")

except Exception as e:
    st.error(f"Error conectando: {e}")
    st.write("Prueba borrando el archivo 'Secrets' en la configuración de Streamlit.")
