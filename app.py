import streamlit as st
import pandas as pd
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import urllib.request
import random
import math

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

# 🆔 CONEXIÓN (NUEVA URL ACTUALIZADA)
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwzOVH8c8f9WEoE4OJOTIccz_EgrOpZ8ySURTVRwi0bnQhFnWVdgfX1W8ivTIu5dFfs/exec"
EMAIL_CONTACTO = "taxi-seguro-world@hotmail.com"
LAT_BASE = -0.466657
LON_BASE = -76.989635

# 🎨 ESTILOS (INTACTOS)
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #000; margin-bottom: 0; }
    .sub-title { font-size: 25px; font-weight: bold; text-align: center; color: #E91E63; margin-top: -10px; margin-bottom: 20px; }
    .step-header { font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; color: #333; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; font-size: 18px; border-radius: 10px; }
    .wa-btn { background-color: #25D366; color: white !important; padding: 15px; border-radius: 10px; text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 20px; margin-top: 20px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }
    .id-badge { background-color: #F0F2F6; padding: 5px 15px; border-radius: 20px; border: 1px solid #CCC; font-weight: bold; color: #555; display: inline-block; margin-bottom: 10px; }
    .footer { text-align: center; color: #888; font-size: 14px; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    .footer a { color: #E91E63; text-decoration: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- FÓRMULA DISTANCIA ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- FUNCIONES ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

def enviar_datos_a_sheets(datos):
    try:
        params = urllib.parse.urlencode(datos)
        url_final = f"{URL_SCRIPT}?{params}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

def obtener_chofer_mas_cercano(lat_cliente, lon_cliente):
    df_choferes = cargar_datos("CHOFERES")
    df_ubicaciones = cargar_datos("UBICACIONES")
    
    if df_choferes.empty or df_ubicaciones.empty: return None, None, None

    if 'Estado' in df_choferes.columns:
        libres = df_choferes[df_choferes['Estado'].astype(str).str.strip().str.upper() == 'LIBRE']
        if libres.empty: return None, None, None
            
        mejor_chofer = None
        menor_distancia = float('inf')
        
        for index, chofer in libres.iterrows():
            nombre_completo = f"{chofer['Nombre']} {chofer['Apellido']}"
            ubi = df_ubicaciones[df_ubicaciones['Conductor'] == nombre_completo]
            if not ubi.empty:
                lat_chof = float(ubi.iloc[-1]['Latitud'])
                lon_chof = float(ubi.iloc[-1]['Longitud'])
                dist = calcular_distancia(lat_cliente, lon_cliente, lat_chof, lon_chof)
                if dist < menor_distancia:
                    menor_distancia = dist
                    mejor_chofer = chofer
        
        if mejor_chofer is not None:
            # Intento de leer la foto (Columna L del Excel)
            # Como pandas lee columnas, buscamos si existe una columna que empiece por http o se llame FOTO
            # En tu script la guardamos en la columna 12 (indice 11).
            foto = ""
            try:
                # Intentamos leer la columna 'FOTO_PENDIENTE' si existe, sino usamos iloc
                if 'FOTO_PENDIENTE' in mejor_chofer:
                    foto = str(mejor_chofer['FOTO_PENDIENTE'])
                else:
                    # Fallback si el header no coincide
                    foto = str(mejor_chofer.iloc[11]) 
            except: pass
            
            return f"{mejor_chofer['Nombre']} {mejor_chofer['Apellido']}", str(mejor_chofer['Telefono']).replace(".0", ""), foto
            
    return None, None, None

# --- INTERFAZ CLIENTE ---
st.markdown('<div class="main-title">🚖 TAXI SEGURO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📍 COCA</div>', unsafe_allow_html=True)
st.sidebar.info("👋 **Conductores:**\nUsen el menú de navegación para ir al Portal de Socios.")
st.divider()

st.markdown('<div class="step-header">📡 PASO 1: ACTIVAR UBICACIÓN</div>', unsafe_allow_html=True)
loc = get_geolocation()
lat_actual, lon_actual = LAT_BASE, LON_BASE
if loc:
    lat_actual = loc['coords']['latitude']
    lon_actual = loc['coords']['longitude']
    mapa = f"https://www.google.com/maps?q={lat_actual},{lon_actual}"
    st.success("✅ GPS ACTIVADO")
else:
    mapa = "No detectado"
    st.info("📍 Por favor activa tu GPS.")

st.markdown('<div class="step-header">📝 PASO 2: DATOS DEL VIAJE</div>', unsafe_allow_html=True)
with st.form("form_pedido"):
    nombre_cli = st.text_input("Tu Nombre:")
    celular_cli = st.text_input("Tu WhatsApp:")
    ref_cli = st.text_input("Referencia / Dirección:")
    tipo_veh = st.selectbox("¿Qué necesitas?", ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"])
    enviar = st.form_submit_button("🚖 SOLICITAR UNIDAD")

if enviar:
    if not nombre_cli or not ref_cli:
        st.error("⚠️ Nombre y Referencia son obligatorios.")
    else:
        tel_limpio = ''.join(filter(str.isdigit, celular_cli))
        if tel_limpio.startswith("0"): tel_limpio = "593" + tel_limpio[1:]
        elif not tel_limpio.startswith("593"): tel_limpio = "593" + tel_limpio
            
        with st.spinner("🔄 Buscando la unidad más cercana..."):
            chof, t_chof, foto_chof = obtener_chofer_mas_cercano(lat_actual, lon_actual)
            id_v = f"TX-{random.randint(1000, 9999)}"
            tipo_solo_texto = tipo_veh.split(" ")[0]
            enviar_datos_a_sheets({"accion": "registrar_pedido", "cliente": nombre_cli, "telefono_cli": tel_limpio, "referencia": ref_cli, "conductor": chof if chof else "OCUPADOS", "telefono_chof": t_chof if t_chof else "N/A", "mapa": mapa, "id_viaje": id_v, "tipo": tipo_solo_texto})
            
            if chof:
                st.balloons()
                st.markdown(f'<div style="text-align:center;"><span class="id-badge">🆔 ID: {id_v}</span></div>', unsafe_allow_html=True)
                
                # --- AQUÍ MOSTRAMOS LA FOTO (NUEVO) ---
                if foto_chof and "http" in foto_chof:
                    st.markdown(f"""
                    <div style="display: flex; justify-content: center; margin-bottom: 15px;">
                        <img src="{foto_chof}" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 4px solid #25D366; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                    </div>
                    """, unsafe_allow_html=True)
                # --------------------------------------
                
                st.success(f"✅ ¡Unidad Encontrada! Conductor: **{chof}**")
                msg = f"🚖 *PEDIDO DE {tipo_solo_texto.upper()}*\n🆔 *ID:* {id_v}\n👤 Cliente: {nombre_cli}\n📱 Cel: {tel_limpio}\n📍 Ref: {ref_cli}\n🗺️ Mapa: {mapa}"
                link_wa = f"https://wa.me/{t_chof}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR UBICACIÓN</a>', unsafe_allow_html=True)
            else: st.error("❌ No hay conductores 'LIBRES' cerca de ti en este momento.")

st.markdown("---")
st.markdown(f"""
    <div class="footer">
        <p>¿Necesitas ayuda o quieres reportar algo?</p>
        <p>📧 Contacto: <a href="mailto:{EMAIL_CONTACTO}" target="_self">{EMAIL_CONTACTO}</a></p>
        <p>© 2025 Taxi Seguro Global</p>
    </div>
""", unsafe_allow_html=True)
