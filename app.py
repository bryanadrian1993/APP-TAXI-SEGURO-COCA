import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math

# --- 1. CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚖", layout="centered")

# 📍 COORDENADAS BASE (Centro del Coca)
LAT_TAXI_BASE = -0.466657
LON_TAXI_BASE = -76.989635

# 📂 ID DE TU CARPETA GOOGLE DRIVE (Ya configurado)
ID_CARPETA_DRIVE = "1spyEiLT-HhKl_fFnfkbMcrzI3_4Kr3dI"

# --- 2. ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000; }
    .wa-btn {
        background-color: #25D366 !important; color: white !important;
        padding: 20px; border-radius: 15px; text-align: center;
        display: block; text-decoration: none; font-weight: bold;
        font-size: 20px; margin-top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .precio-box {
        background-color: #FFF9C4; padding: 20px; border-radius: 10px;
        border: 2px solid #FBC02D; text-align: center; margin-bottom: 20px;
    }
    .precio-titulo { font-size: 18px; color: #555; }
    .precio-valor { font-size: 32px; font-weight: bold; color: #000; }
    .datos-banco {
        background-color: #F3F3F3; padding: 15px; border-radius: 10px;
        border-left: 5px solid #1E88E5; font-size: 14px; margin-bottom: 15px;
    }
    .exito-msg {
        background-color: #E8F5E9; color: #1B5E20; padding: 20px;
        border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE CÁLCULO Y CONEXIÓN ---

def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def obtener_credenciales():
    scope = [
        "https://spreadsheets.google.com/feeds", 
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

def conectar_sheets():
    try:
        creds = obtener_credenciales()
        # Conecta a la hoja de PRUEBAS (Recuerda cambiar esto si pasas a la oficial)
        return gspread.authorize(creds).open("BD_TAXI_PRUEBAS").get_worksheet(0)
    except: return None

def subir_imagen_drive(archivo_obj, nombre_cliente):
    """Sube la imagen a Drive y devuelve el link público"""
    try:
        creds = obtener_credenciales()
        service = build('drive', 'v3', credentials=creds)
        
        # Nombre ordenado por fecha: AAAA-MM-DD_HH-MM_Cliente.jpg
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nombre_archivo = f"{timestamp}_{nombre_cliente}_Pago.jpg"
        
        file_metadata = {
            'name': nombre_archivo,
            'parents': [ID_CARPETA_DRIVE] 
        }
        
        media = MediaIoBaseUpload(archivo_obj, mimetype=archivo_obj.type)
        
        # Subir archivo
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        
        # Dar permiso público para que el taxista pueda ver la foto con el link
        user_permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
        ).execute()
        
        return file.get('webViewLink')
        
    except Exception as e:
        st.error(f"Error subiendo imagen: {e}")
        return None

# --- 4. GESTIÓN DE ESTADOS ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'datos_pedido' not in st.session_state: st.session_state.datos_pedido = {}

# --- 5. INTERFAZ DE USUARIO ---
st.markdown("<h1 style='text-align:center;'>🚖 TAXI SEGURO</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>📍 COCA</h3>", unsafe_allow_html=True)
st.write("---")

# === PASO 1: GPS Y FORMULARIO ===
if st.session_state.paso == 1:
    st.write("🛰️ **PASO 1: ACTIVAR UBICACIÓN**")
    loc = get_geolocation()
    
    lat, lon = LAT_TAXI_BASE, LON_TAXI_BASE
    distancia = 0.0
    gps_activo = False
    mapa_link = "No detectado"

    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        mapa_link = f"https://www.google.com/maps?q={lat},{lon}"
        distancia = calcular_distancia_km(LAT_TAXI_BASE, LON_TAXI_BASE, lat, lon)
        gps_activo = True
        st.success("✅ GPS ACTIVADO")
    else:
        st.warning("⚠️ Esperando señal GPS...")

    with st.form("form_inicial"):
        st.write("📝 **PASO 2: DATOS DEL VIAJE**")
        nombre = st.text_input("Nombre del cliente:")
        celular = st.text_input("Número de WhatsApp:")
        referencia = st.text_input("Referencia exacta:")
        tipo = st.selectbox("Tipo de unidad:", ["Taxi 🚖", "Camioneta 🛻", "Moto 📦"])
        
        if st.form_submit_button("REGISTRAR PEDIDO"):
            if not nombre or not celular or not referencia:
                st.error("❌ Llena todos los campos.")
            elif not gps_activo:
                st.error("⚠️ Activa tu GPS para calcular la tarifa.")
            else:
                costo = round(distancia * 0.75, 2)
                if costo < 1.50: costo = 1.50
                
                st.session_state.datos_pedido = {
                    "nombre": nombre, "celular": celular, "referencia": referencia,
                    "tipo": tipo, "mapa": mapa_link, "distancia": distancia, "costo": costo
                }
                st.session_state.paso = 2
                st.rerun()

# === PASO 2: CONFIRMAR PRECIO ===
elif st.session_state.paso == 2:
    d = st.session_state.datos_pedido
    st.write("💰 **CONFIRMACIÓN DE TARIFA**")
    st.markdown(f"""
    <div class="precio-box">
        <div class="precio-titulo">Costo estimado</div>
        <div class="precio-valor">${d['costo']}</div>
        <small>{round(d['distancia'], 2)} km</small>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    if c1.button("✅ ACEPTAR", use_container_width=True):
        st.session_state.paso = 3
        st.rerun()
    if c2.button("❌ CANCELAR", use_container_width=True):
        st.session_state.paso = 1
        st.rerun()

# === PASO 3: PAGO (CON SUBIDA A DRIVE) ===
elif st.session_state.paso == 3:
    st.write("💳 **MÉTODO DE PAGO**")
    pago = st.radio("Elige:", ("Efectivo", "Transferencia Bancaria", "Código QR DEUNA"))
    
    archivo_subido = None
    if pago == "Transferencia Bancaria":
        st.markdown("""
        <div class="datos-banco">
            <b>🏦 DATOS BANCARIOS:</b><br>
            <b>Banco:</b> PICHINCHA (Ahorros)<br>
            <b>Nº:</b> 2202072013<br>
            <b>Titular:</b> BRYAN ADRIAN CAMPOVERDE JARAMILLO<br>
            <b>CI:</b> 2200377071<br>
            <b>Email:</b> adrian-verdi@outlook.es
        </div>""", unsafe_allow_html=True)
        st.write("📸 **Sube tu comprobante (Foto/Captura):**")
        archivo_subido = st.file_uploader("Cargar imagen", type=["jpg", "png", "jpeg"])

    if st.button("FINALIZAR VIAJE", use_container_width=True):
        st.session_state.datos_pedido['pago'] = pago
        st.session_state.datos_pedido['link_comprobante'] = ""
        
        # Si subió archivo, lo enviamos a Drive
        if archivo_subido:
            with st.spinner("Subiendo comprobante a la nube... (Esto puede tardar unos segundos)"):
                link_drive = subir_imagen_drive(archivo_subido, st.session_state.datos_pedido['nombre'])
                if link_drive:
                    st.session_state.datos_pedido['link_comprobante'] = link_drive
                else:
                    st.warning("No se pudo subir la imagen, pero se registrará el pedido.")
        
        st.session_state.paso = 4
        st.rerun()

# === PASO 4: FIN Y WHATSAPP ===
elif st.session_state.paso == 4:
    d = st.session_state.datos_pedido
    tiempo = math.ceil((d['distancia'] * 2.5) + 3)
    
    # Guardar en Sheets
    hoja = conectar_sheets()
    if hoja:
        try:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            estado = f"PENDIENTE - {d['pago']} - ${d['costo']}"
            if d['link_comprobante']: 
                estado += " (Con Comprobante)"
            # Guardamos todo, incluyendo el link en la última columna
            fila = [fecha, d['nombre'], d['celular'], d['tipo'], d['referencia'], d['mapa'], estado, d['link_comprobante']]
            hoja.append_row(fila)
        except: pass

    st.markdown(f"""
    <div class="exito-msg">
        ✅ PETICIÓN PROCESADA<br>LLEGAREMOS EN {tiempo} MINUTOS APROX.
    </div>""", unsafe_allow_html=True)
    
    # Mensaje WhatsApp
    mensaje = (
        f"🚖 *PEDIDO CONFIRMADO*\n"
        f"👤 {d['nombre']} | 📱 {d['celular']}\n"
        f"💵 Costo: ${d['costo']} ({d['pago']})\n"
        f"🚖 Unidad: {d['tipo']}\n"
        f"🏠 Ref: {d['referencia']}\n"
        f"📍 Mapa: {d['mapa']}"
    )
    
    # Agregar el link de Drive si existe
    if d['link_comprobante']:
        mensaje += f"\n\n📎 *VER COMPROBANTE DE PAGO:*\n{d['link_comprobante']}"

    link_wa = f"https://wa.me/593982443582?text={urllib.parse.quote(mensaje)}"
    st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR AL TAXISTA</a>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 Nuevo Pedido"):
        st.session_state.paso = 1
        st.rerun()
