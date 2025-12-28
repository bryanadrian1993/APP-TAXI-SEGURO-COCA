import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Portal Conductores", page_icon="🚕", layout="wide")
st.title("🚖 PORTAL DEL CONDUCTOR")

# 🔗 ENLACE DIRECTO (Igual que en la otra app)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Le pasamos el enlace DIRECTO aquí para que no busque en secrets
        choferes = conn.read(spreadsheet=URL_HOJA, worksheet="CHOFERES", ttl=2)
        viajes = conn.read(spreadsheet=URL_HOJA, worksheet="VIAJES", ttl=2)
        return choferes, viajes
    except Exception as e:
        st.error(f"⚠️ Error conectando: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_choferes, df_viajes = cargar_datos()

st.markdown("### Identifícate")
if not df_choferes.empty and "Nombre" in df_choferes.columns:
    lista_nombres = df_choferes["Nombre"].dropna().unique()
    chofer_seleccionado = st.selectbox("Selecciona tu nombre:", lista_nombres)
    
    if chofer_seleccionado:
        datos = df_choferes[df_choferes["Nombre"] == chofer_seleccionado].iloc[0]
        mis_viajes = df_viajes[df_viajes["Conductor Asignado"] == chofer_seleccionado] if "Conductor Asignado" in df_viajes.columns else pd.DataFrame()

        # Cálculos simples
        try: dias = (datetime.now() - pd.to_datetime(datos["Fecha_Registro"], dayfirst=True)).days
        except: dias = 0
        
        estado = "✅ AL DÍA"
        try: 
            if pd.to_datetime(str(datos.get("Vencimiento_Suscripcion"))) < datetime.now(): estado = "❌ VENCIDO - PAGAR $1"
        except: pass

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("📅 Días Activo", dias)
        c2.metric("🚗 Viajes", len(mis_viajes))
        c3.metric("💲 Estado", estado)
        st.caption(f"Vence: {datos.get('Vencimiento_Suscripcion')}")
        
        st.divider()
        st.subheader("📜 Historial")
        st.dataframe(mis_viajes, use_container_width=True)
        
        if st.button("🔄 Actualizar"): st.cache_data.clear(); st.rerun()
else:
    st.warning("No se encontraron choferes o no se pudo leer la hoja.")
