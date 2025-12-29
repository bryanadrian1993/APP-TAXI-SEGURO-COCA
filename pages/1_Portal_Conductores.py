import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import base64
import os
from datetime import datetime

# --- ⚙️ CONFIGURACIÓN ---
st.set_page_config(page_title="Portal Socios", page_icon="🚖", layout="centered")
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwzOVH8c8f9WEoE4OJOTIccz_EgrOpZ8ySURTVRwi0bnQhFnWVdgfX1W8ivTIu5dFfs/exec"
DEUDA_MAXIMA = 10.00
NUMERO_DEUNA = "09XXXXXXXX" # Tu número de Deuna

# --- 🛠️ FUNCIONES ---
def cargar_datos(hoja):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}"
        return pd.read_csv(url)
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
    # PANEL CONDUCTOR LOGUEADO
    df = cargar_datos("CHOFERES")
    u = st.session_state.datos_usuario
    # Buscamos la fila actualizada por Nombre y Apellido
    fila = df[(df['Nombre'] == u['Nombre']) & (df['Apellido'] == u['Apellido'])]
    
    # Basado en tu Excel (Índices empiezan en 0):
    # Col 16: KM_ACUMULADOS | Col 17: DEUDA
    km = float(fila.iloc[0, 16]) if not fila.empty else 0.0
    deuda = float(fila.iloc[0, 17]) if not fila.empty else 0.0
    bloqueado = deuda >= DEUDA_MAXIMA

    st.success(f"✅ Socio: **{u['Nombre']} {u['Apellido']}**")
    
    if bloqueado:
        st.error(f"⛔ CUENTA BLOQUEADA POR DEUDA: ${deuda:.2f}")
        if st.button("📱 MOSTRAR QR DEUNA"):
            if os.path.exists("qr_deuna.png"):
                with open("qr_deuna.png", "rb") as f:
                    data = base64.b64encode(f.read()).decode()
                st.markdown(f'<img src="data:image/png;base64,{data}" width="100%">', unsafe_allow_html=True)
            else: st.warning("Imagen QR no encontrada.")
    else:
        st.metric("💸 Deuda Actual", f"${deuda:.2f}")
        st.info(f"Estado: {fila.iloc[0, 8]}") # Columna 8: Estado

    if st.button("🔒 CERRAR SESIÓN"):
        st.session_state.usuario_activo = False
        st.rerun()

else:
    tab_log, tab_reg = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])

    with tab_log:
        l_nom = st.text_input("Nombre")
        l_ape = st.text_input("Apellido")
        l_pass = st.text_input("Contraseña", type="password")
        if st.button("ENTRAR"):
            df = cargar_datos("CHOFERES")
            match = df[(df['Nombre'].astype(str).str.upper() == l_nom.upper()) & 
                       (df['Apellido'].astype(str).str.upper() == l_ape.upper())]
            if not match.empty and str(match.iloc[0]['Clave']) == l_pass:
                st.session_state.usuario_activo = True
                st.session_state.datos_usuario = match.iloc[0].to_dict()
                st.rerun()
            else: st.error("Datos incorrectos")

    with tab_reg:
        with st.form("reg_socio"):
            r_nom = st.text_input("Nombre *")
            r_ape = st.text_input("Apellido *")
            r_ced = st.text_input("Cédula *")
            r_ema = st.text_input("Email *")
            r_dir = st.text_input("Dirección *")
            
            # WhatsApp con Selector de País
            col_p, col_n = st.columns([1, 2])
            pref = col_p.selectbox("País", ["+593 (Ecuador)", "+57 (Col)", "+51 (Perú)", "+1 (USA)", "Otro"])
            telf = col_n.text_input("WhatsApp (Sin código) *")
            
            r_pla = st.text_input("Placa *")
            r_cla = st.text_input("Crear Contraseña *", type="password")
            
            if st.form_submit_button("COMPLETAR REGISTRO"):
                if r_nom and telf and r_cla:
                    # Lógica "Sin código": Unimos el prefijo elegido con el número limpio
                    p_num = pref.split(" ")[0].replace("+", "")
                    n_num = ''.join(filter(str.isdigit, telf))
                    if n_num.startswith("0"): n_num = n_num[1:] # Quitamos el 0 inicial si lo ponen
                    tel_final = p_num + n_num
                    
                    res = enviar_datos({
                        "accion": "registrar_conductor",
                        "nombre": r_nom, "apellido": r_ape, "cedula": r_ced,
                        "email": r_ema, "direccion": r_dir, "telefono": tel_final,
                        "placa": r_pla, "clave": r_cla
                    })
                    st.success("¡Registrado! Ya puedes ingresar.")
