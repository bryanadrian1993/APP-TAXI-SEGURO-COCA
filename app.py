import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math

# --- 1. CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚖", layout="centered")

# 📍 COORDENADAS BASE (Coca)
LAT_TAXI_BASE = -0.466657
LON_TAXI_BASE = -76.989635

# 📱 NÚMERO DEL TAXISTA (FIJO)
NUMERO_TAXISTA = "593962384356"

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
    .datos-banco {
        background-color: #F3F3F3; padding: 15px; border-radius: 10px;
        border-left: 5px solid #1E88E5; font-size: 14px; margin-bottom: 15px;
    }
    .exito-msg {
        background-color: #E8F5E9; color: #1B5E20; padding: 20px;
        border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px;
    }
    .aviso-foto {
        background-color: #FFF3E0; color: #E65100; padding: 10px;
        border-radius: 5px; font-size: 14px; margin-top: 10px; border: 1px solid #FFB74D;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A SHEETS ---
def conectar_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("BD_TAXI_PRUEBAS").get_worksheet(0)
    except: return None

# --- 4. CÁLCULO DE DISTANCIA ---
def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- 5. GESTIÓN DE ESTADOS ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'datos_pedido' not in st.session_state: st.session_state.datos_pedido = {}

# --- 6. INTERFAZ ---
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
                st.error("⚠️ Activa tu GPS.")
            else:
                costo = round(distancia * 0.75, 2)
                if costo < 1.50: costo = 1.50
                st.session_state.datos_pedido = {
                    "nombre": nombre, "celular": celular, "referencia": referencia,
                    "tipo": tipo, "mapa": mapa_link, "distancia": distancia, "costo": costo
                }
                st.session_state.paso = 2
                st.rerun()

# === PASO 2: CONFIRMAR ===
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

# === PASO 3: PAGO (MODO MANUAL) ===
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
        
        # Mantenemos esto visualmente para que el cliente sepa que debe tener el comprobante
        st.info("💡 Ten lista tu captura de pantalla para enviarla por WhatsApp al conductor.")

    if st.button("FINALIZAR VIAJE", use_container_width=True):
        st.session_state.datos_pedido['pago'] = pago
        st.session_state.paso = 4
        st.rerun()

# === PASO 4: FIN Y WHATSAPP ===
elif st.session_state.paso == 4:
    d = st.session_state.datos_pedido
    tiempo = math.ceil((d['distancia'] * 2.5) + 3)
    
    # Guardar en Sheets (Datos básicos sin link de foto, pues no hay nube)
    hoja = conectar_sheets()
    if hoja:
        try:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            estado = f"PENDIENTE - {d['pago']} - ${d['costo']}"
            fila = [fecha, d['nombre'], d['celular'], d['tipo'], d['referencia'], d['mapa'], estado]
            hoja.append_row(fila)
        except: pass

    st.markdown(f"""
    <div class="exito-msg">
        ✅ PETICIÓN PROCESADA<br>LLEGAREMOS EN {tiempo} MINUTOS APROX.
    </div>""", unsafe_allow_html=True)
    
    # Mensaje WhatsApp Optimizado
    mensaje = (
        f"🚖 *PEDIDO CONFIRMADO*\n"
        f"👤 {d['nombre']} | 📱 {d['celular']}\n"
        f"💵 Costo: ${d['costo']} ({d['pago']})\n"
        f"🚖 Unidad: {d['tipo']}\n"
        f"🏠 Ref: {d['referencia']}\n"
        f"📍 Mapa: {d['mapa']}"
    )
    
    # Instrucción clara si es transferencia
    if d['pago'] == "Transferencia Bancaria":
        mensaje += "\n\n📸 *OJO:* EL CLIENTE ENVIARÁ EL COMPROBANTE DE PAGO EN ESTE CHAT."
        st.markdown("""
        <div class="aviso-foto">
            ⚠️ <b>IMPORTANTE:</b> Al presionar el botón verde se abrirá WhatsApp.<br>
            Por favor, <b>ADJUNTA LA FOTO DEL COMPROBANTE</b> en el chat.
        </div>
        """, unsafe_allow_html=True)

    link_wa = f"https://wa.me/{NUMERO_TAXISTA}?text={urllib.parse.quote(mensaje)}"
    st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR AL TAXISTA</a>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 Nuevo Pedido"):
        st.session_state.paso = 1
        st.rerun()
