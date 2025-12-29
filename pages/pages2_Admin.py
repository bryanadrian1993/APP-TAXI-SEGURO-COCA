import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import pydeck as pdk  # <--- NUEVA LIBRERÍA PARA MAPAS PRO
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Admin Panel", page_icon="👮‍♂️", layout="wide")

# 🆔 CONEXIÓN
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzgN1j4xiGgqjH842Ui5FwyMNCkH2k73jBd-GeSnn0Ja2ciNI-10RnTajH2GG7xIoCU/exec"
ADMIN_PASSWORD = "admin123"

# --- FUNCIONES ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
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

# --- LOGIN ---
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

# --- PANEL ---
st.sidebar.success("✅ Modo Administrador Activo")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.admin_logged_in = False
    st.rerun()

st.title("👮‍♂️ Centro de Comando - Taxi Seguro")

df_choferes = cargar_datos("CHOFERES")
df_gps = cargar_datos("UBICACIONES")

col1, col2, col3 = st.columns(3)
col1.metric("Total Socios", len(df_choferes) if not df_choferes.empty else 0)
col2.metric("Socios Activos", len(df_choferes[df_choferes['Estado'] == 'LIBRE']) if not df_choferes.empty and 'Estado' in df_choferes.columns else 0)
col3.metric("Ubicaciones GPS", len(df_gps) if not df_gps.empty else 0)

tab1, tab2 = st.tabs(["📋 GESTIÓN", "🗺️ MAPA DE FLOTA"])

with tab1:
    st.subheader("Directorio de Conductores")
    if not df_choferes.empty:
        st.dataframe(df_choferes[['Nombre', 'Apellido', 'Telefono', 'Placa', 'Estado', 'Tipo_Vehiculo', 'Pais']], use_container_width=True)
        st.markdown("---")
        st.subheader("🚫 Zona de Expulsión")
        lista = df_choferes.apply(lambda x: f"{x['Nombre']} {x['Apellido']}", axis=1).tolist()
        borrar = st.selectbox("Eliminar a:", lista)
        if st.button("🗑️ ELIMINAR", type="primary"):
            p = borrar.split(" ", 1)
            if len(p) == 2:
                with st.spinner("Eliminando..."):
                    res = enviar_datos({"accion": "admin_borrar_chofer", "nombre": p[0], "apellido": p[1]})
                    if "ADMIN_BORRADO_OK" in res:
                        st.success("Eliminado")
                        import time
                        time.sleep(1)
                        st.rerun()
                    else: st.error("Error al eliminar")
    else: st.info("Sin datos.")

with tab2:
    st.subheader("📡 Rastreo Satelital")
    if not df_gps.empty:
        df_mapa = df_gps.copy()
        
        # === 1. LIMPIEZA DE COORDENADAS ===
        def limpiar_coordenada(valor):
            try:
                s = str(valor).replace(",", "").replace(".", "")
                num = float(s)
                # Reducimos el número hasta que sea una coordenada lógica (entre -180 y 180)
                while abs(num) > 180: 
                    num = num / 10
                return num
            except:
                return None

        df_mapa['lat'] = df_mapa['Latitud'].apply(limpiar_coordenada)
        df_mapa['lon'] = df_mapa['Longitud'].apply(limpiar_coordenada)
        df_mapa = df_mapa.dropna(subset=['lat', 'lon'])
        
        if not df_mapa.empty:
            # === 2. MAPA AVANZADO (PyDeck) ===
            st.caption("Los puntos rojos son tus taxis en tiempo real. Pasa el mouse para ver quién es.")
            
            view_state = pdk.ViewState(
                latitude=df_mapa['lat'].mean(),
                longitude=df_mapa['lon'].mean(),
                zoom=14,
                pitch=0
            )

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_mapa,
                get_position='[lon, lat]',
                get_color='[255, 0, 0, 200]', # Color Rojo
                get_radius=80, # Tamaño del punto (metros)
                pickable=True
            )

            # Dibujamos el mapa forzando el estilo 'light' (claro/calles)
            st.pydeck_chart(pdk.Deck(
                map_style=None, 
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{Conductor}\nActualizado: {Ultima_Actualizacion}"}
            ))
            
            st.write("Datos técnicos recibidos:")
            st.dataframe(df_gps.tail(5))
        else:
            st.warning("⚠️ Datos GPS inválidos.")
    else:
        st.info("Sin señal GPS.")
