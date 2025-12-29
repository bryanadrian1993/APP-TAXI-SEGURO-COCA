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

# --- LISTAS GLOBALES ---
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

# --- TÍTULO ---
st.title("🚖 Portal de Socios")

# === CREAMOS DOS PESTAÑAS ===
tab1, tab2 = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])

# ==========================================
# PESTAÑA 1: INICIAR SESIÓN (CORREGIDO: NOMBRE Y APELLIDO)
# ==========================================
with tab1:
    st.markdown("### Ingresa a tu Panel")
    st.info("Ingresa con el Nombre y Apellido exactos de tu registro.")
    
    col_log1, col_log2 = st.columns(2)
    with col_log1:
        login_nombre = st.text_input("Tu Nombre", key="log_nom")
    with col_log2:
        login_apellido = st.text_input("Tu Apellido", key="log_ape")
        
    login_clave = st.text_input("Tu Contraseña", type="password", key="log_pass")
    
    if st.button("ENTRAR AL SISTEMA", type="primary"):
        with st.spinner("Verificando credenciales..."):
            df = cargar_datos("CHOFERES")
            
            if not df.empty:
                # 1. Limpiamos los datos para comparar (Todo a Mayúsculas y sin espacios extra)
                # Datos del Excel
                df['Nombre_Clean'] = df['Nombre'].astype(str).str.strip().str.upper()
                df['Apellido_Clean'] = df['Apellido'].astype(str).str.strip().str.upper()
                df['Clave_Clean'] = df['Clave'].astype(str).str.strip()
                
                # Datos ingresados por el usuario
                input_nom = str(login_nombre).strip().upper()
                input_ape = str(login_apellido).strip().upper()
                input_pass = str(login_clave).strip()
                
                # 2. Buscamos coincidencia exacta de Nombre y Apellido
                usuario_encontrado = df[
                    (df['Nombre_Clean'] == input_nom) & 
                    (df['Apellido_Clean'] == input_ape)
                ]
                
                if not usuario_encontrado.empty:
                    # El usuario existe, ahora verificamos la clave
                    dato_usuario = usuario_encontrado.iloc[0]
                    clave_real = dato_usuario['Clave_Clean']
                    
                    if input_pass == clave_real:
                        st.balloons()
                        st.success(f"✅ ¡Bienvenido, {dato_usuario['Nombre']}!")
                        
                        # --- PANEL DE CONTROL ---
                        st.divider()
                        st.subheader(f"🎛️ Panel de Control - {dato_usuario['Tipo_Vehiculo']}")
                        
                        col_estado, col_saldo = st.columns(2)
                        
                        with col_estado:
                            estado_actual = dato_usuario['Estado']
                            st.metric("Tu Estado", estado_actual)
                            
                            # Botones de Acción (Simulados por ahora)
                            if estado_actual == "LIBRE":
                                st.button("🔴 PONERME OCUPADO")
                            else:
                                st.button("🟢 PONERME LIBRE")
                                    
                        with col_saldo:
                            st.metric("Saldo a Pagar", f"${dato_usuario['SALDO']}")
                            if float(dato_usuario['SALDO']) > 5:
                                st.error("⚠️ Tienes saldo pendiente. Paga para recibir pedidos.")
                            else:
                                st.info("Estas al día con tus pagos.")
                            
                    else:
                        st.error("❌ Contraseña incorrecta.")
                else:
                    st.error("❌ No encontramos un conductor con ese Nombre y Apellido.")
                    st.warning("Verifica si escribiste bien o si te registraste con otro nombre.")
            else:
                st.error("Error de conexión con la base de datos.")

# ==========================================
# PESTAÑA 2: REGISTRO (SIN CAMBIOS)
# ==========================================
with tab2:
    st.markdown("### 📝 Registro Oficial de Socio")
    
    with st.form("form_registro_nuevo"):
        st.subheader("👤 Datos Personales")
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombres *")
            cedula = st.text_input("Cédula / DNI *")
            pais = st.selectbox("País de Operación *", PAISES)
            direccion = st.text_input("Dirección Domiciliaria *")
            
        with col2:
            apellido = st.text_input("Apellidos *")
            email = st.text_input("Correo Electrónico (Opcional)")
            idioma = st.selectbox("Idioma de preferencia *", IDIOMAS)
            telefono = st.text_input("WhatsApp (Ej: 593...) *")

        st.markdown("---")
        st.subheader("🚘 Datos del Vehículo y Seguridad")
        col3, col4 = st.columns(2)
        
        with col3:
            placa = st.text_input("Placa del Vehículo *")
            tipo_veh = st.selectbox("Tipo de Vehículo *", VEHICULOS)
            
        with col4:
            clave = st.text_input("Crea una Contraseña *", type="password")
            confirm_clave = st.text_input("Confirma la Contraseña *", type="password")

        st.caption("Al registrarte aceptas los términos y condiciones.")
        
        enviar = st.form_submit_button("✅ CREAR CUENTA Y TRABAJAR")

        if enviar:
            if not (nombre and apellido and cedula and telefono and placa and clave):
                st.error("⚠️ Por favor llena los campos obligatorios (*).")
            elif clave != confirm_clave:
                st.error("⚠️ Las contraseñas no coinciden.")
            else:
                with st.spinner("Registrando en el sistema..."):
                    datos = {
                        "accion": "registrar_conductor",
                        "nombre": nombre, "apellido": apellido,
                        "cedula": cedula, "email": email,
                        "direccion": direccion, "telefono": telefono,
                        "placa": placa, "clave": clave,
                        "pais": pais, "idioma": idioma, "tipo_veh": tipo_veh
                    }
                    
                    respuesta = enviar_datos(datos)
                    
                    if "REGISTRO_EXITOSO" in respuesta:
                        st.balloons()
                        st.success("🎉 ¡REGISTRO EXITOSO!")
                        st.info("Ve a la pestaña 'INGRESAR' para entrar.")
                    else:
                        st.error(f"Error de conexión: {respuesta}")
