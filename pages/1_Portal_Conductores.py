import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse

st.set_page_config(page_title="Registro Conductores", layout="centered")

# --- CONFIGURACIÓN ---
# 👇 TU ROBOT (Ya configurado)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwI2zteeExU_Zy2yHLMR3A49ZYSHwP_xNGsTy-AuRiD_6llZA6V_QxvvOYiXD48w2uc/exec"

# 👇 TU CORREO (Donde llegarán las fotos)
EMAIL_ADMIN = "taxi-seguroecuador@hotmail.com"

st.image("https://cdn-icons-png.flaticon.com/512/2083/2083260.png", width=100)
st.title("📝 REGISTRO DE SOCIOS")
st.markdown("Únete a la plataforma **TAXI SEGURO COCA**.")

def registrar_chofer(nombre, apellido, cedula, email, telefono, placa, clave):
    try:
        # Empaquetamos los datos nuevos
        params = {
            "accion": "registro",
            "nombre": nombre, "apellido": apellido,
            "cedula": cedula, "email": email,
            "telefono": telefono, "placa": placa, "clave": clave
        }
        # Enviamos al Robot
        query_string = urllib.parse.urlencode(params)
        url_final = f"{URL_SCRIPT}?{query_string}"
        
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

# --- FORMULARIO EN PANTALLA ---
with st.form("form_registro"):
    st.write("👤 **Datos Personales**")
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombres:")
    apellido = c2.text_input("Apellidos:")
    cedula = st.text_input("Cédula / Identificación:")
    
    st.write("📧 **Contacto**")
    email = st.text_input("Tu Correo Electrónico (Obligatorio):")
    telefono = st.text_input("Celular (ej: 5939...):")
    
    st.write("🚖 **Datos del Vehículo**")
    placa = st.text_input("Placa del Vehículo:")
    
    st.write("🔐 **Seguridad**")
    st.info("Crea una contraseña para entrar a tu perfil.")
    clave = st.text_input("Contraseña:", type="password")
    
    acepto = st.checkbox("Declaro que mis documentos están vigentes.")
    
    enviar = st.form_submit_button("🚀 GUARDAR DATOS")

if enviar:
    # Validamos que no falte nada importante
    if not nombre or not apellido or not email or not clave or not placa:
        st.error("❌ Por favor llena todos los campos.")
    elif not acepto:
        st.warning("⚠️ Debes aceptar los términos.")
    else:
        with st.spinner("Guardando registro en la base de datos..."):
            resultado = registrar_chofer(nombre, apellido, cedula, email, telefono, placa, clave)
            
            if "REGISTRO_OK" in resultado:
                st.success("✅ ¡DATOS GUARDADOS CORRECTAMENTE!")
                st.balloons()
                
                # --- PREPARAR EL CORREO AUTOMÁTICO ---
                asunto = f"ALTA NUEVO SOCIO - {nombre} {apellido}"
                cuerpo = f"""Hola Administración,
Soy {nombre} {apellido}.
Cédula: {cedula}
Email: {email}
Placa: {placa}
Teléfono: {telefono}

ADJUNTO A ESTE CORREO MIS FOTOS PARA VALIDACIÓN:
1. Foto de Perfil
2. Foto del Vehículo (Placa: {placa})
3. Foto de la Matrícula
4. Licencia Profesional

Quedo a la espera de mi activación.
"""
                # Creamos el enlace mágico "mailto"
                link_email = f"mailto:{EMAIL_ADMIN}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                
                st.markdown("""
                <div style='background-color:#E3F2FD; padding:20px; border-radius:10px; border:1px solid #BBDEFB; text-align:center;'>
                    <h3 style='color:#0D47A1;'>📨 ÚLTIMO PASO OBLIGATORIO</h3>
                    <p>Tus datos ya están en el sistema.</p>
                    <p>Ahora toca el botón azul para <b>enviarnos las fotos</b> de tus documentos por correo.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # BOTÓN GRANDE
                st.markdown(f"""
                <a href="{link_email}" target="_blank" style="
                    background-color:#0277BD; color:white; padding:20px; 
                    display:block; text-align:center; text-decoration:none; 
                    border-radius:10px; font-weight:bold; font-size:18px; margin-top:15px;">
                    📧 ADJUNTAR FOTOS Y ENVIAR
                </a>
                """, unsafe_allow_html=True)
                
            else:
                st.error(f"Error al registrar: {resultado}")
