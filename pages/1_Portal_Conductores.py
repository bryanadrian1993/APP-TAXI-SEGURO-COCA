import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Portal Conductores", layout="wide")
st.title("🚖 PORTAL CONDUCTOR")

# 🆔 ID DE LA HOJA
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"

# --- FUNCIÓN INFALIBLE ---
def cargar_datos(hoja):
    try:
        # Truco: Bajamos la hoja como CSV directo de Google
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}"
        return pd.read_csv(url)
    except Exception as e:
        return pd.DataFrame()

# Cargamos datos
df_choferes = cargar_datos("CHOFERES")
df_viajes = cargar_datos("VIAJES")

if not df_choferes.empty:
    st.markdown("### Identifícate")
    nombres = df_choferes["Nombre"].dropna().unique()
    chofer = st.selectbox("Soy:", nombres)
    
    if chofer:
        datos = df_choferes[df_choferes["Nombre"] == chofer].iloc[0]
        
        # Filtramos viajes
        mis_viajes = pd.DataFrame()
        if not df_viajes.empty and "Conductor Asignado" in df_viajes.columns:
            mis_viajes = df_viajes[df_viajes["Conductor Asignado"] == chofer]
            
        # Cálculos de fechas
        dias = 0
        try:
            fecha_reg = pd.to_datetime(datos["Fecha_Registro"], dayfirst=True)
            dias = (datetime.now() - fecha_reg).days
        except: pass
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("📅 Días Activo", dias)
        c2.metric("🚗 Viajes", len(mis_viajes))
        c3.metric("💲 Vencimiento", str(datos.get("Vencimiento_Suscripcion", "-")))
        
        st.divider()
        st.subheader("Historial")
        st.dataframe(mis_viajes)
        
        if st.button("🔄 Actualizar"):
            st.cache_data.clear()
            st.rerun()
else:
    st.error("No se pudo leer la lista de choferes. Verifica que la hoja 'CHOFERES' exista y sea pública.")
