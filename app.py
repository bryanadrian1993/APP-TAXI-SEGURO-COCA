import streamlit as st
import pandas as pd
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

# 🎨 ESTILOS VISUALES (CSS)
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
NUMERO_ADMIN = "593962384356"
PASSWORD_ADMIN = "admin123"
LAT_BASE = -0.466657
LON_BASE = -76.989635

# --- FUNCIONES CEREBRALES ---
def cargar_datos(hoja):
    try:
        # Evitamos caché para leer datos actualizados del Excel
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

def obtener_chofer_libre():
    df = cargar_datos("CHOFERES")
    if not df.empty:
        # Limpieza de columnas
        df['Estado'] = df['Estado'].astype(str).str.strip().str.upper()
        
        # Verificamos columna Validado (Columna M)
        if 'Validado' in df.columns:
            df['Validado'] = df['Validado'].astype(str).str.strip().str.upper()
            
            # FILTRO: Debe estar LIBRE y Validado con "SI"
            choferes_aptos = df[(df['Estado'] == 'LIBRE') & (df['Validado'] == 'SI')]
            
            if not choferes_aptos.empty:
                # Elección aleatoria entre los aptos
                elegido = choferes_aptos.sample(1).iloc[0]
                nombre_completo = f"{elegido['Nombre']} {elegido['Apellido']}"
                telefono = str(elegido['Telefono']).replace(".0", "")
                return nombre_completo, telefono
                
    return None, None

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- LÓGICA DE INTERFAZ ---
modo = st.sidebar.selectbox("Menú Principal:", ["🚖 PEDIR TAXI", "👮‍♂️ ADMINISTRADOR"])

if modo == "🚖 PEDIR TAXI":
    st.markdown('<div class="main-title">🚖 TAXI SEGURO</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">📍 COCA</div>', unsafe_allow_html=True)
    st.divider()

    # PASO 1: UBICACIÓN
    st.markdown('<div class="step-header">📡 PASO 1: ACTIVAR UBICACIÓN</div>', unsafe_allow_html=True)
    loc = get_geolocation()
    lat, lon, gps_activo = LAT_BASE, LON_BASE, False
    mapa_link = "No detectado"

    if loc:
        lat, lon, gps_activo = loc['coords']['latitude'], loc['coords']['longitude'], True
        mapa_link = f"https://www.google.com/maps?q={lat},{lon}"
        st.success("✅ GPS ACTIVADO")
    else:
        st.info("📍 Por favor activa tu GPS para localizarte.")

    # PASO 2: FORMULARIO
    st.markdown('<div class="step-header">📝 PASO 2: DATOS DEL VIAJE</div>', unsafe_allow_html=True)
    with st.form("form_pedido"):
        nombre_cli = st.text_input("Nombre del cliente:")
        celular_cli = st.text_input("Número de WhatsApp:")
        ref_cli = st.text_input("Dirección/Referencia exacta:")
        tipo_veh = st.selectbox("Tipo de unidad:", ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"])
        enviar = st.form_submit_button("💰 COTIZAR VIAJE")

    if enviar:
        if not nombre_cli or not ref_cli:
            st.error("⚠️ Nombre y Referencia son obligatorios.")
        elif not gps_activo:
            st.warning("⚠️ Esperando señal de GPS...")
        else:
            # Cálculo de costo
            dist = calcular_distancia(LAT_BASE, LON_BASE, lat, lon)
            costo = round(max(1.50, dist * 0.75), 2)
            
            with st.spinner("🔄 Buscando unidad disponible y validada..."):
                nombre_chof, telefono_chof = obtener_chofer_libre()
                
                # REFORMA: Lógica de asignación restrictiva
                if nombre_chof:
                    # CASO ÉXITO: Hay chofer libre y validado
                    aviso_ws = f"\n🚖 *CONDUCTOR ASIGNADO: {nombre_chof}*"
                    msg = f"🚖 *PEDIDO DE TAXI*\n👤 {nombre_cli}\n📱 {celular_cli}\n📍 {ref_cli}\n💰 Precio: ${costo}\n🗺️ {mapa_link}{aviso_ws}"
                    link_wa = f"https://wa.me/{telefono_chof}?text={urllib.parse.quote(msg)}"
                    
                    st.balloons()
                    st.markdown(f'<div class="precio-box">Total estimado: ${costo}</div>', unsafe_allow_html=True)
                    st.success(f"✅ ¡Unidad Encontrada! Conductor: **{nombre_chof}**")
                    st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)
                else:
                    # CASO FALLO: Nadie libre o validado (No hay botón de WA)
                    st.markdown(f'<div class="precio-box">Total estimado: ${costo}</div>', unsafe_allow_html=True)
                    st.error("❌ **CONDUCTORES OCUPADOS.** En este momento no hay unidades disponibles. Por favor, intente más tarde.")

elif modo == "👮‍♂️ ADMINISTRADOR":
    st.title("👮‍♂️ Panel de Administración")
    p = st.text_input("Clave de Acceso:", type="password")
    if p == PASSWORD_ADMIN:
        st.success("Acceso Correcto")
        st.write("---")
        st.subheader("Socios Conductores en tiempo real")
        st.dataframe(cargar_datos("CHOFERES"), use_container_width=True)
