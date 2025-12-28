import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="TAXI SEGURO - DIAGNOSTICO", page_icon="🔧", layout="centered")

# TUS DATOS FIJOS
LAT_TAXI_BASE = -0.466657
LON_TAXI_BASE = -76.989635
ID_CARPETA_DRIVE = "1spyEiLT-HhKl_fFnfkbMcrzI3_4Kr3dI"
NUMERO_TAXISTA = "593962384356"

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000; }
    .wa-btn {
        background-color: #25D366 !important; color: white !important;
        padding: 20px; border-radius: 15px; text-align: center;
        display: block; text-decoration: none; font-weight: bold;
        font-size: 20px; margin-top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .info-box { background-color: #E3F2FD; padding: 10px; border-radius: 5px; border: 1px solid #2196F3; margin-bottom: 10px; font-size: 12px;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES CON DIAGNÓSTICO ---

def obtener_credenciales():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    return Credentials.from_service_account_info(creds_dict, scopes=scope)

def subir_imagen_drive_con_logs(archivo_obj, nombre_cliente):
    st.info("🔵 1. Iniciando proceso de subida...")
    try:
        creds = obtener_credenciales()
        email_robot = creds.service_account_email
        st.info(f"🔵 2. Robot conectado como: {email_robot}")
        st.info(f"🔵 3. Verificando carpeta ID: {ID_CARPETA_DRIVE}")

        service = build('drive', 'v3', credentials=creds)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nombre_archivo = f"{timestamp}_{nombre_cliente}_Pago.jpg"
        
        file_metadata = {'name': nombre_archivo, 'parents': [ID_CARPETA_DRIVE]}
        media = MediaIoBaseUpload(archivo_obj, mimetype=archivo_obj.type)
        
        st.info("🔵 4. Enviando archivo a Google...")
        file = service.files().create(
            body=file_metadata, media_body=media, fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        st.success(f"✅ 5. Archivo creado con ID: {file_id}")
        
        st.info("🔵 6. Configurando permiso público...")
        service.permissions().create(
            fileId=file_id, body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        link = file.get('webViewLink')
        st.success(f"✅ LISTO. Link generado: {link}")
        return link
        
    except Exception as e:
        st.error(f"❌ ERROR FATAL EN SUBIDA: {str(e)}")
        # Diagnóstico común
        if "404" in str(e):
            st.warning("⚠️ PISTA: Error 404 suele significar que el Robot NO encuentra la carpeta. ¿Seguro que compartiste la carpeta con el correo del paso 2?")
        if "403" in str(e):
            st.warning("⚠️ PISTA: Error 403 es falta de permisos. El robot existe pero no tiene permiso de 'Editor'.")
        return None

def conectar_sheets():
    try:
        creds = obtener_credenciales()
        client = gspread.authorize(creds)
        return client.open("BD_TAXI_PRUEBAS").get_worksheet(0)
    except Exception as e:
        st.error(f"Error Sheets: {e}")
        return None

def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- INTERFAZ ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'datos_pedido' not in st.session_state: st.session_state.datos_pedido = {}

st.markdown("<h1 style='text-align:center;'>🚖 MODO DIAGNÓSTICO</h1>", unsafe_allow_html=True)

# PASO 1
if st.session_state.paso == 1:
    st.write("🛰️ **PASO 1**")
    loc = get_geolocation()
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        distancia = calcular_distancia_km(LAT_TAXI_BASE, LON_TAXI_BASE, lat, lon)
        st.success("GPS OK")
        
        with st.form("f1"):
            nombre = st.text_input("Nombre:")
            celular = st.text_input("Celular:")
            tipo = st.selectbox("Unidad:", ["Taxi 🚖"])
            if st.form_submit_button("REGISTRAR"):
                st.session_state.datos_pedido = {
                    "nombre": nombre, "celular": celular, "tipo": tipo,
                    "distancia": distancia, "costo": 1.50, "referencia": "Prueba", "mapa": "Test"
                }
                st.session_state.paso = 3 # Saltamos directo al pago para probar rápido
                st.rerun()
    else:
        st.warning("Activa GPS")

# PASO 3 (DIRECTO A PRUEBA DE PAGO)
elif st.session_state.paso == 3:
    st.write("🧪 **PRUEBA DE SUBIDA**")
    archivo = st.file_uploader("Sube una foto cualquiera para probar", type=["jpg", "png", "jpeg"])
    
    if st.button("PROBAR SUBIDA"):
        if archivo:
            link = subir_imagen_drive_con_logs(archivo, st.session_state.datos_pedido['nombre'])
            if link:
                st.session_state.datos_pedido['link_comprobante'] = link
                st.session_state.datos_pedido['pago'] = "Transferencia"
                st.session_state.paso = 4
                st.rerun()
        else:
            st.error("Sube un archivo primero.")

# PASO 4
elif st.session_state.paso == 4:
    d = st.session_state.datos_pedido
    st.success("¡Llegamos al final!")
    
    msg = f"PRUEBA EXITOSA.\nLink: {d.get('link_comprobante', 'NO HAY LINK')}"
    link_wa = f"https://wa.me/{NUMERO_TAXISTA}?text={urllib.parse.quote(msg)}"
    st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">ENVIAR WHATSAPP</a>', unsafe_allow_html=True)
    
    if st.button("Reiniciar"):
        st.session_state.paso = 1
        st.rerun()
