import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal Conductores", page_icon="🚖", layout="centered")

# 🆔 TUS DATOS DE CONEXIÓN
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyzzpVm-dlOu8ZGbPUGfOnq-joRYoV-wXuckOvgsmKRAbRZaJQHJ6k9uxfA4pU9EK0d/exec"

# --- INICIALIZAR SESIÓN (Para que no se salga al dar clic) ---
if 'usuario_activo' not in st.session_state:
    st.session_state.usuario_activo = None
if 'datos_usuario' not in st.session_state:
    st.session_state.datos_usuario = {}

# --- LISTAS ---
PAISES = ["Ecuador", "Colombia", "Perú", "México", "España", "USA"]
IDIOMAS = ["Español", "English", "Português", "Français"]
VEHICULOS = ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"]

# --- FUNCIONES DE CONEXIÓN ---
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

# --- FUNCIÓN ESPECIAL PARA CAMBIAR ESTADO ---
def cambiar_estado_nube(nombre, apellido, nuevo_estado):
    datos = {
        "accion": "actualizar_estado", # OJO: Debes agregar esto a tu Script de Google
        "nombre": nombre,
        "apellido": apellido,
        "estado": nuevo_estado
    }
    return enviar_datos(datos)

# --- INTERFAZ PRINCIPAL ---
st.title("🚖 Portal de Socios")

# Si ya está logueado, mostramos DIRECTAMENTE el Panel de Control
if st.session_state.usuario_activo:
    user = st.session_state.datos_usuario
    st.success(f"✅ Conductor Activo: {user['Nombre']} {user['Apellido']}")
    
    st.markdown("---")
    st.subheader(f"🚦 PANEL DE CONTROL - {user['Tipo_Vehiculo']}")
    
    # BOTONES DE ESTADO (LO QUE PEDISTE)
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🟢 ESTOY LIBRE", use_container_width=True):
            with st.spinner("Actualizando a LIBRE..."):
                # Enviamos la orden a Google Sheets
                cambiar_estado_nube(user['Nombre'], user['Apellido'], "LIBRE")
                st.toast("✅ ¡Ahora estás visible para clientes!")
                st.session_state.datos_usuario['Estado'] = "LIBRE" # Actualizamos visualmente
    
    with col_btn2:
        if st.button("🔴 ESTOY OCUPADO", use_container_width=True):
            with st.spinner("Actualizando a OCUPADO..."):
                # Enviamos la orden a Google Sheets
                cambiar_estado_nube(user['Nombre'], user['Apellido'], "OCUPADO")
                st.toast("⛔ Te has puesto como Ocupado.")
                st.session_state.datos_usuario['Estado'] = "OCUPADO" # Actualizamos visualmente

    # INFORMACIÓN DE SALDO
    st.info(f"💰 Tu Saldo Pendiente: ${user.get('SALDO', 0)}")
    
    st.markdown("---")
    if st.button("Cerrar Sesión"):
        st.session_state.usuario_activo = None
        st.session_state.datos_usuario = {}
        st.rerun()

else:
    # SI NO ESTÁ LOGUEADO, MOSTRAMOS EL LOGIN/REGISTRO
    tab1, tab2 = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])

    # ==========================================
    # PESTAÑA 1: LOGIN (NOMBRE Y APELLIDO)
    # ==========================================
    with tab1:
        st.info("Ingresa tus datos para acceder al panel.")
        c1, c2 = st.columns(2)
        with c1:
            l_nom = st.text_input("Nombre", key="log_n")
        with c2:
            l_ape = st.text_input("Apellido", key="log_a")
        l_pass = st.text_input("Contraseña", type="password", key="log_p")

        if st.button("ENTRAR", type="primary"):
            if l_nom and l_ape and l_pass:
                with st.spinner("Verificando..."):
                    df = cargar_datos("CHOFERES")
                    if not df.empty:
                        # Limpieza para comparar
                        df['N_Clean'] = df['Nombre'].astype(str).str.strip().str.upper()
                        df['A_Clean'] = df['Apellido'].astype(str).str.strip().str.upper()
                        df['P_Clean'] = df['Clave'].astype(str).str.strip()
                        
                        u_nom = str(l_nom).strip().upper()
                        u_ape = str(l_ape).strip().upper()
                        u_pass = str(l_pass).strip()

                        found = df[(df['N_Clean'] == u_nom) & (df['A_Clean'] == u_ape)]
                        
                        if not found.empty:
                            usuario = found.iloc[0]
                            if str(usuario['P_Clean']) == u_pass:
                                # ¡LOGIN EXITOSO! GUARDAMOS EN SESIÓN
                                st.session_state.usuario_activo = True
                                st.session_state.datos_usuario = usuario.to_dict()
                                st.rerun() # Recargamos para mostrar el panel
                            else:
                                st.error("❌ Contraseña incorrecta.")
                        else:
                            st.error("❌ Usuario no encontrado.")
                    else:
                        st.error("Error de conexión.")
            else:
                st.warning("Llena todos los campos.")

    # ==========================================
    # PESTAÑA 2: REGISTRO (COMPLETO)
    # ==========================================
    with tab2:
        st.markdown("### 📝 Nuevo Registro")
        with st.form("form_reg"):
            c1, c2 = st.columns(2)
            r_nom = c1.text_input("Nombre *")
            r_ape = c2.text_input("Apellido *")
            
            c3, c4 = st.columns(2)
            r_ced = c3.text_input("Cédula *")
            r_tel = c4.text_input("WhatsApp *")
            
            c5, c6 = st.columns(2)
            r_pla = c5.text_input("Placa *")
            r_veh = c6.selectbox("Vehículo", VEHICULOS)
            
            r_pais = st.selectbox("País", PAISES)
            r_idioma = st.selectbox("Idioma", IDIOMAS)
            r_dir = st.text_input("Dirección")
            r_pass = st.text_input("Crear Clave *", type="password")

            if st.form_submit_button("REGISTRARSE"):
                if r_nom and r_ape and r_ced and r_tel and r_pla and r_pass:
                    datos = {
                        "accion": "registrar_conductor",
                        "nombre": r_nom, "apellido": r_ape,
                        "cedula": r_ced, "telefono": r_tel,
                        "placa": r_pla, "tipo_veh": r_veh,
                        "pais": r_pais, "idioma": r_idioma,
                        "direccion": r_dir, "clave": r_pass,
                        "email": ""
                    }
                    res = enviar_datos(datos)
                    if "REGISTRO_EXITOSO" in res:
                        st.success("✅ Cuenta creada. Ahora INGRESA en la otra pestaña.")
                    else:
                        st.error("Error de conexión.")
                else:
                    st.warning("Faltan datos obligatorios.")
