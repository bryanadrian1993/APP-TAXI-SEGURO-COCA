import streamlit as st
import pandas as pd
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

# 🆔 ID DE TU HOJA (ESTO ES LO ÚNICO QUE NECESITAMOS)
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"

# 📍 VARIABLES
LAT_BASE = -0.466657
LON_BASE = -76.989635
NUMERO_ADMIN = "593962384356"
PASSWORD_ADMIN = "admin123"

# --- 2. FUNCIÓN DE CONEXIÓN INFALIBLE (SIN SECRETS) ---
def cargar_datos(hoja):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}"
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error cargando {hoja}: {e}")
        return pd.DataFrame()

# --- 3. FUNCIONES AUXILIARES ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000; }
    .wa-btn { background-color: #25D366 !important; color: white !important; padding: 15px; border-radius: 10px; text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 18px; margin-top: 10px; }
    .precio-box { background-color: #FFF9C4; padding: 20px; border-radius: 10px; border: 2px solid #FBC02D; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

if 'paso' not in st.session_state: st.session_state.paso = 1
if 'datos_pedido' not in st.session_state: st.session_state.datos_pedido = {}

# ==============================================================================
# MENÚ LATERAL
# ==============================================================================
modo = st.sidebar.selectbox("Modo de Uso:", ["🚖 PEDIR TAXI (Cliente)", "👮‍♂️ ADMINISTRACIÓN (Dueño)"])

# === MODO CLIENTE ===
if modo == "🚖 PEDIR TAXI (Cliente)":
    st.title("🚖 PEDIR TAXI")
    
    if st.session_state.paso == 1:
        st.info("📍 Ubicación")
        loc = get_geolocation()
        lat, lon = LAT_BASE, LON_BASE
        gps_activo = False
        mapa = "No detectado"

        if loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            gps_activo = True
            mapa = f"https://www.google.com/maps?q={lat},{lon}"
            st.success("✅ GPS OK")
        
        with st.form("form_viaje"):
            nombre = st.text_input("Nombre:")
            celular = st.text_input("WhatsApp:")
            ref = st.text_input("Referencia:")
            tipo = st.selectbox("Unidad:", ["Taxi 🚖", "Camioneta 🛻"])
            
            if st.form_submit_button("COTIZAR"):
                if not nombre or not ref: st.error("Faltan datos")
                elif not gps_activo: st.warning("⚠️ Esperando GPS...")
                else:
                    dist = calcular_distancia(LAT_BASE, LON_BASE, lat, lon)
                    costo = round(max(1.50, dist * 0.75), 2)
                    st.session_state.datos_pedido = {"nombre": nombre, "celular": celular, "ref": ref, "tipo": tipo, "mapa": mapa, "costo": costo}
                    st.session_state.paso = 2
                    st.rerun()

    elif st.session_state.paso == 2:
        d = st.session_state.datos_pedido
        st.markdown(f'<div class="precio-box"><h2>${d["costo"]}</h2></div>', unsafe_allow_html=True)
        
        if st.button("✅ CONFIRMAR Y PEDIR"):
            # AQUÍ YA NO INTENTAMOS CONECTAR A SHEETS PARA EVITAR ERROR
            # SE ENVÍA DIRECTO POR WHATSAPP
            msg = f"🚖 *NUEVO PEDIDO*\n👤 {d['nombre']}\n📍 {d['ref']}\n💰 ${d['costo']}\n🗺️ {d['mapa']}"
            link = f"https://wa.me/{NUMERO_ADMIN}?text={urllib.parse.quote(msg)}"
            
            st.balloons()
            st.markdown(f'<a href="{link}" class="wa-btn" target="_blank">📲 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
            
            if st.button("🔄 Nuevo Pedido"):
                st.session_state.paso = 1
                st.rerun()

# === MODO ADMIN ===
elif modo == "👮‍♂️ ADMINISTRACIÓN (Dueño)":
    st.header("👮‍♂️ Panel Dueño")
    pwd = st.text_input("Password:", type="password")
    
    if pwd == PASSWORD_ADMIN:
        st.success("Acceso Correcto")
        # Leemos directo del CSV público
        df_choferes = cargar_datos("CHOFERES")
        df_viajes = cargar_datos("VIAJES")
        
        st.subheader("Choferes")
        st.dataframe(df_choferes)
        
        st.subheader("Viajes")
        st.dataframe(df_viajes)
