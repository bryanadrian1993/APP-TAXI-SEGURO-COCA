import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
from datetime import datetime
from streamlit_js_eval import get_geolocation # <--- IMPORTANTE: ESTO ES NUEVO AQUÍ

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Portal Conductores", page_icon="🚖", layout="centered")

# 🆔 CONEXIÓN
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzgN1j4xiGgqjH842Ui5FwyMNCkH2k73jBd-GeSnn0Ja2ciNI-10RnTajH2GG7xIoCU/exec"
EMAIL_SOPORTE = "taxi-seguro-world@hotmail.com"

# --- INICIALIZAR SESIÓN ---
if 'usuario_activo' not in st.session_state:
    st.session_state.usuario_activo = False
if 'datos_usuario' not in st.session_state:
    st.session_state.datos_usuario = {}

# --- LISTAS ---
PAISES = ["Ecuador", "Colombia", "Perú", "México", "España", "Estados Unidos", "Otro"]
IDIOMAS = ["Español", "English", "Português", "Français", "Italiano", "Deutsch", "Otro"]
VEHICULOS = ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔", "Moto Entrega 🏍️"]

# --- FUNCIONES ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

def enviar_datos(datos):
    try:
        params = urllib.parse.urlencode(datos)
        url_final = f"{URL_SCRIPT}?{params}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

# --- INTERFAZ ---
st.title("🚖 Portal de Socios")

# ESCENARIO 1: DENTRO DEL PANEL
if st.session_state.usuario_activo:
    user = st.session_state.datos_usuario
    st.success(f"✅ Bienvenido: **{user['Nombre']} {user['Apellido']}**")
    st.markdown("---")
    
    st.subheader(f"🚦 ESTADO: {user.get('Estado', 'DESCONOCIDO')}")
    
    # === AQUÍ ESTÁ EL "AGENTE SECRETO" (RASTREO GPS) ===
    # Solo rastreamos si el chofer dice que está LIBRE
    if user.get('Estado') == "LIBRE":
        # Solicitamos GPS de forma invisible
        loc_chofer = get_geolocation(component_key='gps_driver')
        
        if loc_chofer:
            lat = loc_chofer['coords']['latitude']
            lon = loc_chofer['coords']['longitude']
            
            # Enviamos la ubicación a la Nube silenciosamente
            enviar_datos({
                "accion": "actualizar_gps_chofer",
                "conductor": f"{user['Nombre']} {user['Apellido']}",
                "lat": lat,
                "lon": lon
            })
            # Opcional: Un puntito verde pequeño para que sepa que el GPS funciona
            st.caption(f"📡 Señal GPS Activa: {lat:.4f}, {lon:.4f}")
    # ===================================================

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🟢 PONERME LIBRE", use_container_width=True):
            enviar_datos({"accion": "actualizar_estado", "nombre": user['Nombre'], "apellido": user['Apellido'], "estado": "LIBRE"})
            st.session_state.datos_usuario['Estado'] = "LIBRE"
            st.rerun()
    with c2:
        if st.button("🔴 PONERME OCUPADO", use_container_width=True):
            enviar_datos({"accion": "actualizar_estado", "nombre": user['Nombre'], "apellido": user['Apellido'], "estado": "OCUPADO"})
            st.session_state.datos_usuario['Estado'] = "OCUPADO"
            st.rerun()

    st.info(f"💰 Saldo Pendiente: ${user.get('SALDO', 0)}")
    
    st.markdown("---")
    with st.expander("⚙️ Gestión de Cuenta"):
        if st.button("🔒 CERRAR SESIÓN", use_container_width=True):
            st.session_state.usuario_activo = False
            st.session_state.datos_usuario = {}
            st.rerun()
        st.markdown("---")
        st.markdown("### 🗑️ Eliminar mi Cuenta")
        clave_del = st.text_input("Confirma tu contraseña para eliminar:", type="password")
        if st.button("⚠️ ELIMINAR CUENTA DEFINITIVAMENTE", type="primary"):
            if clave_del:
                with st.spinner("Eliminando..."):
                    res = enviar_datos({"accion": "eliminar_conductor", "nombre": user['Nombre'], "apellido": user['Apellido'], "clave": clave_del})
                    if "ELIMINADO_OK" in res:
                        st.session_state.usuario_activo = False
                        st.success("✅ Cuenta eliminada.")
                        st.balloons()
                        st.rerun()
                    elif "ERROR_DATOS" in res:
                        st.error("❌ Contraseña incorrecta.")
                    else: st.error("❌ Error de conexión.")
            else: st.warning("Escribe tu contraseña.")

