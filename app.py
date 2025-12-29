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

# 🆔 DATOS DE CONEXIÓN
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxB7mmTkyTFNoF1Mp19xzdDXqOMDbA8nLemNeDDc1Km3OYs11vF-B1FUpEXGDbgJp3T/exec"
LAT_BASE = -0.466657
LON_BASE = -76.989635

# 🎨 ESTILOS VISUALES ORIGINALES
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #000; margin-bottom: 0; }
    .sub-title { font-size: 25px; font-weight: bold; text-align: center; color: #E91E63; margin-top: -10px; margin-bottom: 20px; }
    .step-header { font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; color: #333; }
    .wa-btn { 
        background-color: #25D366; color: white !important; padding: 15px; border-radius: 10px; 
        text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 20px; margin-top: 20px; 
    }
    .precio-box { background-color: #E8F5E9; padding: 15px; border-radius: 10px; border: 1px solid #4CAF50; text-align: center; margin-top: 10px; }
    .id-box { background-color: #FFF3E0; padding: 5px; border-radius: 5px; border: 1px solid #FF9800; font-weight: bold; color: #E65100; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
def registrar_viaje_en_sheets(datos):
    try:
        # Generamos el ID aquí para mostrarlo en pantalla y enviarlo al Excel
        id_viaje = f"TX-{random.randint(100, 999)}"
        params = {
            "accion": "registrar_pedido",
            "cliente": datos['cliente'],
            "telefono_cli": datos['telefono_cli'],
            "referencia": datos['referencia'],
            "conductor": datos['conductor'],
            "telefono_chof": datos['telefono_chof'],
            "mapa": datos['mapa'],
            "id_viaje": id_viaje # Enviamos el ID generado
        }
        url_final = f"{URL_SCRIPT}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url_final) as response:
            res_txt = response.read().decode('utf-8')
            return res_txt, id_viaje
    except:
        return "Error", "N/A"

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

# --- INTERFAZ ---
st.markdown('<div class="main-title">🚖 TAXI SEGURO</div><div class="sub-title">📍 COCA</div>', unsafe_allow_html=True)
loc = get_geolocation()
lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (LAT_BASE, LON_BASE)
mapa_link = f"https://www.google.com/maps?q={lat},{lon}"

with st.container():
    nombre_cli = st.text_input("Nombre del cliente:")
    celular_cli = st.text_input("Número de WhatsApp:")
    ref_cli = st.text_input("Dirección/Referencia exacta:")
    enviar = st.button("💰 COTIZAR VIAJE")

if enviar and nombre_cli and ref_cli:
    with st.spinner("🔄 Procesando viaje..."):
        nombre_chof, tel_chof = obtener_chofer_libre()
        
        # Registro y obtención del ID
        res_ex, id_viaje_generado = registrar_viaje_en_sheets({
            "cliente": nombre_cli, "telefono_cli": celular_cli, "referencia": ref_cli,
            "conductor": nombre_chof if nombre_chof else "CENTRAL",
            "telefono_chof": tel_chof if tel_chof else "N/A", "mapa": mapa_link
        })
        
        st.markdown(f'<div class="precio-box">Total estimado: $19.41</div>', unsafe_allow_html=True)
        
        if nombre_chof:
            st.balloons()
            # Muestra el ID de viaje en pantalla
            st.markdown(f'<div class="id-box">🆔 ID DE VIAJE: {id_viaje_generado}</div>', unsafe_allow_html=True)
            st.success(f"✅ ¡Unidad Encontrada! Conductor: **{nombre_chof}**")
            
            # Mensaje de WhatsApp incluyendo el ID de viaje
            msg = f"🚖 *PEDIDO DE TAXI*\n🆔 *ID:* {id_viaje_generado}\n👤 *Cliente:* {nombre_cli}\n📍 *Ref:* {ref_cli}\n💰 *Precio:* $19.41\n🗺️ *Mapa:* {mapa_link}"
            
            link_wa = f"https://wa.me/{tel_chof}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)
        else:
            st.error("❌ Conductores ocupados.")
