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
    .step-header { font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; color: #333; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; font-size: 18px; border-radius: 10px; }
    .wa-btn { 
        background-color: #25D366; color: white !important; padding: 15px; border-radius: 10px; 
        text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 20px; margin-top: 20px; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .precio-box { background-color: #E8F5E9; padding: 15px; border-radius: 10px; border: 1px solid #4CAF50; text-align: center; margin-top: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 🆔 DATOS DE CONEXIÓN
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxB7mmTkyTFNoF1Mp19xzdDXqOMDbA8nLemNeDDc1Km3OYs11vF-B1FUpEXGDbgJp3T/exec"
LAT_BASE = -0.466657
LON_BASE = -76.989635

# --- FUNCIONES CEREBRALES ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

def registrar_viaje_en_sheets(datos):
    try:
        params = {
            "accion": "registrar_pedido",
            "cliente": datos['cliente'],
            "telefono_cli": datos['telefono_cli'],
            "referencia": datos['referencia'],
            "conductor": datos['conductor'],
            "telefono_chof": datos['telefono_chof'],
            "mapa": datos['mapa']
        }
        url_final = f"{URL_SCRIPT}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except:
        return "Error"

def obtener_chofer_libre():
    df = cargar_datos("CHOFERES")
    if not df.empty:
        df['Estado'] = df['Estado'].astype(str).str.strip().str.upper()
        if 'Validado' in df.columns:
            df['Validado'] = df['Validado'].astype(str).str.strip().str.upper()
            aptos = df[(df['Estado'] == 'LIBRE') & (df['Validado'] == 'SI')]
            if not aptos.empty:
                elegido = aptos.sample(1).iloc[0]
                nombre = f"{elegido['Nombre']} {elegido['Apellido']}"
                tel = str(elegido['Telefono']).replace(".0", "")
                return nombre, tel
    return None, None

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# --- INTERFAZ ORIGINAL ---
st.markdown('<div class="main-title">🚖 TAXI SEGURO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📍 COCA</div>', unsafe_allow_html=True)
st.divider()

# PASO 1: GPS
st.markdown('<div class="step-header">📡 PASO 1: ACTIVAR UBICACIÓN</div>', unsafe_allow_html=True)
loc = get_geolocation()
if loc:
    lat, lon, gps_activo = loc['coords']['latitude'], loc['coords']['longitude'], True
    mapa_link = f"https://www.google.com/maps?q={lat},{lon}"
    st.success("✅ GPS ACTIVADO: Podemos ver tu ubicación real.")
else:
    lat, lon, gps_activo = LAT_BASE, LON_BASE, False
    mapa_link = "No detectado"
    st.info("📍 Por favor activa tu GPS para localizarte.")

# PASO 2: FORMULARIO
st.markdown('<div class="step-header">📝 PASO 2: DATOS DEL VIAJE</div>', unsafe_allow_html=True)
with st.form("form_pedido"):
    nombre_cli = st.text_input("Nombre del cliente:")
    celular_cli = st.text_input("Número de WhatsApp:")
    ref_cli = st.text_input("Dirección/Referencia exacta (Ej: Casa verde frente al parque):")
    tipo_veh = st.selectbox("Tipo de unidad:", ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"])
    enviar = st.form_submit_button("💰 COTIZAR VIAJE")

if enviar:
    if not nombre_cli or not ref_cli:
        st.error("⚠️ Nombre y Referencia son obligatorios.")
    else:
        dist = calcular_distancia(LAT_BASE, LON_BASE, lat, lon)
        costo = round(max(1.50, dist * 0.75), 2)
        
        with st.spinner("🔄 Buscando unidad y registrando pedido..."):
            nombre_chof, tel_chof = obtener_chofer_libre()
            
            datos_registro = {
                "cliente": nombre_cli,
                "telefono_cli": celular_cli,
                "referencia": ref_cli,
                "conductor": nombre_chof if nombre_chof else "CENTRAL (OCUPADOS)",
                "telefono_chof": tel_chof if tel_chof else "N/A",
                "mapa": mapa_link
            }
            
            # Registro en Excel (Hoja VIAJES)
            res_ex = registrar_viaje_en_sheets(datos_registro)
            
            st.markdown(f'<div class="precio-box">Costo estimado: ${costo}</div>', unsafe_allow_html=True)
            
            if nombre_chof:
                st.balloons()
                st.success(f"✅ ¡Unidad Encontrada! Conductor: **{nombre_chof}**")
                msg = f"🚖 *PEDIDO DE TAXI*\n👤 Cliente: {nombre_cli}\n📱 Cel: {celular_cli}\n📍 Ref: {ref_cli}\n💰 Precio: ${costo}\n🗺️ Mapa: {mapa_link}"
                link_wa = f"https://wa.me/{tel_chof}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)
            else:
                st.error("❌ Todos nuestros conductores están ocupados. Por favor, intente más tarde.")

            if "OK" in res_ex:
                st.toast("✅ Pedido registrado en el sistema.")
