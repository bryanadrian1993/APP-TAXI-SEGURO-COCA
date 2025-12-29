import streamlit as st
import pandas as pd
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math
import urllib.request
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

# 🎨 ESTILOS VISUALES ORIGINALES (CSS)
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #000; margin-bottom: 0; }
    .sub-title { font-size: 25px; font-weight: bold; text-align: center; color: #E91E63; margin-top: -10px; margin-bottom: 20px; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; font-size: 18px; border-radius: 10px; }
    .wa-btn { 
        background-color: #25D366; color: white !important; padding: 15px; border-radius: 10px; 
        text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 20px; margin-top: 20px; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .precio-box { background-color: #E8F5E9; padding: 15px; border-radius: 10px; border: 1px solid #4CAF50; text-align: center; margin-top: 10px; }
    .id-box { background-color: #F0F2F6; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; color: #333; margin-top: 5px; border: 1px dashed #999; }
    </style>
""", unsafe_allow_html=True)

# 🆔 DATOS DE CONEXIÓN
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxB7mmTkyTFNoF1Mp19xzdDXqOMDbA8nLemNeDDc1Km3OYs11vF-B1FUpEXGDbgJp3T/exec"
LAT_BASE = -0.466657
LON_BASE = -76.989635

# --- FUNCIONES ---
def registrar_viaje_en_sheets(datos):
    try:
        params = {
            "accion": "registrar_pedido",
            "cliente": datos['cliente'],
            "telefono_cli": datos['telefono_cli'],
            "referencia": datos['referencia'],
            "conductor": datos['conductor'],
            "telefono_chof": datos['telefono_chof'],
            "mapa": datos['mapa'],
            "id_viaje": datos['id_viaje']  # Enviamos el ID generado
        }
        url_f = f"{URL_SCRIPT}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url_f) as res: return res.read().decode('utf-8')
    except: return "Error"

def obtener_chofer_libre():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=CHOFERES"
        df = pd.read_csv(url)
        df['Estado'] = df['Estado'].astype(str).str.strip().str.upper()
        df['Validado'] = df['Validado'].astype(str).str.strip().str.upper()
        aptos = df[(df['Estado'] == 'LIBRE') & (df['Validado'] == 'SI')]
        if not aptos.empty:
            el = aptos.sample(1).iloc[0]
            return f"{el['Nombre']} {el['Apellido']}", str(el['Telefono']).replace(".0", "")
    except: pass
    return None, None

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# --- INTERFAZ ORIGINAL ---
st.markdown('<div class="main-title">🚖 TAXI SEGURO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📍 COCA</div>', unsafe_allow_html=True)

loc = get_geolocation()
lat, lon, gps = (loc['coords']['latitude'], loc['coords']['longitude'], True) if loc else (LAT_BASE, LON_BASE, False)

# Formulario Original
nombre_cli = st.text_input("Nombre del cliente:")
celular_cli = st.text_input("Número de WhatsApp:")
ref_cli = st.text_input("Dirección/Referencia exacta:")
enviar = st.button("💰 COTIZAR VIAJE")

if enviar and nombre_cli and ref_cli:
    costo = round(max(1.50, calcular_distancia(LAT_BASE, LON_BASE, lat, lon) * 0.75), 2)
    mapa = f"https://www.google.com/maps?q={lat},{lon}"
    
    with st.spinner("Procesando..."):
        chof, t_chof = obtener_chofer_libre()
        # Generamos el ID de viaje aquí para mostrarlo y enviarlo
        id_v = f"TX-{random.randint(100, 999)}"
        
        res = registrar_viaje_en_sheets({
            "cliente": n_cli if 'n_cli' in locals() else nombre_cli, 
            "telefono_cli": t_cli if 't_cli' in locals() else celular_cli, 
            "referencia": ref_cli,
            "conductor": chof if chof else "OCUPADOS", 
            "telefono_chof": t_chof if t_chof else "N/A", 
            "mapa": mapa,
            "id_viaje": id_v
        })
        
        st.markdown(f'<div class="precio-box">Total estimado: ${costo}</div>', unsafe_allow_html=True)
        
        if chof:
            st.markdown(f'<div class="id-box">🆔 ID DE VIAJE: {id_v}</div>', unsafe_allow_html=True)
            st.success(f"✅ ¡Unidad Encontrada! Conductor: **{chof}**")
            # Mensaje de WhatsApp con ID incluido
            msg = f"🚖 *PEDIDO DE TAXI*\n🆔 *ID:* {id_v}\n👤 *Cliente:* {nombre_cli}\n📍 *Ref:* {ref_cli}\n💰 *Precio:* ${costo}\n🗺️ *Mapa:* {mapa}"
            st.markdown(f'<a href="https://wa.me/{t_chof}?text={urllib.parse.quote(msg)}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)
        else:
            st.error("❌ Todos nuestros conductores están ocupados.")
