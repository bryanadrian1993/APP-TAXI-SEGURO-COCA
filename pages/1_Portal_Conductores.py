import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Registro Conductores", layout="centered")

# --- CONFIGURACIÓN DE GOOGLE SHEETS ---
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwI2zteeExU_Zy2yHLMR3A49ZYSHwP_xNGsTy-AuRiD_6llZA6V_QxvvOYiXD48w2uc/exec"
EMAIL_ADMIN = "taxi-seguroecuador@hotmail.com"

# --- INICIALIZACIÓN DE VARIABLES (Cura el NameError de la línea 22) ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
if 'usuario_completo' not in st.session_state:
    st.session_state.usuario_completo = ""

# --- FUNCIONES DE COMUNICACIÓN ---
def registrar_chofer(nombre, apellido, cedula, email, direccion, telefono, placa, clave):
    try:
        params = {
            "accion": "registro", "nombre": nombre, "apellido": apellido,
            "cedula": cedula, "email": email, "direccion": direccion,
            "telefono": telefono, "placa": placa, "clave": clave
        }
        url_final = f"{URL_SCRIPT}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

def actualizar_estado_en_sheets(nombre_completo, nuevo_estado):
    try:
        params = {"accion": "actualizar_estado", "nombre": nombre_completo, "estado": nuevo_estado}
        url_final = f"{URL_SCRIPT}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

# --- DISEÑO SUPERIOR (LOGO Y TÍTULO) ---
st.image("https://cdn-icons-png.flaticon.com/512/2083/2083260.png", width=100)
st.title("📝 REGISTRO DE SOCIOS")

# --- 1. ACCESO SOCIOS (MARCAR LIBRE/OCUPADO) ---
if not st.session_state.conectado:
    with st.expander("🔐 CLIC AQUÍ PARA INGRESAR Y MARCAR TU ESTADO", expanded=False):
        c1, c2 = st.columns(2)
        nom_acc = c1.text_input("Nombre (como registró):", key="acc_nom")
        ape_acc = c2.text_input("Apellido (como registró):", key="acc_ape")
        if st.button("INGRESAR AL SISTEMA"):
            if nom_acc and ape_acc:
                st.session_state.conectado = True
                # Se limpia el nombre (TRIM) para evitar errores de búsqueda 
                st.session_state.usuario_completo = f"{nom_acc} {ape_acc}".upper().strip()
                st.rerun()
else:
    st.success(f"Socio Activo: **{st.session_state.usuario_completo}**")
    b1, b2 = st.columns(2)
    if b1.button("🟢 ESTOY LIBRE", use_container_width=True):
        res = actualizar_estado_en_sheets(st.session_state.usuario_completo, "LIBRE")
        if "OK" in res: st.toast("✅ Estado actualizado en Excel")
        else: st.error(f"Error: {res}") # Ayuda a ver si no encuentra al socio
    
    if b2.button("🔴 ESTOY OCUPADO", use_container_width=True):
        res = actualizar_estado_en_sheets(st.session_state.usuario_completo, "OCUPADO")
        if "OK" in res: st.toast("✅ Estado actualizado en Excel")
        else: st.error(f"Error: {res}")

    if st.button("Cerrar Sesión"):
        st.session_state.conectado = False
        st.rerun()

st.divider()

# --- 2. FORMULARIO DE REGISTRO (ORIGINAL RESTAURADO) ---
with st.form("form_registro"):
    st.write("👤 **Datos Personales**")
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombres:")
    apellido = c2.text_input("Apellidos:")
    cedula = st.text_input("Cédula de Identidad:")
    
    st.write("🏠 **Domicilio**")
    direccion = st.text_input("Dirección Domiciliaria Completa:")
    
    st.write("📧 **Contacto**")
    email = st.text_input("Tu Correo Electrónico:")
    telefono = st.text_input("Celular (ej: 593...):")
    
    st.write("🚖 **Datos del Vehículo**")
    placa = st.text_input("Placa del Vehículo:")
    
    st.write("🔐 **Seguridad**")
    st.info("Crea tu contraseña para entrar:")
    clave = st.text_input("Contraseña:", type="password")
    
    acepto = st.checkbox("Declaro que mis documentos están vigentes.")
    enviar = st.form_submit_button("🚀 GUARDAR Y CONTINUAR")

# --- LÓGICA DE ENVÍO Y REQUISITOS (ORIGINAL) ---
if enviar:
    if not nombre or not email or not clave or not placa:
        st.error("❌ Faltan datos obligatorios.")
    elif not acepto:
        st.warning("⚠️ Debes aceptar los términos.")
    else:
        with st.spinner("Guardando registro..."):
            resultado = registrar_chofer(nombre, apellido, cedula, email, direccion, telefono, placa, clave)
            if "REGISTRO_OK" in resultado:
                st.success("✅ ¡DATOS GUARDADOS!")
                st.balloons()
                
                # Preparar mensaje para botones de email
                asunto = f"ALTA NUEVO SOCIO - {nombre} {apellido}"
                cuerpo = f"Hola Admin,\nSoy {nombre} {apellido}.\nCédula: {cedula}\nPlaca: {placa}\n\nADJUNTO REQUISITOS."
                link_email = f"mailto:{EMAIL_ADMIN}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                
                st.markdown(f'<a href="{link_email}" style="background-color:#0277BD; color:white; padding:15px; display:block; text-align:center; text-decoration:none; border-radius:10px; font-weight:bold;">📱 ENVIAR REQUISITOS POR CELULAR</a>', unsafe_allow_html=True)
            else:
                st.error(f"Error: {resultado}")
