import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math

# --- 1. CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚖", layout="centered")

# 🔗 ENLACE DIRECTO A TU HOJA (¡AQUÍ ESTÁ LA MAGIA!)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus/edit"

# 📍 DATOS DE LA BASE
LAT_TAXI_BASE = -0.466657
LON_TAXI_BASE = -76.989635
NUMERO_ADMIN = "593962384356"
PASSWORD_ADMIN = "admin123"

# --- 2. CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. FUNCIONES ---
def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- 4. ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000; }
    .wa-btn { background-color: #25D366 !important; color: white !important; padding: 20px; border-radius: 15px; text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 20px; margin-top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .precio-box { background-color: #FFF9C4; padding: 20px; border-radius: 10px; border: 2px solid #FBC02D; text-align: center; margin-bottom: 20px; }
    .exito-msg { background-color: #E8F5E9; color: #1B5E20; padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

if 'paso' not in st.session_state: st.session_state.paso = 1
if 'datos_pedido' not in st.session_state: st.session_state.datos_pedido = {}

# ==============================================================================
# MENÚ LATERAL
# ==============================================================================
modo = st.sidebar.selectbox("Modo de Uso:", ["🚖 PEDIR TAXI (Cliente)", "👮‍♂️ ADMINISTRACIÓN (Dueño)"])

if modo == "🚖 PEDIR TAXI (Cliente)":
    st.markdown("<h1 style='text-align:center;'>🚖 TAXI SEGURO</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>📍 COCA</h3>", unsafe_allow_html=True)
    st.write("---")

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
                    st.error("⚠️ Tu GPS aún no carga.")
                else:
                    costo = round(distancia * 0.75, 2)
                    if costo < 1.50: costo = 1.50
                    st.session_state.datos_pedido = { "nombre": nombre, "celular": celular, "referencia": referencia, "tipo": tipo, "mapa": mapa_link, "distancia": distancia, "costo": costo }
                    st.session_state.paso = 2
                    st.rerun()

    elif st.session_state.paso == 2:
        d = st.session_state.datos_pedido
        st.write("💰 **CONFIRMACIÓN DE TARIFA**")
        st.markdown(f"""<div class="precio-box"><div class="precio-titulo">Costo estimado</div><div style="font-size: 30px; font-weight: bold;">${d['costo']}</div><small>{round(d['distancia'], 2)} km</small></div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("✅ ACEPTAR", use_container_width=True): st.session_state.paso = 3; st.rerun()
        if c2.button("❌ CANCELAR", use_container_width=True): st.session_state.paso = 1; st.rerun()

    elif st.session_state.paso == 3:
        st.write("💳 **MÉTODO DE PAGO**")
        pago = st.radio("Elige:", ("Efectivo", "Transferencia Bancaria", "Código QR DEUNA"))
        if pago != "Efectivo": st.info("ℹ️ Deberás enviar la foto del comprobante.")
        
        if st.button("FINALIZAR Y PEDIR TAXI", use_container_width=True):
             # AQUÍ USAMOS EL ENLACE DIRECTO
             try: df_check = conn.read(spreadsheet=URL_HOJA, worksheet="VIAJES", ttl=0)
             except: pass
             d = st.session_state.datos_pedido
             msg = (f"🚕 *PEDIDO NUEVO*\n👤 {d['nombre']}\n📱 {d['celular']}\n📍 {d['referencia']}\n💵 ${d['costo']} ({pago})\n🗺️ {d['mapa']}")
             if pago != "Efectivo": msg += "\n\n📸 *ADJUNTO EL COMPROBANTE AQUÍ*"
             link = f"https://wa.me/{NUMERO_ADMIN}?text={urllib.parse.quote(msg)}"
             st.balloons()
             st.markdown('<div class="exito-msg">✅ SOLICITUD PROCESADA</div>', unsafe_allow_html=True)
             st.markdown(f'<br><a href="{link}" class="wa-btn" target="_blank">📲 ENVIAR AL OPERADOR</a>', unsafe_allow_html=True)
             if st.button("🔄 Nuevo Viaje"): st.session_state.paso = 1; st.rerun()

elif modo == "👮‍♂️ ADMINISTRACIÓN (Dueño)":
    st.header("👮‍♂️ Panel de Control")
    pwd = st.text_input("Contraseña:", type="password")
    if pwd == PASSWORD_ADMIN:
        st.success("🔓 Acceso Concedido")
        try:
            # USAMOS EL ENLACE DIRECTO AQUÍ TAMBIÉN
            df_choferes = conn.read(spreadsheet=URL_HOJA, worksheet="CHOFERES", ttl=5)
            df_viajes = conn.read(spreadsheet=URL_HOJA, worksheet="VIAJES", ttl=5)
            st.subheader("Estado de la Flota"); st.dataframe(df_choferes)
            st.subheader("Últimos Viajes"); st.dataframe(df_viajes.tail(10))
        except Exception as e:
            st.error(f"Error de conexión: {e}")
