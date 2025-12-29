import streamlit as st
import pandas as pd
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import urllib.request
import random
import math
import re

# --- ⚙️ CONFIGURACIÓN (MANTENIDA EXACTAMENTE IGUAL) ---
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwzOVH8c8f9WEoE4OJOTIccz_EgrOpZ8ySURTVRwi0bnQhFnWVdgfX1W8ivTIu5dFfs/exec"
EMAIL_CONTACTO = "taxi-seguro-world@hotmail.com"

LAT_BASE = -0.466657
LON_BASE = -76.989635

# 🎨 ESTILOS CSS (TUS ESTILOS ORIGINALES SIN TOCAR)
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #000; margin-bottom: 0; }
    .sub-title { font-size: 25px; font-weight: bold; text-align: center; color: #E91E63; margin-top: -10px; margin-bottom: 20px; }
    .step-header { font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; color: #333; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; font-size: 18px; border-radius: 10px; }
    .id-badge { background-color: #F0F2F6; padding: 5px 15px; border-radius: 20px; border: 1px solid #CCC; font-weight: bold; color: #555; display: inline-block; margin-bottom: 10px; }
    .footer { text-align: center; color: #888; font-size: 14px; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    .footer a { color: #E91E63; text-decoration: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 📏 LÓGICA DE DISTANCIA (TU FÓRMULA ORIGINAL) ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- 📥 CARGA DE DATOS (CON LIMPIEZA PARA EVITAR EL KEYERROR) ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        df = pd.read_csv(url)
        # ESTO EVITA EL ERROR: Borra espacios invisibles en los nombres de las columnas
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

def enviar_datos_a_sheets(datos):
    try:
        params = urllib.parse.urlencode(datos)
        url_final = f"{URL_SCRIPT}?{params}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

def formatear_internacional(prefijo, numero):
    if not numero: return ""
    n = ''.join(filter(str.isdigit, str(numero).split(".")[0].strip()))
    p = str(prefijo).split(" ")[0].replace("+", "").strip()
    if n.startswith(p): return n 
    if n.startswith("0"): n = n[1:]
    return p + n

# --- 🔍 ASIGNACIÓN POR DISTANCIA Y TIPO DE VEHÍCULO ---
def obtener_chofer_mas_cercano(lat_cliente, lon_cliente, tipo_solicitado):
    df_choferes = cargar_datos("CHOFERES") #
    df_ubicaciones = cargar_datos("UBICACIONES")
    if df_choferes.empty or df_ubicaciones.empty: return None, None, None
    
    # Filtramos por tipo solicitado (ej: de "Taxi 🚖" a "Taxi")
    tipo_filtro = tipo_solicitado.split(" ")[0].strip().upper()
    
    libres = df_choferes[
        (df_choferes['Estado'].astype(str).str.strip().str.upper() == 'LIBRE') & 
        (df_choferes['Tipo_Vehiculo'].astype(str).str.upper().str.contains(tipo_filtro))
    ]
    
    if libres.empty: return None, None, None
    
    mejor_chofer, menor_distancia = None, float('inf')
    for index, chofer in libres.iterrows():
        nombre_completo = f"{chofer['Nombre']} {chofer['Apellido']}"
        ubi = df_ubicaciones[df_ubicaciones['Conductor'] == nombre_completo]
        if not ubi.empty:
            lat_chof, lon_chof = float(ubi.iloc[-1]['Latitud']), float(ubi.iloc[-1]['Longitud'])
            dist = calcular_distancia(lat_cliente, lon_cliente, lat_chof, lon_chof)
            if dist < menor_distancia:
                menor_distancia, mejor_chofer = dist, chofer
                
    if mejor_chofer is not None:
        telf = ''.join(filter(str.isdigit, str(mejor_chofer['Telefono'])))
        if (len(telf) == 9 or len(telf) == 10) and telf.startswith("0"): telf = "593" + telf[1:]
        foto = str(mejor_chofer['Foto_Perfil']) if 'Foto_Perfil' in mejor_chofer else ""
        return f"{mejor_chofer['Nombre']} {mejor_chofer['Apellido']}", telf, foto
    return None, None, None

# --- 📱 INTERFAZ CLIENTE (TUS PASOS 1 Y 2) ---
st.markdown('<div class="main-title">🚖 TAXI SEGURO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🌎 SERVICIO GLOBAL</div>', unsafe_allow_html=True)
st.sidebar.info("👋 **Conductores:**\nUsen el menú de navegación para ir al Portal de Socios.")
st.divider()

st.markdown('<div class="step-header">📡 PASO 1: ACTIVAR UBICACIÓN</div>', unsafe_allow_html=True)
loc = get_geolocation()
lat_actual, lon_actual = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (LAT_BASE, LON_BASE)
if loc: st.success("✅ GPS ACTIVADO")
else: st.info("📍 Por favor activa tu GPS.")

st.markdown('<div class="step-header">📝 PASO 2: DATOS DEL VIAJE</div>', unsafe_allow_html=True)
with st.form("form_pedido"):
    nombre_cli = st.text_input("Tu Nombre:")
    st.write("Tu Número de WhatsApp:")
    col_pref, col_num = st.columns([1.5, 3])
    
    prefijo_pais = col_pref.selectbox("País", [
        "+593 (Ecuador)", "+57 (Colombia)", "+51 (Perú)", "+1 (USA/Canada)", 
        "+34 (España)", "+44 (UK)", "+55 (Brasil)", "+33 (Francia)", 
        "+39 (Italia)", "+49 (Alemania)", "+86 (China)", "+81 (Japón)", "+7 (Rusia)"
    ])
    celular_cli = col_num.text_input("Número (Sin el código)")
    
    ref_cli = st.text_input("Referencia / Dirección:")
    tipo_veh = st.selectbox("¿Qué necesitas?", ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"])
    enviar = st.form_submit_button("🚖 SOLICITAR UNIDAD")

if enviar:
    if not nombre_cli or not ref_cli or not celular_cli:
        st.error("⚠️ Nombre, Teléfono y Referencia son obligatorios.")
    else:
        tel_final_cli = formatear_internacional(prefijo_pais, celular_cli)
        with st.spinner("🔄 Buscando la unidad más cercana..."):
            # Aquí ahora pasamos el 'tipo_veh' para filtrar correctamente
            chof, t_chof, foto_chof = obtener_chofer_mas_cercano(lat_actual, lon_actual, tipo_veh)
            id_v = f"TX-{random.randint(1000, 9999)}"
            mapa_link = f"http://maps.google.com/maps?q={lat_actual},{lon_actual}"
            
            enviar_datos_a_sheets({
                "accion": "registrar_pedido", "cliente": nombre_cli, "telefono_cli": tel_final_cli, 
                "referencia": ref_cli, "conductor": chof if chof else "OCUPADOS", 
                "mapa": mapa_link, "id_viaje": id_v
            })
            
            if chof:
                st.balloons()
                st.markdown(f'<div style="text-align:center;"><span class="id-badge">🆔 ID: {id_v}</span></div>', unsafe_allow_html=True)
                
                # REPARADOR DE FOTO DE DRIVE (TU PEDIDO)
                if foto_chof and "http" in foto_chof:
                    match_foto = re.search(r'[-\w]{25,}', foto_chof)
                    if match_foto:
                        id_foto = match_foto.group()
                        url_foto_final = f"https://lh3.googleusercontent.com/u/0/d/{id_foto}"
                        st.markdown(f'<div style="text-align:center; margin-bottom:15px;"><img src="{url_foto_final}" style="width:130px;height:130px;border-radius:50%;object-fit:cover;border:4px solid #25D366;box-shadow: 0 4px 8px rgba(0,0,0,0.2);"></div>', unsafe_allow_html=True)

                st.success(f"✅ ¡Unidad Encontrada! Conductor: **{chof}**")
                
                # MENSAJE DE WHATSAPP (TU ESTRUCTURA ORIGINAL)
                msg = f"🚖 *PEDIDO*\n🆔 *ID:* {id_v}\n👤 Cliente: {nombre_cli}\n📍 Ref: {ref_cli}\n🗺️ Mapa: {mapa_link}"
                link_wa = f"https://api.whatsapp.com/send?phone={t_chof}&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link_wa}" target="_blank" style="background-color:#25D366;color:white;padding:15px;text-align:center;display:block;text-decoration:none;font-weight:bold;font-size:20px;border-radius:10px;">📲 ENVIAR UBICACIÓN</a>', unsafe_allow_html=True)
            else: st.error("❌ No hay conductores de este tipo 'LIBRES' cerca de ti.")

# --- 🏁 FOOTER ---
st.markdown(f'<div class="footer"><p>¿Necesitas ayuda?</p><p>📧 <a href="mailto:{EMAIL_CONTACTO}">{EMAIL_CONTACTO}</a></p><p>© 2025 Taxi Seguro Global</p></div>', unsafe_allow_html=True)
