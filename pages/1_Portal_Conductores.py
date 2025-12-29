import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import base64
import math
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- ⚙️ CONFIGURACIÓN DE NEGOCIO ---
TARIFA_POR_KM = 0.10        # Comisión que te pagan ($0.10 por KM)
DEUDA_MAXIMA = 10.00        # Límite de bloqueo
LINK_PAYPAL = "https://paypal.me/CAMPOVERDEJARAMILLO" # ✅ Tu link real
NUMERO_DEUNA = "09XXXXXXXX" # 👈 Reemplaza con tu número de Deuna real

# --- 🔗 CONFIGURACIÓN TÉCNICA ---
st.set_page_config(page_title="Portal Conductores", page_icon="🚖", layout="centered")
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwzOVH8c8f9WEoE4OJOTIccz_EgrOpZ8ySURTVRwi0bnQhFnWVdgfX1W8ivTIu5dFfs/exec"

# --- 🔄 INICIALIZAR SESIÓN Y MEMORIA ---
if 'usuario_activo' not in st.session_state: st.session_state.usuario_activo = False
if 'datos_usuario' not in st.session_state: st.session_state.datos_usuario = {}
if 'ultima_lat' not in st.session_state: st.session_state.ultima_lat = None
if 'ultima_lon' not in st.session_state: st.session_state.ultima_lon = None

# --- 📋 LISTAS ---
PAISES = ["Ecuador", "Colombia", "Perú", "México", "España", "Estados Unidos", "Argentina", "Brasil", "Chile", "Otro"]
IDIOMAS = ["Español", "English", "Português", "Français", "Italiano", "Deutsch", "Otro"]
VEHICULOS = ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔", "Moto Entrega 🏍️"]

# --- 🛠️ FUNCIONES ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

def enviar_datos(datos):
    try:
        if 'imagen_base64' in datos:
            data = urllib.parse.urlencode(datos).encode()
            req = urllib.request.Request(URL_SCRIPT, data=data) 
            with urllib.request.urlopen(req) as response:
                return response.read().decode('utf-8')
        else:
            params = urllib.parse.urlencode(datos)
            url_final = f"{URL_SCRIPT}?{params}"
            with urllib.request.urlopen(url_final) as response:
                return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371 # Radio tierra km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) * R

# --- 📱 INTERFAZ ---
st.title("🚖 Portal de Socios")

