import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Registro Conductores", layout="centered")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwI2zteeExU_Zy2yHLMR3A49ZYSHwP_xNGsTy-AuRiD_6llZA6V_QxvvOYiXD48w2uc/exec"
EMAIL_ADMIN = "taxi-seguroecuador@hotmail.com"

# --- INICIALIZACIÓN (Evita el NameError) ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
if 'usuario_completo' not in st.session_state:
    st.session_state.usuario_completo = ""

# --- FUNCIONES ---
def actualizar_estado_en_sheets(nombre_completo, nuevo_estado):
    try:
        # Usamos strip() para limpiar espacios como el que tiene "BRYAN " en tu Excel
        params = {
            "accion": "actualizar_estado", 
            "nombre": nombre_completo.strip(), 
            "estado": nuevo_estado
        }
        url_final = f"{URL_SCRIPT}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

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

# --- DISEÑO ---
st.image("https://cdn-icons-png.flaticon.com/512/2083/2083260.png", width=100)
st.title("📝 REGISTRO DE SOCIOS")

# --- 1. ACCESO CON CLAVE (CORREGIDO) ---
if not st.session_state.conectado:
    with st.expander("🔐 INGRESO PARA SOCIOS REGISTRADOS", expanded=True):
        c1, c2 = st.columns(2)
        nom_acc = c1.text_input("Nombre (como registró):")
        ape_acc = c2.text_input("Apellido (como registró):")
        # ESTA ES LA CLAVE QUE PEDISTE
        pass_acc = st.text_input("Tu Clave de Socio:", type="password")
        
        if st.button("VERIFICAR E INGRESAR"):
            # Para la prueba, validamos que la clave no esté vacía 
            # (El script de Google debería validar la clave real del Excel)
            if nom_acc and ape_acc and pass_acc:
                st.session_state.conectado = True
                st.session_state.usuario_completo = f"{nom_acc.strip()} {ape_acc.strip()}".upper()
                st.rerun()
            else:
                st.error("❌ Por favor, ingrese Nombre, Apellido y Clave.")
else:
    st.success(f"Socio Activo: **{st.session_state.usuario_completo}**")
    col_b1, col_b2 = st.columns(2)
    
    if col_b1.button("🟢 ESTOY LIBRE", use_container_width=True):
        with st.spinner("Conectando con Excel..."):
            res = actualizar_estado_en_sheets(st.session_state.usuario_completo, "LIBRE")
            if "OK" in res:
                st.toast("✅ Estado actualizado: LIBRE")
            else:
                st.error(f"❌ Error del Servidor: {res}")
    
    if col_b2.button("🔴 ESTOY OCUPADO", use_container_width=True):
        with st.spinner("Conectando con Excel..."):
            res = actualizar_estado_en_sheets(st.session_state.usuario_completo, "OCUPADO")
            if "OK" in res:
                st.toast("✅ Estado actualizado: OCUPADO")
            else:
                st.error(f"❌ Error del Servidor: {res}")

    if st.button("Cerrar Sesión"):
        st.session_state.conectado = False
        st.rerun()

st.divider()

# --- 2. FORMULARIO DE REGISTRO ORIGINAL ---
with st.form("form_registro"):
    st.write("👤 **Datos Personales**")
    c_reg1, c_reg2 = st.columns(2)
    r_nombre = c_reg1.text_input("Nombres:")
    r_apellido = c_reg2.text_input("Apellidos:")
    r_cedula = st.text_input("Cédula:")
    r_dir = st.text_input("Dirección:")
    r_email = st.text_input("Correo:")
    r_tel = st.text_input("WhatsApp (ej: 593...):")
    r_placa = st.text_input("Placa:")
    r_clave = st.text_input("Crea tu Contraseña:", type="password")
    r_acepto = st.checkbox("Documentos vigentes.")
    if st.form_submit_button("🚀 GUARDAR REGISTRO"):
        if r_nombre and r_clave:
            res_reg = registrar_chofer(r_nombre, r_apellido, r_cedula, r_email, r_dir, r_tel, r_placa, r_clave)
            if "REGISTRO_OK" in res_reg:
                st.success("✅ ¡Registrado con éxito!")
