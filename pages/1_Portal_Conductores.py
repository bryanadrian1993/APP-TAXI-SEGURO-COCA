import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal Conductores", page_icon="🚖", layout="centered")

# 🆔 TUS DATOS DE CONEXIÓN
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbw9h2Rm1JkZHnL56-TY8SiuPbeGlM5FJc7mQ1zIXYO4jzeEato_XJ0Jl-DzfTJhXjoQ/exec"

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'usuario_activo' not in st.session_state:
    st.session_state.usuario_activo = False
if 'datos_usuario' not in st.session_state:
    st.session_state.datos_usuario = {}

# ==========================================
# 🌎 LISTAS GLOBALES AMPLIADAS
# ==========================================
PAISES = [
    "Ecuador", "Colombia", "Perú", "México", "España", "Estados Unidos",
    "Argentina", "Bolivia", "Brasil", "Chile", "Costa Rica", "Cuba",
    "El Salvador", "Guatemala", "Honduras", "Nicaragua", "Panamá", "Paraguay",
    "Puerto Rico", "República Dominicana", "Uruguay", "Venezuela",
    "Canadá", "Italia", "Francia", "Alemania", "Reino Unido", "Portugal",
    "Rusia", "China", "Japón", "Otro"
]

IDIOMAS = [
    "Español", "English", "Português", "Français", "Italiano", 
    "Deutsch (Alemán)", "Русский (Ruso)", "中文 (Chino)", "العربية (Árabe)", 
    "Quechua", "Shuar"
]

VEHICULOS = ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔", "Moto Entrega 🏍️", "Camión de Carga 🚛"]

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

def actualizar_estado_nube(nombre, apellido, nuevo_estado):
    datos = {
        "accion": "actualizar_estado", 
        "nombre": nombre,
        "apellido": apellido,
        "estado": nuevo_estado
    }
    return enviar_datos(datos)

# --- INTERFAZ PRINCIPAL ---
st.title("🚖 Portal de Socios")

# ====================================================
# ESCENARIO 1: EL CONDUCTOR YA INGRESÓ (PANEL DE CONTROL)
# ====================================================
if st.session_state.usuario_activo:
    user = st.session_state.datos_usuario
    
    st.success(f"✅ Bienvenido: **{user['Nombre']} {user['Apellido']}**")
    
    st.markdown("---")
    st.subheader(f"🚦 PANEL DE CONTROL - {user.get('Tipo_Vehiculo', 'Conductor')}")
    
    # --- BOTONES DE ESTADO ---
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🟢 ESTOY LIBRE", use_container_width=True):
            with st.spinner("Actualizando..."):
                res = actualizar_estado_nube(user['Nombre'], user['Apellido'], "LIBRE")
                st.session_state.datos_usuario['Estado'] = "LIBRE"
                st.toast("✅ ¡Ahora estás visible para clientes!")
                st.rerun()
    
    with col_btn2:
        if st.button("🔴 ESTOY OCUPADO", use_container_width=True):
            with st.spinner("Actualizando..."):
                res = actualizar_estado_nube(user['Nombre'], user['Apellido'], "OCUPADO")
                st.session_state.datos_usuario['Estado'] = "OCUPADO"
                st.toast("⛔ Te has puesto como Ocupado.")
                st.rerun()

    # Mostramos el estado actual grande
    estado_actual = st.session_state.datos_usuario.get('Estado', 'DESCONOCIDO')
    if estado_actual == "LIBRE":
        st.markdown(f"<h2 style='text-align: center; color: green;'>ESTADO: {estado_actual}</h2>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h2 style='text-align: center; color: red;'>ESTADO: {estado_actual}</h2>", unsafe_allow_html=True)

    st.info(f"💰 Saldo Pendiente: ${user.get('SALDO', 0)}")
    
    st.markdown("---")
    if st.button("🔒 CERRAR SESIÓN"):
        st.session_state.usuario_activo = False
        st.session_state.datos_usuario = {}
        st.rerun()

