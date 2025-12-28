import streamlit as st
import urllib.parse

# Configuración de la pestaña independiente
st.set_page_config(page_title="Registro de Socios", page_icon="📝")

# Correo de destino
EMAIL_ADMIN = "taxi-seguroecuador@hotmail.com"

st.markdown("<h1 style='text-align: center;'>📝 REGISTRO DE NUEVOS SOCIOS</h1>", unsafe_allow_html=True)
st.write("Complete todos los campos y luego use los botones para enviar sus documentos.")

# --- FORMULARIO CON TODOS LOS CAMPOS SOLICITADOS ---
with st.form("registro_socio"):
    col1, col2 = st.columns(2)
    with col1:
        nombres = st.text_input("Nombres Completos:")
        cedula = st.text_input("Número de Cédula:")
        email = st.text_input("Correo Electrónico:")
    with col2:
        apellidos = st.text_input("Apellidos Completos:")
        telefono = st.text_input("Número de WhatsApp:")
        placa = st.text_input("Placa del Vehículo:")
    
    direccion = st.text_area("Dirección Domiciliaria:")
    
    st.info("⚠️ Al hacer clic en GUARDAR, se activarán los botones para enviar sus 5 requisitos.")
    guardar = st.form_submit_button("🚀 GUARDAR DATOS Y PREPARAR ENVÍO")

# --- LÓGICA DE ENVÍO ---
if guardar:
    if not nombres or not cedula or not placa:
        st.error("❌ Por favor complete los campos obligatorios (Nombres, Cédula y Placa).")
    else:
        st.success(f"✅ ¡Datos listos! Ahora envíe sus documentos por correo.")
        
        asunto = f"REGISTRO NUEVO CONDUCTOR - {nombres} {apellidos}"
        cuerpo = f"""Deseo registrarme como socio conductor:
        
- Nombre: {nombres} {apellidos}
- Cédula: {cedula}
- Correo: {email}
- Teléfono: {telefono}
- Dirección: {direccion}
- Placa: {placa}

Adjunto las 5 fotos de requisitos:
1. Foto de Perfil
2. Foto del Vehículo
3. Foto de la Cédula
4. Foto de la Matrícula
5. Foto de la Licencia"""

        mailto_link = f"mailto:{EMAIL_ADMIN}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
        gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to={EMAIL_ADMIN}&su={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"

        st.divider()
        st.markdown("### 📸 PASO FINAL: ENVIAR 5 REQUISITOS")
        
        # Botones con los colores exactos solicitados
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.markdown(f'''
                <a href="{mailto_link}" style="text-decoration:none;">
                    <div style="background-color:#0277BD; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">
                        📱 ENVIAR DESDE CELULAR
                    </div>
                </a>''', unsafe_allow_html=True)
        with col_btn2:
            st.markdown(f'''
                <a href="{gmail_link}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#DB4437; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">
                        💻 ENVIAR DESDE GMAIL (PC)
                    </div>
                </a>''', unsafe_allow_html=True)
