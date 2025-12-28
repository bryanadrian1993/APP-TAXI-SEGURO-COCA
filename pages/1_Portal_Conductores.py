import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse

st.set_page_config(page_title="Registro Conductores", layout="centered")

# --- CONFIGURACIÓN ---
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwI2zteeExU_Zy2yHLMR3A49ZYSHwP_xNGsTy-AuRiD_6llZA6V_QxvvOYiXD48w2uc/exec"
EMAIL_ADMIN = "taxi-seguroecuador@hotmail.com"

st.image("https://cdn-icons-png.flaticon.com/512/2083/2083260.png", width=100)
st.title("📝 REGISTRO DE SOCIOS")

def registrar_chofer(nombre, apellido, cedula, email, telefono, placa, clave):
    try:
        params = {
            "accion": "registro",
            "nombre": nombre, "apellido": apellido,
            "cedula": cedula, "email": email,
            "telefono": telefono, "placa": placa, "clave": clave
        }
        query_string = urllib.parse.urlencode(params)
        url_final = f"{URL_SCRIPT}?{query_string}"
        
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

# --- FORMULARIO ---
with st.form("form_registro"):
    st.write("👤 **Datos Personales**")
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombres:")
    apellido = c2.text_input("Apellidos:")
    cedula = st.text_input("Cédula / Identificación:")
    
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

if enviar:
    if not nombre or not email or not clave or not placa:
        st.error("❌ Faltan datos obligatorios.")
    elif not acepto:
        st.warning("⚠️ Debes aceptar los términos.")
    else:
        with st.spinner("Guardando registro..."):
            resultado = registrar_chofer(nombre, apellido, cedula, email, telefono, placa, clave)
            
            if "REGISTRO_OK" in resultado:
                st.success("✅ ¡DATOS GUARDADOS!")
                st.balloons()
                
                # --- PREPARAR CORREOS ---
                asunto = f"ALTA NUEVO SOCIO - {nombre} {apellido}"
                cuerpo = f"""Hola Admin,
Soy {nombre} {apellido}.
Cédula: {cedula}
Placa: {placa}

ADJUNTO FOTOS (Licencia, Auto, Matrícula).
"""
                # 1. ENLACE ESTÁNDAR (Para celulares y Outlook) - SIN TARGET BLANK
                link_email = f"mailto:{EMAIL_ADMIN}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                
                # 2. ENLACE GMAIL WEB (Para computadoras)
                link_gmail = f"https://mail.google.com/mail/?view=cm&fs=1&to={EMAIL_ADMIN}&su={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                
                st.markdown("""
                <div style='background-color:#E3F2FD; padding:20px; border-radius:10px; border:1px solid #BBDEFB; text-align:center;'>
                    <h3 style='color:#0D47A1;'>📨 ÚLTIMO PASO: ENVIAR FOTOS</h3>
                    <p>Elige una opción para adjuntar tus fotos:</p>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                
                # Botón 1: App de Correo (Celulares)
                c1.markdown(f"""
                <a href="{link_email}" style="
                    background-color:#0277BD; color:white; padding:15px; 
                    display:block; text-align:center; text-decoration:none; 
                    border-radius:10px; font-weight:bold;">
                    📱 APP DE CORREO
                </a>
                """, unsafe_allow_html=True)

                # Botón 2: Gmail Web (Computadoras)
                c2.markdown(f"""
                <a href="{link_gmail}" target="_blank" style="
                    background-color:#DB4437; color:white; padding:15px; 
                    display:block; text-align:center; text-decoration:none; 
                    border-radius:10px; font-weight:bold;">
                    📧 USAR GMAIL WEB
                </a>
                """, unsafe_allow_html=True)
                
                st.info(f"Si nada funciona, envía las fotos manualmente a: **{EMAIL_ADMIN}**")
                
            else:
                st.error(f"Error al registrar: {resultado}")