# ====================================================
# ESCENARIO 2: NO HA INGRESADO (LOGIN O REGISTRO)
# ====================================================
else:
    tab1, tab2 = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])

    # --- PESTAÑA 1: LOGIN ---
    with tab1:
        st.info("Ingresa tus datos para acceder.")
        
        c_log1, c_log2 = st.columns(2)
        with c_log1:
            l_nom = st.text_input("Nombre", key="ln")
        with c_log2:
            l_ape = st.text_input("Apellido", key="la")
            
        l_pass = st.text_input("Contraseña", type="password", key="lp")

        if st.button("ENTRAR AL SISTEMA", type="primary"):
            if l_nom and l_ape and l_pass:
                with st.spinner("Buscando usuario..."):
                    df = cargar_datos("CHOFERES")
                    
                    if not df.empty:
                        try:
                            if 'Nombre' in df.columns and 'Apellido' in df.columns and 'Clave' in df.columns:
                                df['N_Clean'] = df['Nombre'].astype(str).str.strip().str.upper()
                                df['A_Clean'] = df['Apellido'].astype(str).str.strip().str.upper()
                                df['P_Clean'] = df['Clave'].astype(str).str.strip()
                                
                                u_nom = str(l_nom).strip().upper()
                                u_ape = str(l_ape).strip().upper()
                                u_pass = str(l_pass).strip()

                                encontrado = df[(df['N_Clean'] == u_nom) & (df['A_Clean'] == u_ape)]
                                
                                if not encontrado.empty:
                                    usuario = encontrado.iloc[0]
                                    if str(usuario['P_Clean']) == u_pass:
                                        st.session_state.usuario_activo = True
                                        st.session_state.datos_usuario = usuario.to_dict()
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error("❌ Contraseña incorrecta.")
                                else:
                                    st.error("❌ Usuario no encontrado.")
                            else:
                                st.error("⚠️ Error en base de datos (Columnas).")
                        except Exception as e:
                            st.error(f"Error procesando: {e}")
                    else:
                        st.error("Error conectando con la nube.")
            else:
                st.warning("⚠️ Llena todos los campos.")

    # --- PESTAÑA 2: REGISTRO (GLOBAL) ---
    with tab2:
        st.markdown("### 📝 Registro Global")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            r_nom = c1.text_input("Nombres *")
            r_ape = c2.text_input("Apellidos *")
            
            c3, c4 = st.columns(2)
            r_ced = c3.text_input("Cédula/ID *")
            # AQUÍ AHORA SALDRÁN TODOS LOS PAÍSES
            r_pais = c4.selectbox("País de Operación *", PAISES)
            
            c5, c6 = st.columns(2)
            r_dir = c5.text_input("Dirección *")
            # AQUÍ AHORA SALDRÁN TODOS LOS IDIOMAS
            r_idioma = c6.selectbox("Idioma *", IDIOMAS)
            
            r_telf = st.text_input("WhatsApp (con código país) *")
            
            st.markdown("---")
            c7, c8 = st.columns(2)
            r_pla = c7.text_input("Placa *")
            r_veh = c8.selectbox("Tipo Vehículo *", VEHICULOS)
            
            r_pass1 = st.text_input("Crear Clave *", type="password")
            r_pass2 = st.text_input("Confirmar Clave *", type="password")
            
            if st.form_submit_button("✅ REGISTRARME"):
                if not (r_nom and r_ape and r_ced and r_telf and r_pla and r_pass1):
                    st.warning("⚠️ Faltan campos obligatorios.")
                elif r_pass1 != r_pass2:
                    st.error("⚠️ Las contraseñas no coinciden.")
                else:
                    with st.spinner("Creando cuenta global..."):
                        datos = {
                            "accion": "registrar_conductor",
                            "nombre": r_nom, "apellido": r_ape,
                            "cedula": r_ced, "telefono": r_telf,
                            "placa": r_pla, "tipo_veh": r_veh,
                            "pais": r_pais, "idioma": r_idioma,
                            "direccion": r_dir, "clave": r_pass1,
                            "email": ""
                        }
                        res = enviar_datos(datos)
                        if "REGISTRO_EXITOSO" in res:
                            st.success(f"🎉 ¡Bienvenido! Configurado para {r_pais} en {r_idioma}.")
                            st.info("Ve a la pestaña INGRESAR para comenzar.")
                            st.balloons()
                        else:
                            st.error("Error de conexión.")
