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

if enviar:
    if not nombre or not email or not clave or not placa or not direccion:
        st.error("❌ Faltan datos obligatorios (incluida la dirección).")
    elif not acepto:
        st.warning("⚠️ Debes aceptar los términos.")
    else:
        with st.spinner("Guardando registro..."):
            resultado = registrar_chofer(nombre, apellido, cedula, email, direccion, telefono, placa, clave)
            
            if "REGISTRO_OK" in resultado:
                st.success("✅ ¡DATOS GUARDADOS!")
                st.balloons()
                
                # --- PREPARAR CORREOS ---
                asunto = f"ALTA NUEVO SOCIO - {nombre} {apellido}"
                cuerpo = f"""Hola Admin,
Soy {nombre} {apellido}.
Cédula: {cedula}
Dirección: {direccion}
Placa: {placa}

ADJUNTO MIS 5 REQUISITOS (Fotos).
"""
                link_email = f"mailto:{EMAIL_ADMIN}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                link_gmail = f"https://mail.google.com/mail/?view=cm&fs=1&to={EMAIL_ADMIN}&su={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                
                # --- CAJA AZUL DE REQUISITOS ---
                st.markdown("""
                <div style='background-color:#E3F2FD; padding:20px; border-radius:10px; border:1px solid #BBDEFB;'>
                    <h3 style='color:#0D47A1; text-align:center;'>📨 ÚLTIMO PASO: ENVIAR REQUISITOS</h3>
                    <p style='text-align:center;'><b>Debes adjuntar OBLIGATORIAMENTE estas 5 fotos:</b></p>
                    <ul style='color:#0D47A1; font-weight:bold;'>
                        <li>1. Foto de Perfil (Rostro) 👤</li>
                        <li>2. Foto del Vehículo 🚖</li>
                        <li>3. Foto de la Cédula de Identidad 🆔</li>
                        <li>4. Foto de la Matrícula del Vehículo 📄</li>
                        <li>5. Foto de la Licencia de Conducir 💳</li>
                    </ul>
                    <hr>
                    <p style='text-align:center;'>Elige una opción para enviar:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # --- BOTONES CLAROS ---
                c1, c2 = st.columns(2)
                
                # Botón Azul (Celular)
                c1.markdown(f"""
                <a href="{link_email}" style="
                    background-color:#0277BD; color:white; padding:15px; 
                    display:block; text-align:center; text-decoration:none; 
                    border-radius:10px; font-weight:bold;">
                    📱 DESDE EL CELULAR
                </a>
                <p style="text-align:center; font-size:12px; color:gray;">(Usa la App de Correo)</p>
                """, unsafe_allow_html=True)

                # Botón Rojo (PC)
                c2.markdown(f"""
                <a href="{link_gmail}" target="_blank" style="
                    background-color:#DB4437; color:white; padding:15px; 
                    display:block; text-align:center; text-decoration:none; 
                    border-radius:10px; font-weight:bold;">
                    💻 DESDE COMPUTADORA
                </a>
                <p style="text-align:center; font-size:12px; color:gray;">(Abre Gmail Web)</p>
                """, unsafe_allow_html=True)

                # --- MENSAJE DE RESPALDO ---
                st.write("") 
                st.warning(f"⚠️ **¿Problemas con los botones?**\nSi ninguna opción funciona, envía tus 5 fotos manualmente a nuestro correo: **{EMAIL_ADMIN}**")
                
            else:
                st.error(f"Error al registrar: {resultado}")
