import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_js_eval import get_geolocation
from datetime import datetime, timedelta
import urllib.parse
import math

# --- 1. CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚖", layout="centered")

# 📍 COORDENADAS BASE (Coca) Y DATOS
LAT_TAXI_BASE = -0.466657
LON_TAXI_BASE = -76.989635
NUMERO_ADMIN = "593962384356"   # Tu número (Receptor de pedidos)
PASSWORD_ADMIN = "admin123"     # 🔒 CONTRASEÑA DEL JEFE

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000; }
    .wa-btn {
        background-color: #25D366 !important; color: white !important;
        padding: 15px; border-radius: 10px; text-align: center;
        display: block; text-decoration: none; font-weight: bold;
        font-size: 18px; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .precio-box {
        background-color: #FFF9C4; padding: 20px; border-radius: 10px;
        border: 2px solid #FBC02D; text-align: center; margin-bottom: 20px;
    }
    .exito-msg {
        background-color: #E8F5E9; color: #1B5E20; padding: 20px;
        border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A SHEETS (NUEVA VERSIÓN ESTABLE) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def guardar_pedido(fecha, nombre, celular, tipo, ref, mapa, estado):
    try:
        # Leemos la hoja actual para no borrar nada
        df = conn.read(worksheet="VIAJES", ttl=0)
        # Creamos una nueva fila
        nueva_fila = pd.DataFrame([{
            "Fecha": fecha, "Nombre del cliente": nombre, "Telefono": celular,
            "Tipo": tipo, "Referencia": ref, "Mapa": mapa, "Estado": estado,
            "Conductor Asignado": "", "Telefono Conductor": "", "ID_Viaje": ""
        }])
        # Unimos y guardamos (Esto requiere permisos de escritura en la API)
        # NOTA: Para escritura simple sin configurar API compleja, 
        # app sheet sigue siendo mejor receptor, pero aquí mostramos la interfaz.
        return True
    except:
        return False

# --- CÁLCULO DISTANCIA ---
def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- GESTIÓN DE ESTADOS ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'datos_pedido' not in st.session_state: st.session_state.datos_pedido = {}

# ==============================================================================
# MENÚ PRINCIPAL (SIDEBAR)
# ==============================================================================
modo = st.sidebar.selectbox("Modo de Uso:", ["🚖 PEDIR TAXI (Cliente)", "👮‍♂️ ADMINISTRACIÓN (Dueño)"])

# ==============================================================================
# MODO 1: CLIENTE
# ==============================================================================
if modo == "🚖 PEDIR TAXI (Cliente)":
    st.markdown("<h1 style='text-align:center;'>🚖 TAXI SEGURO</h1>", unsafe_allow_html=True)

    # PASO 1: GPS Y FORMULARIO
    if st.session_state.paso == 1:
        st.info("📍 Activa tu ubicación para calcular la tarifa exacta.")
        try:
            loc = get_geolocation()
        except:
            loc = None
            
        lat, lon = LAT_TAXI_BASE, LON_TAXI_BASE
        distancia = 0.0
        gps_activo = False
        mapa_link = "No detectado"

        if loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            mapa_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            distancia = calcular_distancia_km(LAT_TAXI_BASE, LON_TAXI_BASE, lat, lon)
            gps_activo = True
            st.success("✅ Ubicación Detectada")
        
        with st.form("form_inicial"):
            nombre = st.text_input("Tu Nombre:")
            celular = st.text_input("Tu WhatsApp:")
            referencia = st.text_input("Referencia Exacta:")
            tipo = st.selectbox("Tipo de unidad:", ["Taxi 🚖", "Camioneta 🛻", "Moto 📦"])
            
            if st.form_submit_button("COTIZAR VIAJE", use_container_width=True):
                if not nombre or not celular or not referencia:
                    st.error("❌ Llena todos los campos.")
                elif not gps_activo:
                    st.warning("⚠️ Esperando señal GPS... (Intenta de nuevo)")
                else:
                    costo = round(distancia * 0.75, 2)
                    if costo < 1.50: costo = 1.50
                    st.session_state.datos_pedido = {
                        "nombre": nombre, "celular": celular, "referencia": referencia,
                        "tipo": tipo, "mapa": mapa_link, "distancia": distancia, "costo": costo
                    }
                    st.session_state.paso = 2
                    st.rerun()

    # PASO 2: CONFIRMAR PRECIO
    elif st.session_state.paso == 2:
        d = st.session_state.datos_pedido
        st.write("💰 **CONFIRMACIÓN DE TARIFA**")
        st.markdown(f"""
        <div class="precio-box">
            <div style="font-size:20px;">Costo Estimado</div>
            <div style="font-size:40px; font-weight:bold;">${d['costo']}</div>
            <small>{round(d['distancia'], 2)} km de recorrido</small>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        if c1.button("✅ ACEPTAR VIAJE", use_container_width=True):
            st.session_state.paso = 3
            st.rerun()
        if c2.button("❌ CANCELAR", use_container_width=True):
            st.session_state.paso = 1
            st.rerun()

    # PASO 3: PAGO
    elif st.session_state.paso == 3:
        st.write("💳 **MÉTODO DE PAGO**")
        pago = st.radio("Elige cómo pagar:", ("Efectivo", "Transferencia Bancaria", "Código QR DEUNA"))
        
        if pago != "Efectivo":
            st.info("💡 Al finalizar, deberás enviar la foto del comprobante al WhatsApp.")

        if st.button("SOLICITAR UNIDAD AHORA", use_container_width=True):
            d = st.session_state.datos_pedido
            # Generar Mensaje
            msg = (f"🚖 *NUEVO PEDIDO*\n👤 {d['nombre']}\n📱 {d['celular']}\n"
                   f"📍 {d['referencia']}\n💰 ${d['costo']} ({pago})\n🗺️ {d['mapa']}")
            
            # Link WhatsApp
            link = f"https://wa.me/{NUMERO_ADMIN}?text={urllib.parse.quote(msg)}"
            
            st.balloons()
            st.markdown(f"""
            <div class="exito-msg">✅ ¡LISTO!<br>Toca el botón verde para enviar tu ubicación al operador.</div>
            <br>
            <a href="{link}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Volver al Inicio"):
                st.session_state.paso = 1
                st.rerun()

# ==============================================================================
# MODO 2: ADMINISTRACIÓN (PANEL DUEÑO)
# ==============================================================================
elif modo == "👮‍♂️ ADMINISTRACIÓN (Dueño)":
    st.header("👮‍♂️ Panel de Control")
    pwd = st.text_input("Contraseña:", type="password")

    if pwd == PASSWORD_ADMIN:
        st.success("🔓 Acceso Concedido")
        
        # Leemos datos de Sheets usando la conexión nueva
        try:
            df_choferes = conn.read(worksheet="CHOFERES", ttl=5)
            df_viajes = conn.read(worksheet="VIAJES", ttl=5)
            
            tab1, tab2 = st.tabs(["👥 Choferes", "🚖 Últimos Viajes"])
            
            with tab1:
                st.dataframe(df_choferes)
            
            with tab2:
                st.dataframe(df_viajes.tail(10))
                
        except Exception as e:
            st.error(f"Error cargando datos: {e}")
