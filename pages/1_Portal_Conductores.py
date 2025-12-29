import streamlit as st
import urllib.parse
import urllib.request

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Registro Conductores", page_icon="📝")

# TU NUEVO URL DEL SCRIPT (Asegúrate de que sea el correcto)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyzzpVm-dlOu8ZGbPUGfOnq-joRYoV-wXuckOvgsmKRAbRZaJQHJ6k9uxfA4pU9EK0d/exec"

# --- LISTAS DE OPCIONES ---
PAISES = ["Ecuador", "Colombia", "Perú", "México", "España", "USA"]
IDIOMAS = ["Español", "English", "Português", "Français"]
VEHICULOS = ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"]

def enviar_datos(datos):
    try:
        params = urllib.parse.urlencode(datos)
        url_final = f"{URL_SCRIPT}?{params}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

# --- INTERFAZ DEL FORMULARIO ---
st.title("📝 Registro Oficial de Socio")
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

    st.caption("Al registrarte aceptas los términos y condiciones de la plataforma.")
    
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
                    "nombre": nombre,
                    "apellido": apellido,
                    "cedula": cedula,
                    "email": email,
                    "direccion": direccion,
                    "telefono": telefono,
                    "placa": placa,
                    "clave": clave,
                    "pais": pais,
                    "idioma": idioma,
                    "tipo_veh": tipo_veh
                }
                
                respuesta = enviar_datos(datos)
                
                if "REGISTRO_EXITOSO" in respuesta:
                    st.balloons()
                    st.success("🎉 ¡REGISTRO EXITOSO!")
                    st.info("Tu cuenta está ACTIVA. Ya puedes recibir pedidos.")
                else:
                    st.error(f"Error de conexión: {respuesta}")
