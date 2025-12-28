import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Portal Conductores", layout="wide")
st.title("🚖 PORTAL CONDUCTOR")

# 🆔 ID DE LA HOJA
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"

# --- FUNCIÓN DE CARGA ---
def cargar_datos(hoja):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df_choferes = cargar_datos("CHOFERES")
df_viajes = cargar_datos("VIAJES")

if not df_choferes.empty:
    st.markdown("### Identifícate")
    # Limpiamos nombres vacíos
    nombres = df_choferes["Nombre"].dropna().unique()
    chofer = st.selectbox("Soy:", nombres)
    
    if chofer:
        datos = df_choferes[df_choferes["Nombre"] == chofer].iloc[0]
        
        # 1. Filtramos viajes
        mis_viajes = pd.DataFrame()
        if not df_viajes.empty and "Conductor Asignado" in df_viajes.columns:
            mis_viajes = df_viajes[df_viajes["Conductor Asignado"] == chofer]
            
        # 2. Cálculos de Fechas (Con corrección de errores 'nan')
        dias_texto = "Pendiente"
        try:
            # Intentamos leer la fecha, si está vacía no falla
            if pd.notna(datos.get("Fecha_Registro")):
                fecha_reg = pd.to_datetime(datos["Fecha_Registro"], dayfirst=True)
                dias = (datetime.now() - fecha_reg).days
                dias_texto = f"{dias} días"
        except: pass
        
        # Buscamos la columna correcta para el vencimiento
        vencimiento = datos.get("Vence_Suscripcion") # Nombre exacto de tu Excel
        if pd.isna(vencimiento): vencimiento = "No asignado"
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("📅 Tiempo Activo", dias_texto)
        c2.metric("🚗 Viajes Totales", len(mis_viajes))
        c3.metric("💲 Vencimiento", str(vencimiento))
        
        st.divider()
        st.subheader("📜 Historial de Carreras")
        st.dataframe(mis_viajes, use_container_width=True)
        
        if st.button("🔄 Actualizar Datos"):
            st.cache_data.clear()
            st.rerun()
else:
    st.warning("No se encontraron choferes. Revisa que la hoja 'CHOFERES' tenga datos.")
