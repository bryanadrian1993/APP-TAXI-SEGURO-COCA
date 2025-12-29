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
tab1, tab2 = st.tabs(["🔐 YA SOY CONDUCTOR", "📝 QUIERO REGISTRARME"])

# ==========================================
# PESTAÑA 1: INICIAR SESIÓN (LO QUE FALTABA)
# ==========================================
with tab1:
    st.markdown("### Ingresa a tu Panel de Control")
    st.info("Usa tu WhatsApp y la Clave que creaste al registrarte.")
    
    usuario = st.text_input("Tu WhatsApp (Usuario)", key="login_user")
    clave_input = st.text_input("Tu Contraseña", type="password", key="login_pass")
    
    if st.button("ENTRAR AL SISTEMA", type="primary"):
        df = cargar_datos("CHOFERES")
        
        if not df.empty:
            # Buscamos el usuario (convertimos a string para comparar bien)
            usuario_str = str(usuario).strip()
            # Limpiamos columna Telefono del Excel
            df['Telefono'] = df['Telefono'].astype(str).str.replace("'", "").str.strip()
            
            # Filtramos
            usuario_encontrado = df[df['Telefono'] == usuario_str]
            
            if not usuario_encontrado.empty:
                dato_usuario = usuario_encontrado.iloc[0]
                clave_real = str(dato_usuario['Clave']).strip()
                
                if clave_input == clave_real:
                    st.success(f"✅ ¡Bienvenido de nuevo, {dato_usuario['Nombre']}!")
                    st.balloons()
                    
                    # --- AQUÍ VA EL PANEL DE CONTROL DEL CONDUCTOR ---
                    st.divider()
                    st.subheader(f"Panel de Control - {dato_usuario['Tipo_Vehiculo']}")
                    
                    # Botón para cambiar estado
                    estado_actual = dato_usuario['Estado']
                    col_estado, col_saldo = st.columns(2)
                    
                    with col_estado:
                        st.metric("Estado Actual", estado_actual)
                        if estado_actual == "LIBRE":
                            if st.button("🔴 MARCAR OCUPADO"):
                                # Aquí iría la lógica para cambiar estado en Sheets
                                st.warning("Cambiando a Ocupado...")
                        else:
                            if st.button("🟢 MARCAR LIBRE"):
                                st.success("Cambiando a Libre...")
                                
                    with col_saldo:
                        st.metric("Saldo Pendiente", f"${dato_usuario['SALDO']}")
                        st.caption("Recuerda pagar tus comisiones para no ser bloqueado.")
                        
                else:
                    st.error("❌ Contraseña incorrecta.")
            else:
                st.error("❌ Usuario no encontrado. ¿Ya te registraste?")
        else:
            st.error("Error de conexión con la base de datos.")

# ==========================================
# PESTAÑA 2: REGISTRO (EL FORMULARIO NUEVO)
# ==========================================
with tab2:
    st.markdown("### 📝 Registro Oficial de Socio")
    st.markdown("Completa los datos para activar tu cuenta global.")

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
                        st.info("Ve a la pestaña 'YA SOY CONDUCTOR' para ingresar.")
                    else:
                        st.error(f"Error de conexión: {respuesta}")
