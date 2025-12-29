import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import re
from datetime import datetime

# --- ⚙️ CONFIGURACIÓN ---
DEUDA_MAXIMA = 10.00        
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwzOVH8c8f9WEoE4OJOTIccz_EgrOpZ8ySURTVRwi0bnQhFnWVdgfX1W8ivTIu5dFfs/exec"

# --- 🛠️ FUNCIONES ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

def enviar_datos(datos):
    try:
        params = urllib.parse.urlencode(datos)
        url_final = f"{URL_SCRIPT}?{params}"
        with urllib.request.urlopen(url_final) as response: return response.read().decode('utf-8')
    except: return "Error"

# --- 📱 INTERFAZ ---
st.title("🚖 Portal de Socios")

if 'usuario_activo' not in st.session_state: st.session_state.usuario_activo = False

if st.session_state.usuario_activo:
    # --- PANEL DEL SOCIO (Sin cambios en tu configuración de perfil) ---
    df_fresh = cargar_datos("CHOFERES")
    u = st.session_state.datos_usuario
    fila = df_fresh[(df_fresh['Nombre'] == u['Nombre']) & (df_fresh['Apellido'] == u['Apellido'])]
    
    if not fila.empty:
        foto_raw = str(fila['Foto_Perfil'].values[0])
        estado = str(fila['Estado'].values[0])
        km = float(fila['KM_ACUMULADOS'].values[0])
        deuda = float(fila['DEUDA'].values[0])

        if "http" in foto_raw:
            match = re.search(r'[-\w]{25,}', foto_raw)
            id_f = match.group() if match else ""
            foto_f = f"https://lh3.googleusercontent.com/u/0/d/{id_f}"
            st.markdown(f'<div style="text-align:center;margin-bottom:20px;"><img src="{foto_f}" style="width:145px;height:145px;border-radius:50%;object-fit:cover;border:5px solid #25D366;"></div>', unsafe_allow_html=True)
        
        st.success(f"✅ Socio: **{u['Nombre']} {u['Apellido']}**")
        c1, c2 = st.columns(2)
        c1.metric("🛣️ KM Totales", f"{km:.2f} km")
        c2.metric("💸 Deuda Actual", f"${deuda:.2f}")

    if st.button("🔒 CERRAR SESIÓN"):
        st.session_state.usuario_activo = False
        st.rerun()

else:
    tab_log, tab_reg = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])
    
    with tab_log:
        l_nom = st.text_input("Nombre", key="log_nom")
        l_ape = st.text_input("Apellido", key="log_ape")
        l_pass = st.text_input("Contraseña", type="password")
        
        if st.button("ENTRAR", type="primary"):
            df = cargar_datos("CHOFERES")
            match = df[(df['Nombre'].astype(str).str.upper() == l_nom.upper()) & (df['Apellido'].astype(str).str.upper() == l_ape.upper())]
            if not match.empty and str(match.iloc[0]['Clave']) == l_pass:
                st.session_state.usuario_activo = True
                st.session_state.datos_usuario = match.iloc[0].to_dict()
                st.rerun()
            else: st.error("Datos incorrectos")
        
        # --- NUEVA RECUPERACIÓN POR EMAIL ---
        st.divider()
        st.write("¿Olvidaste tu clave?")
        if st.button("📩 ENVIAR MIS DATOS AL CORREO"):
            if l_nom and l_ape:
                res = enviar_datos({
                    "accion": "recuperar_clave_email",
                    "nombre": l_nom,
                    "apellido": l_ape
                })
                st.info("Si los datos son correctos, recibirás un email en pocos minutos.")
            else:
                st.warning("Escribe tu Nombre y Apellido arriba para buscar tu cuenta.")

    with tab_reg:
        # Registro (Manteniendo tus campos de 18 columnas)
        with st.form("registro_socio"):
            r_nom = st.text_input("Nombres *")
            r_ape = st.text_input("Apellidos *")
            r_email = st.text_input("Correo Electrónico *")
            r_pass = st.text_input("Contraseña *", type="password")
            if st.form_submit_button("✅ REGISTRARME"):
                enviar_datos({"accion": "registrar_conductor", "nombre": r_nom, "apellido": r_ape, "email": r_email, "clave": r_pass})
                st.success("Registro enviado.")
