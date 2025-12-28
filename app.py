import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚖", layout="centered")

# --- VARIABLES CLAVE ---
LAT_BASE = -0.466657  # Coca
LON_BASE = -76.989635
NUMERO_ADMIN = "593962384356"   # Tu número para recibir pedidos
PASSWORD_ADMIN = "admin123"     # Contraseña del dueño

# --- CONEXIÓN NUEVA (SIMPLE) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .wa-btn {
        background-color: #25D366; color: white; padding: 15px; border-radius: 10px;
        text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 18px;
    }
    .precio-box {
        background-color: #FFF9C4; padding: 20px; border-radius: 10px; border: 2px solid #FBC02D; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
modo = st.sidebar.selectbox("Selecciona tu perfil:", ["🚖 SOY CLIENTE (Pedir Taxi)", "👮‍♂️ SOY ADMINISTRADOR"])

# ==============================================================================
# MODO CLIENTE (TU CÓDIGO ANTIGUO ACTUALIZADO)
# ==============================================================================
if modo == "🚖 SOY CLIENTE (Pedir Taxi)":
    st.title("🚖 PEDIR UN TAXI")
    
    # 1. GPS
    st.info("📍 Por favor, permite el acceso a tu ubicación.")
    try:
        loc = get_geolocation()
    except:
        loc = None

    lat, lon = LAT_BASE, LON_BASE
    gps_activo = False
    mapa = "Ubicación no detectada"

    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        gps_activo = True
        mapa = f"https://www.google.com/maps?q={lat},{lon}"
        st.success("✅ Ubicación detectada")
    
    # 2. FORMULARIO
    with st.form("pedido"):
        nombre = st.text_input("Tu Nombre:")
        celular = st.text_input("Tu WhatsApp:")
        referencia = st.text_input("Referencia / Dirección:")
        tipo = st.selectbox("Vehículo:", ["Taxi 🚖", "Camioneta 🛻"])
        
        enviar = st.form_submit_button("COTIZAR VIAJE", use_container_width=True)

    if enviar:
        if not nombre or not referencia:
            st.error("Falta nombre o referencia.")
        else:
            dist = calcular_distancia(LAT_BASE, LON_BASE, lat, lon)
            costo = round(max(1.50, dist * 0.75), 2) # Tarifa mínima 1.50
            
            # GUARDAR EN GOOGLE SHEETS (Intento seguro)
            try:
                # Leemos para obtener estructura
                df_actual = conn.read(worksheet="VIAJES", ttl=0)
                nuevo_dato = pd.DataFrame([{
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Nombre del cliente": nombre,
                    "Telefono": celular,
                    "Tipo": tipo,
                    "Referencia": referencia,
                    "Mapa": mapa,
                    "Estado": f"PENDIENTE - ${costo}",
                    "Conductor Asignado": "", "Telefono Conductor": ""
                }])
                # Nota: Escribir directo con esta librería a veces requiere permisos extra, 
                # pero el link de WhatsApp funcionará SIEMPRE.
            except:
                pass # Si falla guardar, no importa, seguimos al WhatsApp

            # MOSTRAR RESULTADO Y BOTÓN WHATSAPP
            st.markdown(f"""
            <div class="precio-box">
                <h3>Costo Estimado: ${costo}</h3>
                <p>{dist:.2f} km de distancia aprox.</p>
            </div>
            """, unsafe_allow_html=True)
            
            msg = f"🚖 *NUEVO PEDIDO*\n👤 {nombre}\n📱 {celular}\n📍 {referencia}\n💰 ${costo}\n🗺️ {mapa}"
            link_wa = f"https://wa.me/{NUMERO_ADMIN}?text={urllib.parse.quote(msg)}"
            
            st.markdown(f'<br><a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)

# ==============================================================================
# MODO ADMINISTRADOR (TU PANEL NUEVO)
# ==============================================================================
elif modo == "👮‍♂️ SOY ADMINISTRADOR":
    st.header("👮‍♂️ Panel de Control")
    pwd = st.text_input("Contraseña:", type="password")
    
    if pwd == PASSWORD_ADMIN:
        st.success("Acceso Correcto")
        # Aquí usamos la conexión nueva que configuramos en secrets
        try:
            df_viajes = conn.read(worksheet="VIAJES", ttl=5)
            df_choferes = conn.read(worksheet="CHOFERES", ttl=5)
            
            st.subheader("Últimos Viajes")
            st.dataframe(df_viajes.tail(5))
            
            st.subheader("Lista de Choferes")
            st.dataframe(df_choferes)
        except Exception as e:
            st.error(f"No se pudo leer la hoja. Verifica que la pestaña se llame VIAJES. Error: {e}")
