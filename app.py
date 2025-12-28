import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse 

# 1. CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚕", layout="centered")

# 2. ESTILOS VISUALES (IDÉNTICOS AL ORIGINAL)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000; }
    .alerta-gps {
        background-color: #FFEBEE; color: #B71C1C; padding: 15px;
        border-radius: 10px; border: 2px solid #D32F2F; text-align: center; margin-bottom: 15px;
    }
    .exito-gps {
        background-color: #E8F5E9; color: #2E7D32; padding: 15px;
        border-radius: 10px; border: 2px solid #4CAF50; text-align: center; margin-bottom: 15px;
    }
    .wa-btn {
        background-color: #25D366 !important; color: white !important;
        padding: 20px; border-radius: 15px; text-align: center;
        display: block; text-decoration: none; font-weight: bold;
        font-size: 20px; margin-top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN GOOGLE SHEETS (CORREGIDA PARA BD_TAXI_PRUEBAS)
def conectar_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Extraer credenciales de los secrets de Streamlit
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        # CAMBIO: Conecta a la hoja de PRUEBAS
        return gspread.authorize(creds).open("BD_TAXI_PRUEBAS").get_worksheet(0)
    except Exception as e:
        # st.error(f"Error técnico: {e}") # Descomentar solo para ver errores de conexión
        return None

# 4. INTERFAZ PRINCIPAL
st.markdown("<h1 style='text-align:center;'>🚕 TAXI SEGURO</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>📍 COCA</h3>", unsafe_allow_html=True)

# SECCIÓN DE DETECCIÓN DE GPS
st.write("---")
st.write("🛰️ **PASO 1: ACTIVAR UBICACIÓN**")

# Intentamos obtener la ubicación
loc = get_geolocation()

if loc:
    st.markdown('<div class="exito-gps">✅ GPS ACTIVADO: Podemos ver tu ubicación real.</div>', unsafe_allow_html=True)
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    mapa_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
else:
    st.markdown("""
        <div class="alerta-gps">
            <b>⚠️ ATENCIÓN: GPS BLOQUEADO</b><br>
            Tu celular no nos permite ver tu ubicación. Sigue estos pasos:<br>
            1. Toca el <b>CANDADO 🔒</b> arriba junto a la dirección web.<br>
            2. Activa el interruptor de <b>UBICACIÓN</b>.<br>
            3. Recarga esta página.
        </div>
    """, unsafe_allow_html=True)
    mapa_link = "UBICACIÓN MANUAL (GPS Falló)"

# 5. FORMULARIO DE PEDIDO
with st.form("pedido_taxi"):
    st.write("🛰️ **PASO 2: DATOS DEL VIAJE**")
    nombre = st.text_input("Nombre del cliente:")
    celular = st.text_input("Número de WhatsApp:")
    referencia = st.text_input("Dirección/Referencia exacta (Ej: Casa verde frente al parque):")
    tipo = st.selectbox("Tipo de unidad:", ["Taxi 🚕", "Camioneta 🛻", "Moto 📦"])
    
    boton_registro = st.form_submit_button("REGISTRAR PEDIDO")

if boton_registro:
    if not nombre or not celular:
        st.error("❌ Por favor llena tu nombre y celular.")
    else:
        # Guardar en Sheets
        hoja = conectar_sheets()
        if hoja:
            try:
                fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                hoja.append_row([fecha, nombre, celular, tipo, referencia, mapa_link, "PENDIENTE"])
            except: 
                st.error("No se pudo escribir en la hoja. Verifica el permiso del correo de servicio.")

        # MENSAJE DE WHATSAPP PARA EL TAXISTA
        mensaje_texto = (
            f"🚕 *PEDIDO DE UNIDAD*\n"
            f"👤 *Cliente:* {nombre}\n"
            f"📱 *WhatsApp:* {celular}\n"
            f"🚕 *Servicio:* {tipo}\n"
            f"🏠 *Referencia:* {referencia}\n\n"
            f"📍 *UBICACIÓN:* {mapa_link}"
        )
        
        msg_encoded = urllib.parse.quote(mensaje_texto)
        # Se mantiene el número original de tu código
        link_final = f"https://wa.me/593982443582?text={msg_encoded}"
        
        st.success("✅ ¡Datos guardados!")
        st.markdown(f'<a href="{link_final}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)
