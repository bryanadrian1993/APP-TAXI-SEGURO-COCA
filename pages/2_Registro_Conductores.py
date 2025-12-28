import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="Registro de Socios", page_icon="📝")

# --- CONFIGURACIÓN ---
# Asegúrate de que esta URL sea la de tu Google Apps Script actualizado
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwI2zteeExU_Zy2yHLMR3A49ZYSHwP_xNGsTy-AuRiD_6llZA6V_QxvvOYiXD48w2uc/exec"
EMAIL_ADMIN = "taxi-seguroecuador@hotmail.com"

st.image("https://cdn-icons-png.flaticon.com/512/2083/2083260.png", width=100)
st.title("📝 REGISTRO DE NUEVOS SOCIOS")
st.write("Completa tus datos para unirte a la flota de Taxi Seguro Coca.")

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

# --- FORMULARIO ---
with st.form("form_registro"):
    st.subheader("👤 Datos Personales")
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombres:")
    apellido = c2.text_input("Apellidos:")
    cedula = st.text_input("Número de Cédula:")
    
    st.subheader("🏠 Ubicación y Contacto")
    direccion = st.text_input("Dirección Domiciliaria Exacta:")
    email = st.text_input("Correo Electrónico:")
    telefono = st.text_input("Número de Celular (WhatsApp):")
    
    st.subheader("🚖 Información del Vehículo")
    placa = st.text_input("Número de Placa:")
    
    st.subheader("🔐 Seguridad")
    st.info("Esta clave te servirá para entrar al Portal de Conductores después.")
    clave = st.text_input("Crea una contraseña:", type="password")
    
    acepto = st.checkbox("Declaro que la información es real y mis documentos están vigentes.")
    
    enviar = st.form_submit_button("🚀 GUARDAR DATOS Y CONTINUAR")

if enviar:
    if not nombre or not email or not clave or not placa or not direccion:
        st.error("❌ Por favor, completa todos los campos obligatorios.")
    elif not acepto:
        st.warning("⚠️ Debes aceptar la declaración para continuar.")
    else:
        with st.spinner("Guardando registro en la base de datos..."):
            resultado = registrar_chofer(nombre, apellido, cedula, email, direccion, telefono, placa, clave)
            
            if "REGISTRO_OK" in resultado:
                st.success("✅ ¡DATOS GUARDADOS CORRECTAMENTE!")
                st.balloons()
                
                # --- PREPARACIÓN DEL CORREO DE REQUISITOS ---
                asunto = f"REQUISITOS NUEVO SOCIO - {nombre} {apellido}"
                cuerpo = f"""Hola, adjunto mis documentos para la validación:
- Nombre: {nombre} {apellido}
- Cédula: {cedula}
- Placa: {placa}
- Dirección: {direccion}

(Adjunto aquí las 5 fotos solicitadas)"""

                # Enlaces para envío
                link_mail_app = f"mailto:{EMAIL_ADMIN}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                link_gmail_web = f"https://mail.google.com/mail/?view=cm&fs=1&to={EMAIL_ADMIN}&su={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                
                # --- CUADRO DE INSTRUCCIONES FINALES ---
                st.markdown(f"""
                <div style='background-color:#FFF3E0; padding:20px; border-radius:10px; border:1px solid #FFB74D;'>
                    <h3 style='color:#E65100; text-align:center;'>📩 ÚLTIMO PASO OBLIGATORIO</h3>
                    <p style='text-align:center;'>Para activar tu cuenta, debes enviar las <b>5 fotos</b> de tus documentos:</p>
                    <ul style='font-weight:bold;'>
                        <li>1. Foto de Perfil</li>
                        <li>2. Foto del Vehículo</li>
                        <li>3. Foto de la Cédula</li>
                        <li>4. Foto de la Matrícula</li>
                        <li>5. Foto de la Licencia</li>
                    </ul>
                    <hr>
                    <p style='text-align:center;'>Haz clic en el botón según donde estés ahora:</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns(2)
                
                # Botón para Celular
                col_btn1.markdown(f"""
                <a href="{link_mail_app}" style="background-color:#0277BD; color:white; padding:15px; display:block; text-align:center; text-decoration:none; border-radius:10px; font-weight:bold;">📱 ENVIAR DESDE CELULAR</a>
                """, unsafe_allow_html=True)

                # Botón para Computadora
                col_btn2.markdown(f"""
                <a href="{link_gmail_web}" target="_blank" style="background-color:#DB4437; color:white; padding:15px; display:block; text-align:center; text-decoration:none; border-radius:10px; font-weight:bold;">💻 ENVIAR DESDE PC (GMAIL)</a>
                """, unsafe_allow_html=True)
                
                st.warning(f"Si los botones no abren, envía las fotos manualmente a: **{EMAIL_ADMIN}**")
            else:
                st.error(f"Hubo un problema: {resultado}")
