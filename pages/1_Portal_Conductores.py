import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import base64
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Portal Conductores", page_icon="🚖", layout="centered")

# 🆔 CONEXIÓN
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwzOVH8c8f9WEoE4OJOTIccz_EgrOpZ8ySURTVRwi0bnQhFnWVdgfX1W8ivTIu5dFfs/exec"

# --- INICIALIZAR SESIÓN ---
if 'usuario_activo' not in st.session_state: st.session_state.usuario_activo = False
if 'datos_usuario' not in st.session_state: st.session_state.datos_usuario = {}

# --- LISTAS ---
PAISES = ["Ecuador", "Colombia", "Perú", "México", "España", "Estados Unidos", "Argentina", "Brasil", "Chile", "Otro"]
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

# --- INTERFAZ ---
st.title("🚖 Portal de Socios")

# ESCENARIO 1: DENTRO DEL PANEL
if st.session_state.usuario_activo:
    user = st.session_state.datos_usuario
    st.success(f"✅ Bienvenido: **{user['Nombre']} {user['Apellido']}**")
    
    # === FOTO DE PERFIL ===
    with st.expander("📸 Mi Foto de Perfil (Obligatorio)", expanded=True):
        col_f1, col_f2 = st.columns([1, 2])
        foto_actual = "SIN_FOTO"
        if 'FOTO_PENDIENTE' in user: foto_actual = str(user['FOTO_PENDIENTE'])
        
        with col_f1:
            if "http" in foto_actual:
                foto_visible = foto_actual.replace("uc?export=view&", "thumbnail?sz=w400&")
                st.image(foto_visible, caption="Tu Foto Actual", width=120)
            else: st.info("Sin foto")
        
        with col_f2:
            foto_subida = st.file_uploader("Subir nueva foto (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
            if foto_subida:
                if st.button("📤 GUARDAR FOTO"):
                    with st.spinner("Subiendo a la nube..."):
                        bytes_data = foto_subida.getvalue()
                        b64_str = base64.b64encode(bytes_data).decode('utf-8')
                        
                        res = enviar_datos({
                            "accion": "subir_foto_perfil",
                            "nombre_chofer": user['Nombre'],
                            "apellido_chofer": user['Apellido'],
                            "nombre_archivo": f"foto_{user['Nombre']}.jpg",
                            "imagen_base64": b64_str
                        })
                        
                        if "FOTO_OK" in res:
                            nueva_url = res.split("|")[1]
                            st.session_state.datos_usuario['FOTO_PENDIENTE'] = nueva_url
                            st.success("✅ ¡Foto actualizada!")
                            import time
                            time.sleep(1)
                            st.rerun()
                        else: st.error(f"Error: {res}")

    st.markdown("---")
    st.subheader(f"🚦 ESTADO: {user.get('Estado', 'DESCONOCIDO')}")
    
    if user.get('Estado') == "LIBRE":
        loc_chofer = get_geolocation(component_key='gps_driver')
        if loc_chofer:
            lat = loc_chofer['coords']['latitude']
            lon = loc_chofer['coords']['longitude']
            enviar_datos({
                "accion": "actualizar_gps_chofer",
                "conductor": f"{user['Nombre']} {user['Apellido']}",
                "lat": lat, "lon": lon
            })
            st.caption(f"📡 Señal GPS Activa")

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

    st.markdown("---")
    with st.expander("⚙️ Gestión de Cuenta"):
        if st.button("🔒 CERRAR SESIÓN", use_container_width=True):
            st.session_state.usuario_activo = False
            st.session_state.datos_usuario = {}
            st.rerun()

else:
    # LOGIN / REGISTRO
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
                        match = df[(df['Nombre'].str.strip().str.upper() == l_nom.strip().upper()) & (df['Apellido'].str.strip().str.upper() == l_ape.strip().upper())]
                        if not match.empty:
                            usuario = match.iloc[0]
                            if str(usuario['Clave']).strip() == l_pass.strip():
                                st.session_state.usuario_activo = True
                                st.session_state.datos_usuario = usuario.to_dict()
                                st.rerun()
                            else: st.error("❌ Contraseña incorrecta.")
                        else: st.error("❌ Usuario no encontrado.")
            else: st.warning("Llena todos los campos.")
            
    # === AQUÍ ESTÁ EL FORMULARIO RESTAURADO ===
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
            r_email = c6.text_input("Email *")
            c7, c8 = st.columns(2)
            r_idioma = c7.selectbox("Idioma *", IDIOMAS)
            r_telf = c8.text_input("WhatsApp (Sin código de país) *")
            c9, c10 = st.columns(2)
            r_pla = c9.text_input("Placa *")
            r_veh = c10.selectbox("Vehículo *", VEHICULOS)
            r_pass1 = st.text_input("Clave *", type="password")
            r_pass2 = st.text_input("Confirmar Clave *", type="password")
            
            if st.form_submit_button("✅ REGISTRARME"):
                if r_nom and r_email and r_pass1 == r_pass2:
                    # Limpiamos el número de whatsapp del chofer antes de enviarlo
                    # Asumimos que si no puso código, es de su país. 
                    # Por simplicidad aquí lo mandamos directo y el cliente (app.py) o el admin lo corregirán si hace falta.
                    datos = {
                        "accion": "registrar_conductor", 
                        "nombre": r_nom, 
                        "apellido": r_ape, 
                        "cedula": r_ced, 
                        "telefono": r_telf, 
                        "placa": r_pla, 
                        "tipo_veh": r_veh, 
                        "pais": r_pais, 
                        "idioma": r_idioma, 
                        "direccion": r_dir, 
                        "clave": r_pass1, 
                        "email": r_email
                    }
                    res = enviar_datos(datos)
                    if "REGISTRO_EXITOSO" in res: st.success("¡Cuenta Creada! Ahora puedes ingresar.")
                    else: st.error("Error al registrar.")
                else:
                    st.warning("Verifica que las claves coincidan y llenes los datos.")
