import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

# 🔗 ENLACE DIRECTO (Esta es la clave para que no falle)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus/edit"

# 📍 DATOS
LAT_BASE = -0.466657
LON_BASE = -76.989635
NUMERO_ADMIN = "593962384356"
PASSWORD_ADMIN = "admin123"

# --- 2. CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. FUNCIONES Y ESTILOS ---
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
# MENÚ
# ==============================================================================
modo = st.sidebar.selectbox("Modo de Uso:", ["🚖 PEDIR TAXI (Cliente)", "👮‍♂️ ADMINISTRACIÓN (Dueño)"])

# === CLIENTE ===
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
            # INTENTO DE GUARDAR (Ignora si falla, prioriza WhatsApp)
            try: conn.read(spreadsheet=URL_HOJA, worksheet="VIAJES", ttl=0)
            except: pass
            
            msg = f"🚖 *NUEVO PEDIDO*\n👤 {d['nombre']}\n📍 {d['ref']}\n💰 ${d['costo']}\n🗺️ {d['mapa']}"
            link = f"https://wa.me/{NUMERO_ADMIN}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link}" class="wa-btn" target="_blank">📲 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
            if st.button("🔄 Inicio"): st.session_state.paso = 1; st.rerun()

# === ADMIN ===
elif modo == "👮‍♂️ ADMINISTRACIÓN (Dueño)":
    st.header("👮‍♂️ Panel Dueño")
    if st.text_input("Password:", type="password") == PASSWORD_ADMIN:
        try:
            # AQUÍ USAMOS EL ENLACE DIRECTO
            df_v = conn.read(spreadsheet=URL_HOJA, worksheet="VIAJES", ttl=0)
            df_c = conn.read(spreadsheet=URL_HOJA, worksheet="CHOFERES", ttl=0)
            st.dataframe(df_v.tail(5))
            st.dataframe(df_c)
        except Exception as e:
            st.error(f"Error: {e}")
