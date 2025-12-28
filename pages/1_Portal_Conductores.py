import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.request
import urllib.parse

st.set_page_config(page_title="Portal Conductores", layout="wide")
st.title("🚖 PORTAL CONDUCTOR")

# --- TUS ENLACES DE CONEXIÓN ---
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
# 👇 AQUÍ YA PUSE TU ENLACE NUEVO
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwI2zteeExU_Zy2yHLMR3A49ZYSHwP_xNGsTy-AuRiD_6llZA6V_QxvvOYiXD48w2uc/exec"

# --- FUNCIONES ---
def cargar_datos(hoja):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

def cambiar_estado(nombre, nuevo_estado):
    try:
        # Preparamos el nombre para enviarlo por internet (por si tiene tildes o espacios)
        nombre_safe = urllib.parse.quote(nombre)
        url_final = f"{URL_SCRIPT}?nombre={nombre_safe}&estado={nuevo_estado}"
        
        # Enviamos la orden al robot
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error de conexión: {e}"

# --- INTERFAZ ---
df_choferes = cargar_datos("CHOFERES")
df_viajes = cargar_datos("VIAJES")

if not df_choferes.empty:
    st.markdown("### 🆔 Identifícate")
    nombres = df_choferes["Nombre"].dropna().unique()
    chofer = st.selectbox("Selecciona tu nombre:", nombres)
    
    if chofer:
        datos = df_choferes[df_choferes["Nombre"] == chofer].iloc[0]
        # Leemos el estado, quitamos espacios y ponemos mayúsculas para evitar errores
        estado_actual = str(datos.get("Estado", "Desconocido")).strip().upper()
        
        st.divider()
        st.subheader("🚦 Tu Estado Actual")
        
        # Semáforo visual
        if estado_actual == "LIBRE":
            st.success(f"Estás: {estado_actual} 🟢 (Recibiendo carreras)")
        else:
            st.error(f"Estás: {estado_actual} 🔴 (No recibirás carreras)")
            
        c1, c2 = st.columns(2)
        
        # BOTÓN: ME PONGO LIBRE
        if c1.button("🟢 ME PONGO LIBRE", use_container_width=True):
            with st.spinner("Conectando con la central..."):
                res = cambiar_estado(chofer, "LIBRE")
                if "OK" in res:
                    st.toast("✅ ¡Listo! Ahora estás visible para el sistema.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Error al actualizar. Intenta de nuevo.")

        # BOTÓN: ME PONGO OCUPADO
        if c2.button("🔴 ESTOY OCUPADO", use_container_width=True):
            with st.spinner("Actualizando estado..."):
                res = cambiar_estado(chofer, "OCUPADO")
                if "OK" in res:
                    st.toast("⏸️ Te has puesto como Ocupado.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Error al actualizar.")

        # --- MÉTRICAS ---
        st.divider()
        
        # Filtro de viajes
        mis_viajes = pd.DataFrame()
        if not df_viajes.empty and "Conductor Asignado" in df_viajes.columns:
            mis_viajes = df_viajes[df_viajes["Conductor Asignado"] == chofer]
            
        # Cálculos de fecha
        dias_texto = "Pendiente"
        try:
            if pd.notna(datos.get("Fecha_Registro")):
                dias = (datetime.now() - pd.to_datetime(datos["Fecha_Registro"], dayfirst=True)).days
                dias_texto = f"{dias} días"
        except: pass
        
        vencimiento = datos.get("Vence_Suscripcion", "No asignado")
        if pd.isna(vencimiento): vencimiento = "No asignado"
        
        m1, m2, m3 = st.columns(3)
        m1.metric("📅 Antigüedad", dias_texto)
        m2.metric("🚗 Carreras", len(mis_viajes))
        m3.metric("💲 Vencimiento", str(vencimiento))
        
        st.subheader("📜 Historial")
        st.dataframe(mis_viajes, use_container_width=True)
        
        if st.button("🔄 Refrescar Pantalla"):
            st.cache_data.clear()
            st.rerun()
else:
    st.warning("No se pudo cargar la lista de choferes.")