# ESCENARIO 2: LOGIN / REGISTRO (SIN CAMBIOS)
else:
    tab1, tab2 = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])
    with tab1:
        col_L1, col_L2 = st.columns(2)
        l_nom = col_L1.text_input("Nombre", key="ln")
        l_ape = col_L2.text_input("Apellido", key="la")
        l_pass = st.text_input("Contraseña", type="password", key="lp")
        if st.button("ENTRAR", type="primary"):
            if l_nom and l_ape and l_pass:
                with st.spinner("Verificando..."):
                    df = cargar_datos("CHOFERES")
                    if not df.empty:
                        try:
                            match = df[(df['Nombre'].str.strip().str.upper() == l_nom.strip().upper()) & (df['Apellido'].str.strip().str.upper() == l_ape.strip().upper())]
                            if not match.empty:
                                usuario = match.iloc[0]
                                if str(usuario['Clave']).strip() == l_pass.strip():
                                    st.session_state.usuario_activo = True
                                    st.session_state.datos_usuario = usuario.to_dict()
                                    st.rerun()
                                else: st.error("❌ Contraseña incorrecta.")
                            else: st.error("❌ Usuario no encontrado.")
                        except: st.error("Error validando datos.")
            else: st.warning("Llena todos los campos.")
        st.markdown("---")
        with st.expander("❓ ¿Olvidaste tu contraseña?"):
            recup_email = st.text_input("Tu Correo Electrónico:")
            if st.button("📧 RECUPERAR CLAVE"):
                if recup_email:
                    with st.spinner("Enviando correo..."):
                        res = enviar_datos({"accion": "recuperar_clave", "email": recup_email})
                        if "CORREO_ENVIADO" in res: st.success("✅ ¡Listo! Revisa tu correo.")
                        elif "EMAIL_NO_ENCONTRADO" in res: st.error("❌ Correo no registrado.")
                        else: st.error("Error de conexión.")

    with tab2:
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            r_nom = c1.text_input("Nombres *")
            r_ape = c2.text_input("Apellidos *")
            c3, c4 = st.columns(2)
            r_ced = c3.text_input("Cédula/ID *")
            r_pais = c4.selectbox("País *", PAISES)
            c5, c6 = st.columns(2)
            r_dir = c5.text_input("Dirección *")
            r_email = c6.text_input("Email (Vital para recuperar clave) *")
            c7, c8 = st.columns(2)
            r_idioma = c7.selectbox("Idioma *", IDIOMAS)
            r_telf = c8.text_input("WhatsApp (con código) *")
            c9, c10 = st.columns(2)
            r_pla = c9.text_input("Placa *")
            r_veh = c10.selectbox("Vehículo *", VEHICULOS)
            r_pass1 = st.text_input("Crear Clave *", type="password")
            r_pass2 = st.text_input("Confirmar Clave *", type="password")
            if st.form_submit_button("✅ REGISTRARME"):
                if r_nom and r_email and r_pass1 == r_pass2:
                    datos = {"accion": "registrar_conductor", "nombre": r_nom, "apellido": r_ape, "cedula": r_ced, "telefono": r_telf, "placa": r_pla, "tipo_veh": r_veh, "pais": r_pais, "idioma": r_idioma, "direccion": r_dir, "clave": r_pass1, "email": r_email}
                    res = enviar_datos(datos)
                    if "REGISTRO_EXITOSO" in res:
                        st.success("🎉 ¡Cuenta Creada!")
                        st.error(f"⚠️ Envía tus documentos a: {EMAIL_SOPORTE} en 48h.")
                else: st.error("Revisa los datos obligatorios.")
