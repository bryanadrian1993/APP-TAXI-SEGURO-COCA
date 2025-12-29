import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal de Socios", layout="wide")

# Tu URL de Google Apps Script
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwI2zteeExU_Zy2yHLMR3A49ZYSHwP_xNGsTy-AuRiD_6llZA6V_QxvvOYiXD48w2uc/exec"
EMAIL_ADMIN = "taxi-seguroecuador@hotmail.com"

# --- FUNCIÓN PARA ACTUALIZAR ESTADO EN EXCEL ---
def actualizar_estado_en_sheets(nombre_completo, nuevo_estado):
    try:
        params = {
            "accion": "actualizar_estado",
            "nombre": nombre_completo,
            "estado": nuevo_estado
        }
        query_string = urllib.parse.urlencode(params)
        url_final = f"{URL_SCRIPT}?{query_string}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

# --- 1. ACCESO PARA SOCIOS (LIBRE / OCUPADO) ---
st.markdown("# 👮 PORTAL DE CONDUCTORES")

# Inicializar estado de conexión para evitar errores de variable
if 'conectado' not in st.session_state:
    st.session_state.conectado = False

if not st.session_state.conectado:
    with st.expander("🔐 CLIC AQUÍ PARA INGRESAR Y MARCAR TU ESTADO", expanded=True):
        col_login1, col_login2 = st.columns(2)
        nom_acceso = col_login1.text_input("Nombre (como registró):", key="acceso_nom")
        ape_acceso = col_login2.text_input("Apellido (como registró):", key="acceso_ape")
        
        if st.button("INGRESAR AL SISTEMA"):
            if nom_acceso and ape_acceso:
                st.session_state.conectado = True
                # Sumamos nombre y apellido para la búsqueda en Excel
                st.session_state.usuario_completo = f"{nom_acceso} {ape_acceso}".upper().strip()
                st.rerun()
            else:
                st.error("Por favor ingrese su Nombre y Apellido.")
else:
    st.success(f"Socio Activo: **{st.session_state.usuario_completo}**")
    b1, b2 = st.columns(2)
    
    if b1.button("🟢 MARCAR COMO LIBRE", use_container_width=True):
        with st.spinner("Actualizando en Excel..."):
            res = actualizar_estado_en_sheets(st.session_state.usuario_completo, "LIBRE")
            if "OK" in res:
                st.toast("✅ Estado actualizado: LIBRE")
            else:
                st.error(f"Error: {res}")
    
    if b2.button("🔴 MARCAR COMO OCUPADO", use_container_width=True):
        with st.spinner("Actualizando en Excel..."):
            res = actualizar_estado_en_sheets(st.session_state.usuario_completo, "OCUPADO")
            if "OK" in res:
                st.toast("✅ Estado actualizado: OCUPADO")
    
    if st.button("Cerrar Sesión"):
        st.session_state.conectado = False
        st.rerun()

st.divider()

# --- 2. FORMULARIO DE REGISTRO (MANTIENE TU LÓGICA ORIGINAL) ---
st.subheader("📝 Nuevo Registro de Socio")

def registrar_chofer(nombre, apellido, cedula, email, direccion, telefono, placa, clave):
    try:
        params = {
            "accion": "registro",
            "nombre": nombre, "apellido": apellido,
            "cedula": cedula, "email": email,
            "direccion": direccion,
            "telefono": telefono, "placa": placa, "clave": clave
        }
        query_string = urllib.parse.urlencode(params)
        url_final = f"{URL_SCRIPT}?{query_string}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

with st.form("form_registro"):
    st.write("👤 **Datos Personales**")
    c1, c2 = st.columns(2)
    nombre_reg = c1.text_input("Nombres:")
    apellido_reg = c2.text_input("Apellidos:")
    cedula_reg = st.text_input("Cédula de Identidad:")
    
    st.write("🏠 **Domicilio**")
    direccion_reg = st.text_input("Dirección Domiciliaria Completa:")
    
    st.write("📧 **Contacto**")
    email_reg = st.text_input("Correo Electrónico:")
    telefono_reg = st.text_input("Celular (ej: 593...):")
    
    st.write("🚖 **Datos del Vehículo**")
    placa_reg = st.text_input("Placa del Vehículo:")
    
    st.write("🔐 **Seguridad**")
    clave_reg = st.text_input("Crea tu Contraseña:", type="password")
    
    acepto_reg = st.checkbox("Declaro que mis documentos están vigentes.")
    
    enviar_reg = st.form_submit_button("🚀 GUARDAR Y CONTINUAR")

if enviar_reg:
    if not nombre_reg or not clave_reg or not placa_reg:
        st.error("❌ Faltan datos obligatorios.")
    elif not acepto_reg:
        st.warning("⚠️ Debes aceptar los términos.")
    else:
        with st.spinner("Registrando..."):
            resultado_reg = registrar_chofer(nombre_reg, apellido_reg, cedula_reg, email_reg, direccion_reg, telefono_reg, placa_reg, clave_reg)
            if "REGISTRO_OK" in resultado_reg:
                st.success("✅ ¡REGISTRO GUARDADO EN EXCEL!")
                st.balloons()
