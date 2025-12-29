import streamlit as st
import pandas as pd
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import urllib.request
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

# 🎨 ESTILOS VISUALES ORIGINALES (CSS) - INTACTOS
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #000; margin-bottom: 0; }
    .sub-title { font-size: 25px; font-weight: bold; text-align: center; color: #E91E63; margin-top: -10px; margin-bottom: 20px; }
    .step-header { font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; color: #333; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; font-size: 18px; border-radius: 10px; }
    .wa-btn { 
        background-color: #25D366; color: white !important; padding: 15px; border-radius: 10px; 
        text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 20px; margin-top: 20px; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .id-badge { background-color: #F0F2F6; padding: 5px 15px; border-radius: 20px; border: 1px solid #CCC; font-weight: bold; color: #555; display: inline-block; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 🆔 DATOS DE CONEXIÓN (TU NUEVO SCRIPT)
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzJcAE1b_GcXEUxdWgEDgZu6Kc7NxE2Ya9YGM-1Kf34O3Z_16hDDLXo242wRNhcTRuB/exec"
LAT_BASE = -0.466657
LON_BASE = -76.989635

# --- FUNCIONES ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

def registrar_viaje_en_sheets(datos):
    try:
        url_final = f"{URL_SCRIPT}?{urllib.parse.urlencode(datos)}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except: return "Error"

def obtener_chofer_libre():
    df = cargar_datos("CHOFERES")
    if not df.empty:
        df['Estado'] = df['Estado'].astype(str).str.strip().str.upper()
        df['Validado'] = df['Validado'].astype(str).str.strip().str.upper() if 'Validado' in df.columns else 'SI'
        aptos = df[(df['Estado'] == 'LIBRE') & (df['Validado'] == 'SI')]
        if not aptos.empty:
            el = aptos.sample(1).iloc[0]
            return f"{el['Nombre']} {el['Apellido']}", str(el['Telefono']).replace(".0", "")
    return None, None

# --- INTERFAZ ORIGINAL (Paso a Paso) ---
st.markdown('<div class="main-title">🚖 TAXI SEGURO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📍 COCA</div>', unsafe_allow_html=True)
st.divider()

st.markdown('<div class="step-header">📡 PASO 1: ACTIVAR UBICACIÓN</div>', unsafe_allow_html=True)
loc = get_geolocation()
if loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    mapa = f"https://www.google.com/maps?q={lat},{lon}"
    st.success("✅ GPS ACTIVADO: Podemos ver tu ubicación real.")
else:
    lat, lon = LAT_BASE, LON_BASE
    mapa = "No detectado"
    st.info("📍 Por favor activa tu GPS para localizarte.")

st.markdown('<div class="step-header">📝 PASO 2: DATOS DEL VIAJE</div>', unsafe_allow_html=True)
with st.form("form_pedido"):
    nombre_cli = st.text_input("Nombre del cliente:")
    celular_cli = st.text_input("Número de WhatsApp:")
    ref_cli = st.text_input("Dirección/Referencia exacta:")
    tipo_veh = st.selectbox("Tipo de unidad:", ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"])
    enviar = st.form_submit_button("🚖 SOLICITAR UNIDAD")

if enviar:
    if not nombre_cli or not ref_cli:
        st.error("⚠️ Nombre y Referencia son obligatorios.")
    else:
        tel_limpio = ''.join(filter(str.isdigit, celular_cli))
        if tel_limpio.startswith("0"): tel_limpio = "593" + tel_limpio[1:]
        elif not tel_limpio.startswith("593"): tel_limpio = "593" + tel_limpio
            
        with st.spinner("🔄 Procesando pedido..."):
            chof, t_chof = obtener_chofer_libre()
            id_v = f"TX-{random.randint(1000, 9999)}"
            tipo_solo_texto = tipo_veh.split(" ")[0]

            registrar_viaje_en_sheets({
                "accion": "registrar_pedido", "cliente": nombre_cli, "telefono_cli": tel_limpio, 
                "referencia": ref_cli, "conductor": chof if chof else "OCUPADOS", 
                "telefono_chof": t_chof if t_chof else "N/A", "mapa": mapa, "id_viaje": id_v,
                "tipo": tipo_solo_texto
            })
            
            if chof:
                st.balloons()
                st.markdown(f'<div style="text-align:center;"><span class="id-badge">🆔 ID DE VIAJE: {id_v}</span></div>', unsafe_allow_html=True)
                st.success(f"✅ ¡Unidad Encontrada! Conductor: **{chof}**")
                
                tipo_msg = tipo_solo_texto.upper()
                msg = f"🚖 *PEDIDO DE {tipo_msg}*\n🆔 *ID:* {id_v}\n👤 Cliente: {nombre_cli}\n📱 Cel: {tel_limpio}\n📍 Ref: {ref_cli}\n🗺️ Mapa: {mapa}"
                link_wa = f"https://wa.me/{t_chof}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)
            else:
                st.error("❌ Conductores ocupados.")
