import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse

st.set_page_config(page_title="Registro Conductores", layout="centered")

# --- CONFIGURACIÓN ---
# 👇 AQUÍ YA PUSE TU ENLACE DEL ROBOT (NO LO TOQUES, YA ESTÁ LISTO)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwI2zteeExU_Zy2yHLMR3A49ZYSHwP_xNGsTy-AuRiD_6llZA6V_QxvvOYiXD48w2uc/exec"

# 👇 TU CORREO PARA RECIBIR LAS FOTOS
EMAIL_ADMIN = "taxi-seguroecuador@hotmail.com"

st.image("https://cdn-icons-png.flaticon.com/512/2083/2083260.png", width=100)
st.title("📝 REGISTRO DE SOCIOS")
st.markdown("Únete a la plataforma **TAXI SEGURO COCA**.")

def registrar_chofer(nombre, apellido, cedula, telefono, placa, clave):
    try:
        # Preparamos los datos para enviarlos al Robot
        params = {
            "accion": "registro",
            "nombre": nombre, "apellido": apellido,
            "cedula": cedula, "telefono": telefono,
            "placa": placa, "clave": clave
        }
        query_string = urllib.parse.urlencode(params)
        url_final = f"{URL_SCRIPT}?{query_string}"
        
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

# --- FORMULARIO ---
with st.form("form_registro"):
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombres:")
    apellido = c2.text_input("Apellidos:")
    
    cedula = st.text_input("Cédula / Identificación:")
    telefono = st.text_input("Celular (con código país, ej: 593...):")
    placa = st.text_input("Placa del Vehículo:")
    
    st.info("🔐 Crea una contraseña segura para entrar a tu perfil.")
    clave = st.text_input("Contraseña Personal:", type="password")
    
    # Checkbox de términos
    acepto = st.checkbox("Declaro que mis documentos están vigentes.")
    
    enviar = st.form_submit_button("🚀 GUARDAR Y CONTINUAR")

if enviar:
    if not nombre or not apellido or not cedula or not clave:
        st.error("❌ Faltan datos obligatorios.")
    elif not acepto:
        st.warning("⚠️ Debes aceptar los términos.")
    else:
        with st.spinner("Guardando tus datos en el sistema..."):
            resultado = registrar_chofer(nombre, apellido, cedula, telefono, placa, clave)
            
            if "REGISTRO_OK" in resultado:
                st.success("✅ ¡DATOS GUARDADOS CORRECTAMENTE!")
                st.balloons()
                
                # --- PREPARAR CORREO AUTOMÁTICO ---
                asunto = f"DOCUMENTOS NUEVO SOCIO - {nombre} {apellido}"
                cuerpo = f"""Hola Administración,
Soy {nombre} {apellido} (Cédula: {cedula}).
He completado mi registro en la App Taxi Seguro.

ADJUNTO A ESTE CORREO MIS FOTOS PARA VALIDACIÓN:
1. Foto de Perfil
2. Foto del Vehículo (Placa: {placa})
3. Foto de la Matrícula
4. Licencia Profesional

Quedo a la espera de mi activación.
"""
                # Creamos el enlace "mailto" seguro
                link_email = f"mailto:{EMAIL_ADMIN}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                
                st.markdown("""
                <div style='background-color:#E3F2FD; padding:15px; border-radius:10px; border:1px solid #BBDEFB; color: #0D47A1;'>
                    <h3>📨 ÚLTIMO PASO: ENVIAR FOTOS</h3>
                    <p>Para activar tu cuenta, debes enviar las fotos de tus documentos al correo del administrador.</p>
                    <ol>
                        <li>Toca el botón de abajo.</li>
                        <li>Se abrirá tu correo automáticamente.</li>
                        <li><b>Adjunta las fotos</b> (clip 📎) y envía.</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón grande
                st.markdown(f'<a href="{link_email}" target="_blank" style="background-color:#0277BD; color:white; padding:15px; display:block; text-align:center; text-decoration:none; border-radius:10px; font-weight:bold; margin-top:10px; font-size:18px;">📧 ADJUNTAR FOTOS Y ENVIAR CORREO</a>', unsafe_allow_html=True)
            else:
                st.error(f"Error al registrar: {resultado}")
