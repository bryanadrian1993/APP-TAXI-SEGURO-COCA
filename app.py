import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math

# --- 1. CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚖", layout="centered")

# COORDENADAS BASE DEL TAXISTA (CENTRO DEL COCA - Parque Central aprox)
# Esto sirve para calcular la distancia hacia el cliente
LAT_TAXI_BASE = -0.466657
LON_TAXI_BASE = -76.989635

# --- 2. ESTILOS VISUALES (Tus estilos originales) ---
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
    .exito-msg {
        background-color: #E8F5E9; color: #1B5E20; padding: 20px;
        border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE CÁLCULO Y CONEXIÓN ---

# Función matemática para calcular distancia entre dos puntos GPS (Fórmula Haversine)
def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def conectar_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("BD_TAXI_PRUEBAS").get_worksheet(0)
    except: return None

# --- 4. GESTIÓN DE ESTADOS (MEMORIA DE LA APP) ---
# Esto permite navegar entre pantallas sin perder datos
if 'paso' not in st.session_state:
    st.session_state.paso = 1 # 1: Formulario, 2: Confirmar Precio, 3: Pago, 4: Final
if 'datos_pedido' not in st.session_state:
    st.session_state.datos_pedido = {}

# --- 5. INTERFAZ DE USUARIO ---
st.markdown("<h1 style='text-align:center;'>🚖 TAXI SEGURO</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>📍 COCA</h3>", unsafe_allow_html=True)
st.write("---")

# ==========================================
# PANTALLA 1: FORMULARIO Y GPS
# ==========================================
if st.session_state.paso == 1:
    st.write("🛰️ **PASO 1: ACTIVAR UBICACIÓN**")
    
    # Obtener GPS
    loc = get_geolocation()
    
    # Variables por defecto
    lat_cliente = LAT_TAXI_BASE
    lon_cliente = LON_TAXI_BASE
    mapa_link = "No detectado"
    distancia = 0.0
    gps_activo = False

    if loc:
        lat_cliente = loc['coords']['latitude']
        lon_cliente = loc['coords']['longitude']
        mapa_link = f"https://www.google.com/maps?q={lat_cliente},{lon_cliente}"
        # Calcular distancia real desde la base
        distancia = calcular_distancia_km(LAT_TAXI_BASE, LON_TAXI_BASE, lat_cliente, lon_cliente)
        gps_activo = True
        st.success("✅ GPS ACTIVADO: Ubicación detectada.")
    else:
        st.warning("⚠️ Esperando señal GPS... Asegúrate de tener la ubicación activada.")

    with st.form("formulario_inicial"):
        st.write("📝 **PASO 2: DATOS DEL VIAJE**")
        nombre = st.text_input("Nombre del cliente:")
        celular = st.text_input("Número de WhatsApp:")
        referencia = st.text_input("Referencia exacta:")
        tipo = st.selectbox("Tipo de unidad:", ["Taxi 🚖", "Camioneta 🛻", "Moto 📦"])
        
        enviar = st.form_submit_button("REGISTRAR PEDIDO")

        if enviar:
            if not nombre or not celular or not referencia:
                st.error("❌ Por favor llena todos los campos.")
            elif not gps_activo:
                st.error("⚠️ Necesitamos tu GPS para calcular el costo. Actívalo y recarga.")
            else:
                # CÁLCULO DEL COSTO
                costo_calculado = round(distancia * 0.75, 2)
                # Tarifa mínima de $1.50 (opcional, para evitar viajes de 10 centavos)
                if costo_calculado < 1.50: costo_calculado = 1.50
                
                # Guardar datos en memoria
                st.session_state.datos_pedido = {
                    "nombre": nombre,
                    "celular": celular,
                    "referencia": referencia,
                    "tipo": tipo,
                    "lat": lat_cliente,
                    "lon": lon_cliente,
                    "mapa": mapa_link,
                    "distancia": distancia,
                    "costo": costo_calculado
                }
                # Pasar al siguiente paso
                st.session_state.paso = 2
                st.rerun()

# ==========================================
# PANTALLA 2: CONFIRMACIÓN DE COSTO
# ==========================================
elif st.session_state.paso == 2:
    datos = st.session_state.datos_pedido
    st.write("💰 **CONFIRMACIÓN DE TARIFA**")
    
    st.markdown(f"""
    <div class="precio-box">
        <div class="precio-titulo">Costo estimado del viaje</div>
        <div class="precio-valor">${datos['costo']}</div>
        <small>Distancia aprox: {round(datos['distancia'], 2)} km</small>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ ACEPTAR", use_container_width=True):
            st.session_state.paso = 3
            st.rerun()
    with col2:
        if st.button("❌ CANCELAR", use_container_width=True):
            st.session_state.paso = 1
            st.rerun()

# ==========================================
# PANTALLA 3: MÉTODO DE PAGO
# ==========================================
elif st.session_state.paso == 3:
    st.write("💳 **SELECCIONE MÉTODO DE PAGO**")
    
    opcion_pago = st.radio(
        "¿Cómo desea pagar?",
        ("Efectivo (Pagar al conductor)", "Transferencia Bancaria", "Código QR DEUNA")
    )
    
    if st.button("FINALIZAR Y PEDIR TAXI", use_container_width=True):
        # Guardar la elección de pago
        st.session_state.datos_pedido['pago'] = opcion_pago
        st.session_state.paso = 4
        st.rerun()

# ==========================================
# PANTALLA 4: PROCESAMIENTO FINAL Y WHATSAPP
# ==========================================
elif st.session_state.paso == 4:
    d = st.session_state.datos_pedido
    
    # 1. CÁLCULO DE TIEMPO DE LLEGADA
    # Fórmula estimada: (Km * 2.5 min) + 3 min de base por tráfico
    minutos_estimados = math.ceil((d['distancia'] * 2.5) + 3)
    
    # 2. GUARDAR EN GOOGLE SHEETS
    hoja = conectar_sheets()
    if hoja:
        try:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Orden columnas: Fecha, Nombre, Celular, Tipo, Ref, Mapa, ESTADO (incluye pago y costo)
            estado_info = f"PENDIENTE - {d['pago']} - ${d['costo']}"
            hoja.append_row([fecha, d['nombre'], d['celular'], d['tipo'], d['referencia'], d['mapa'], estado_info])
        except:
            pass # Si falla sheet, sigue mostrando el mensaje al usuario
    
    # 3. MENSAJE EN PANTALLA
    st.markdown(f"""
    <div class="exito-msg">
        SU PETICIÓN HA SIDO PROCESADA.<br>
        EL VEHICULO LLEGARÁ APROXIMADAMENTE EN {minutos_estimados} MINUTOS.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.info(f"Forma de pago seleccionada: **{d['pago']}**")
    
    # 4. BOTÓN DE WHATSAPP
    mensaje_wa = (
        f"🚖 *NUEVO PEDIDO CONFIRMADO*\n"
        f"👤 *Cliente:* {d['nombre']}\n"
        f"📱 *Tel:* {d['celular']}\n"
        f"💵 *Costo:* ${d['costo']}\n"
        f"💳 *Pago:* {d['pago']}\n"
        f"🚖 *Unidad:* {d['tipo']}\n"
        f"🏠 *Ref:* {d['referencia']}\n"
        f"📍 *Mapa:* {d['mapa']}"
    )
    
    msg_encoded = urllib.parse.quote(mensaje_wa)
    # TU NÚMERO DE CONDUCTOR
    link_final = f"https://wa.me/593962384356?text={msg_encoded}"
    
    st.markdown(f'<a href="{link_final}" class="wa-btn" target="_blank">📲 ENVIAR CONFIRMACIÓN AL TAXISTA</a>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 Hacer otro pedido"):
        st.session_state.paso = 1
        st.session_state.datos_pedido = {}
        st.rerun()
