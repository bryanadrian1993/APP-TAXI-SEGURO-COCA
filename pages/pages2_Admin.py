import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Admin Panel", page_icon="👮‍♂️", layout="wide")

# 🆔 CONEXIÓN
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzgN1j4xiGgqjH842Ui5FwyMNCkH2k73jBd-GeSnn0Ja2ciNI-10RnTajH2GG7xIoCU/exec"

# 🔐 CONTRASEÑA MAESTRA
ADMIN_PASSWORD = "admin123"

# --- FUNCIONES ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        # Forzamos la lectura tratando de interpretar números
        df = pd.read_csv(url)
        return df
    except: return pd.DataFrame()

def enviar_datos(datos):
    try:
        params = urllib.parse.urlencode(datos)
        url_final = f"{URL_SCRIPT}?{params}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

# --- LOGIN DE ADMINISTRADOR ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.markdown("<h1 style='text-align: center;'>👮‍♂️ ACCESO RESTRINGIDO</h1>", unsafe_allow_html=True)
    password = st.text_input("Contraseña de Administrador", type="password")
    if st.button("INGRESAR"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("⛔ Acceso Denegado")
    st.stop() 

# --- PANEL DE CONTROL ---
st.sidebar.success("✅ Modo Administrador Activo")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.admin_logged_in = False
    st.rerun()

st.title("👮‍♂️ Centro de Comando - Taxi Seguro")

# CARGAR DATOS
df_choferes = cargar_datos("CHOFERES")
df_gps = cargar_datos("UBICACIONES")

# METRICAS
col1, col2, col3 = st.columns(3)
total_choferes = len(df_choferes) if not df_choferes.empty else 0
choferes_libres = len(df_choferes[df_choferes['Estado'] == 'LIBRE']) if not df_choferes.empty and 'Estado' in df_choferes.columns else 0

col1.metric("Total Socios", total_choferes)
col2.metric("Socios Activos (LIBRE)", choferes_libres)
col3.metric("Ubicaciones GPS", len(df_gps) if not df_gps.empty else 0)

tab1, tab2 = st.tabs(["📋 GESTIÓN DE SOCIOS", "🗺️ MAPA DE FLOTA"])

# --- PESTAÑA 1: GESTIÓN ---
with tab1:
    st.subheader("Directorio de Conductores")
    
    if not df_choferes.empty:
        st.dataframe(df_choferes[['Nombre', 'Apellido', 'Telefono', 'Placa', 'Estado', 'Tipo_Vehiculo', 'Pais']], use_container_width=True)
        
        st.markdown("---")
        st.subheader("🚫 Zona de Expulsión")
        st.warning("Aquí puedes eliminar conductores falsos o que no enviaron documentos.")
        
        lista_nombres = df_choferes.apply(lambda x: f"{x['Nombre']} {x['Apellido']}", axis=1).tolist()
        chofer_a_borrar = st.selectbox("Selecciona al conductor a eliminar:", lista_nombres)
        
        if st.button("🗑️ ELIMINAR CONDUCTOR DEFINITIVAMENTE", type="primary"):
            partes = chofer_a_borrar.split(" ", 1)
            if len(partes) == 2:
                n_borrar = partes[0]
                a_borrar = partes[1]
                
                with st.spinner(f"Eliminando a {chofer_a_borrar}..."):
                    res = enviar_datos({
                        "accion": "admin_borrar_chofer",
                        "nombre": n_borrar,
                        "apellido": a_borrar
                    })
                    
                    if "ADMIN_BORRADO_OK" in res:
                        st.success(f"✅ {chofer_a_borrar} ha sido eliminado del sistema.")
                        st.balloons()
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ No se pudo eliminar. Verifica que el nombre coincida exactamente.")
            else:
                st.error("Error al procesar el nombre.")
    else:
        st.info("No hay conductores registrados aún.")

# --- PESTAÑA 2: MAPA EN VIVO (CORREGIDO) ---
with tab2:
    st.subheader("📡 Rastreo Satelital en Tiempo Real")
    if not df_gps.empty:
        # === CORRECCIÓN DE DATOS ===
        # 1. Copiamos para no dañar el original
        df_mapa = df_gps.copy()
        
        # 2. Forzamos conversión a NÚMEROS (Si falla, pone NaN)
        # Esto arregla el error de "TypeError" si vienen como texto
        df_mapa['Latitud'] = pd.to_numeric(df_mapa['Latitud'], errors='coerce')
        df_mapa['Longitud'] = pd.to_numeric(df_mapa['Longitud'], errors='coerce')
        
        # 3. Eliminamos filas que no tengan coordenadas válidas
        df_mapa = df_mapa.dropna(subset=['Latitud', 'Longitud'])
        
        # 4. Renombrar columnas para el mapa
        df_mapa = df_mapa.rename(columns={"Latitud": "lat", "Longitud": "lon"})
        
        if not df_mapa.empty:
            st.map(df_mapa, zoom=14)
            st.write("Últimas ubicaciones reportadas:")
            st.dataframe(df_gps.tail(10))
        else:
            st.warning("⚠️ Hay datos de GPS, pero el formato de coordenadas no es válido.")
    else:
        st.info("No hay señales GPS activas en este momento.")
