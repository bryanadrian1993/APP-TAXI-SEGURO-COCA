import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Registro Conductores", layout="wide")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwI2zteeExU_Zy2yHLMR3A49ZYSHwP_xNGsTy-AuRiD_6llZA6V_QxvvOYiXD48w2uc/exec"
EMAIL_ADMIN = "taxi-seguroecuador@hotmail.com"

# --- LÓGICA DE LOGIN Y ESTADO (Botón arriba) ---
col_logo, col_espacio, col_login = st.columns([1, 1, 1.5])

with col_logo:
    st.image("https://cdn-icons-png.flaticon.com/512/2083/2083260.png", width=80)

with col_login:
    if 'conectado' not in st.session_state:
        st.session_state.conectado = False
    
    if st.button("🔐 ACCESO SOCIOS (Libre/Ocupado)", use_container_width=True):
        st.session_state.ver_login = not st.session_state.get('ver_login', False)

if st.session_state.get('ver_login', False):
    with st.container(border=True):
        if not st.session_state.conectado:
            st.subheader("Ingreso de Socio")
            c1, c2 = st.columns(2)
            u_nom = c1.text_input("Nombre:")
            u_cla = c2.text_input("Contraseña:", type="password")
            if st.button("INGRESAR"):
                if u_nom and u_cla:
                    st.session_state.conectado = True
                    st.session_state.usuario = u_nom
                    st.rerun()
        else:
            st.success(f"Hola, {st.session_state.usuario}")
            b1, b2 = st.columns(2)
            if b1.button("🟢 ESTOY LIBRE", use_container_width=True):
                st.session_state.mi_estado = "LIBRE"
            if b2.button("🔴 ESTOY OCUPADO", use_container_width=True):
                st.session_state.mi_estado = "OCUPADO"
            
            est = st.session_state.get('mi_estado', 'SIN DEFINIR')
            color = "#28a745" if est == "LIBRE" else "#dc3545"
            st.markdown(f"<div style='background-color:{color}; color:white; padding:10px; border-radius:10px; text-align:center;'><h3>ESTADO: {est}</h3></div>", unsafe_allow_html=True)
            
            if st.button("Cerrar Sesión"):
                st.session_state.conectado = False
                st.rerun()

st.title("📝 REGISTRO DE SOCIOS")

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

# --- FORMULARIO ORIGINAL (Se mantiene) ---
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

# --- LÓGICA DE ENVÍO (Se mantiene) ---
if enviar:
    if not nombre or not email or not clave or not placa or not direccion:
        st.error("❌ Faltan datos obligatorios.")
    elif not acepto:
        st.warning("⚠️ Debes aceptar los términos.")
    else:
        with st.spinner("Guardando registro..."):
            resultado = registrar_chofer(nombre, apellido, cedula, email, direccion, telefono, placa, clave)
            if "REGISTRO_OK" in resultado:
                st.success("✅ ¡DATOS GUARDADOS!")
                st.balloons()
                
                asunto = f"ALTA NUEVO SOCIO - {nombre} {apellido}"
                cuerpo = f"Hola Admin,\nSoy {nombre} {apellido}.\nCédula: {cedula}\nDirección: {direccion}\nPlaca: {placa}\n\nADJUNTO MIS 5 REQUISITOS."
                link_email = f"mailto:{EMAIL_ADMIN}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                link_gmail = f"https://mail.google.com/mail/?view=cm&fs=1&to={EMAIL_ADMIN}&su={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                
                st.markdown("""
                <div style='background-color:#E3F2FD; padding:20px; border-radius:10px; border:1px solid #BBDEFB;'>
                    <h3 style='color:#0D47A1; text-align:center;'>📨 ÚLTIMO PASO: ENVIAR REQUISITOS</h3>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                c1.markdown(f'<a href="{link_email}" style="background-color:#0277BD; color:white; padding:15px; display:block; text-align:center; text-decoration:none; border-radius:10px; font-weight:bold;">📱 CELULAR</a>', unsafe_allow_html=True)
                c2.markdown(f'<a href="{link_gmail}" target="_blank" style="background-color:#DB4437; color:white; padding:15px; display:block; text-align:center; text-decoration:none; border-radius:10px; font-weight:bold;">💻 COMPUTADORA</a>', unsafe_allow_html=True)
            else:
                st.error(f"Error: {resultado}")
