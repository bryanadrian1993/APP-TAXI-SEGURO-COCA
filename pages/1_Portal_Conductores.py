import streamlit as st
import urllib.request
import urllib.parse

st.set_page_config(page_title="Portal Socios", layout="wide")

URL_SCRIPT = "TU_NUEVA_URL_DE_APPS_SCRIPT"

# --- FUNCIÓN DE ENVÍO ---
def actualizar_estado_en_sheets(nombre_completo, nuevo_estado):
    try:
        params = {"accion": "actualizar_estado", "nombre": nombre_completo, "estado": nuevo_estado}
        url_final = f"{URL_SCRIPT}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

# --- INICIALIZACIÓN DE SESIÓN (Cura el NameError) ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False

# --- INTERFAZ ---
if not st.session_state.conectado:
    st.subheader("🔑 Ingreso de Socio")
    col1, col2 = st.columns(2)
    nom = col1.text_input("Nombre (como registró):")
    ape = col2.text_input("Apellido (como registró):")
    if st.button("INGRESAR"):
        if nom and ape:
            st.session_state.conectado = True
            st.session_state.usuario_completo = f"{nom} {ape}".upper()
            st.rerun()
else:
    st.success(f"Socio: **{st.session_state.usuario_completo}**")
    c1, c2 = st.columns(2)
    
    if c1.button("🟢 ESTOY LIBRE", use_container_width=True):
        res = actualizar_estado_en_sheets(st.session_state.usuario_completo, "LIBRE")
        if "OK" in res: st.toast("✅ Excel actualizado: LIBRE")
            
    if c2.button("🔴 ESTOY OCUPADO", use_container_width=True):
        res = actualizar_estado_en_sheets(st.session_state.usuario_completo, "OCUPADO")
        if "OK" in res: st.toast("✅ Excel actualizado: OCUPADO")

    if st.button("Cerrar Sesión"):
        st.session_state.conectado = False
        st.rerun()