if st.session_state.usuario_activo:
    # Recargar datos frescos del Excel para validar deuda real
    df_fresh = cargar_datos("CHOFERES")
    user_nom = st.session_state.datos_usuario['Nombre']
    user_ape = st.session_state.datos_usuario['Apellido']
    fila_actual = df_fresh[(df_fresh['Nombre'] == user_nom) & (df_fresh['Apellido'] == user_ape)]
    
    # Asignar valores (Columna Q es 16, Columna R es 17)
    km_actuales = float(fila_actual.iloc[0, 16]) if not fila_actual.empty else 0.0
    deuda_actual = float(fila_actual.iloc[0, 17]) if not fila_actual.empty else 0.0
    bloqueado = deuda_actual >= DEUDA_MAXIMA

    nombre_completo = f"{user_nom} {user_ape}"
    st.success(f"✅ Socio: **{nombre_completo}**")

    # === 💰 SISTEMA DE PAGOS Y BLOQUEO ===
    if bloqueado:
        st.error(f"⛔ CUENTA BLOQUEADA POR DEUDA: ${deuda_actual:.2f}")
        st.warning("Selecciona un método para pagar y reactivarte:")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f'''<a href="{LINK_PAYPAL}" target="_blank" style="text-decoration:none;"><div style="background-color:#003087;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">🔵 PAYPAL</div></a>''', unsafe_allow_html=True)
        with col_p2:
            if st.button("📱 MOSTRAR QR DEUNA", use_container_width=True):
                try: st.image("qr_deuna.png", caption=f"Envía a: {NUMERO_DEUNA}")
                except: st.error("Sube 'qr_deuna.png' a tu carpeta.")

        if st.button("🔄 YA PAGUÉ, REVISAR MI SALDO", type="primary", use_container_width=True):
            res = enviar_datos({"accion": "registrar_pago_deuda", "nombre_completo": nombre_completo})
            if "PAGO_EXITOSO" in res:
                st.success("¡Pago validado! Ya puedes trabajar.")
                st.rerun()
    
    else:
        # Panel Financiero si no está bloqueado
        st.metric("💸 Deuda Pendiente", f"${deuda_actual:.2f}", f"Límite: ${DEUDA_MAXIMA}")
        st.caption(f"📍 KM totales: {km_actuales:.2f}")
        st.progress(min(deuda_actual/DEUDA_MAXIMA, 1.0))

        # === 🚦 ESTADO Y RASTREO (Solo si no está bloqueado) ===
        st.subheader(f"🚦 ESTADO: {st.session_state.datos_usuario.get('Estado', 'OCUPADO')}")
        
        if st.session_state.datos_usuario.get('Estado') == "LIBRE":
            loc = get_geolocation(component_key='gps_tracking')
            if loc:
                lat_now, lon_now = loc['coords']['latitude'], loc['coords']['longitude']
                # Enviar GPS al servidor
                enviar_datos({"accion": "actualizar_gps_chofer", "conductor": nombre_completo, "lat": lat_now, "lon": lon_now})
                
                # Cobro por KM
                if st.session_state.ultima_lat:
                    dist = calcular_distancia(st.session_state.ultima_lat, st.session_state.ultima_lon, lat_now, lon_now)
                    if dist > 0.1: # Cobrar cada 100 metros
                        costo = dist * TARIFA_POR_KM
                        enviar_datos({"accion": "registrar_cobro_km", "nombre_completo": nombre_completo, "km": dist, "costo": costo})
                        st.session_state.ultima_lat, st.session_state.ultima_lon = lat_now, lon_now
                        st.toast(f"📈 Km registrado: +${costo:.3f}")
                else:
                    st.session_state.ultima_lat, st.session_state.ultima_lon = lat_now, lon_now

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🟢 PONERME LIBRE", use_container_width=True):
                enviar_datos({"accion": "actualizar_estado", "nombre": user_nom, "apellido": user_ape, "estado": "LIBRE"})
                st.session_state.datos_usuario['Estado'] = "LIBRE"
                st.rerun()
        with c2:
            if st.button("🔴 PONERME OCUPADO", use_container_width=True):
                enviar_datos({"accion": "actualizar_estado", "nombre": user_nom, "apellido": user_ape, "estado": "OCUPADO"})
                st.session_state.datos_usuario['Estado'] = "OCUPADO"
                st.rerun()

    # === FOTO DE PERFIL ===
    with st.expander("📸 Mi Foto de Perfil"):
        # ... (Tu código original de fotos se mantiene igual aquí) ...
        col_f1, col_f2 = st.columns([1, 2])
        foto_actual = str(st.session_state.datos_usuario.get('FOTO_PENDIENTE', "SIN_FOTO"))
        with col_f1:
            if "http" in foto_actual: st.image(foto_actual.replace("uc?export=view&", "thumbnail?sz=w400&"), width=120)
            else: st.info("Sin foto")
        with col_f2:
            foto_subida = st.file_uploader("Subir foto", type=['png', 'jpg', 'jpeg'])
            if foto_subida and st.button("📤 GUARDAR FOTO"):
                b64_str = base64.b64encode(foto_subida.getvalue()).decode('utf-8')
                res = enviar_datos({"accion": "subir_foto_perfil", "nombre_chofer": user_nom, "apellido_chofer": user_ape, "nombre_archivo": f"foto_{user_nom}.jpg", "imagen_base64": b64_str})
                if "FOTO_OK" in res:
                    st.session_state.datos_usuario['FOTO_PENDIENTE'] = res.split("|")[1]
                    st.success("¡Foto lista!")
                    st.rerun()

    if st.button("🔒 CERRAR SESIÓN"):
        st.session_state.usuario_activo = False
        st.rerun()

else:
    # --- LOGIN / REGISTRO (Tu código original intacto) ---
    tab1, tab2 = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])
    with tab1:
        # ... (Copia aquí tu lógica de Login original) ...
        l_nom = st.text_input("Nombre", key="ln")
        l_ape = st.text_input("Apellido", key="la")
        l_pass = st.text_input("Contraseña", type="password", key="lp")
        if st.button("ENTRAR"):
            df = cargar_datos("CHOFERES")
            match = df[(df['Nombre'].str.upper() == l_nom.upper()) & (df['Apellido'].str.upper() == l_ape.upper())]
            if not match.empty and str(match.iloc[0]['Clave']) == l_pass:
                st.session_state.usuario_activo = True
                st.session_state.datos_usuario = match.iloc[0].to_dict()
                st.rerun()
    with tab2:
        # ... (Aquí va tu formulario de registro original) ...
        with st.form("reg"):
             # (He mantenido los campos pero resumidos para el mensaje, usa tus campos de registro originales aquí)
             st.write("Formulario de Registro")
             # ... código de registro ...
             if st.form_submit_button("✅ REGISTRARME"):
                 # ... envío de datos original ...
                 pass
