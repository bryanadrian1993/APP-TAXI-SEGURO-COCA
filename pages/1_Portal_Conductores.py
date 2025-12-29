import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import base64
import os
import math
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- ⚙️ CONFIGURACIÓN DE NEGOCIO ---
TARIFA_POR_KM = 0.10        
DEUDA_MAXIMA = 10.00        
LINK_PAYPAL = "https://paypal.me/CAMPOVERDEJARAMILLO" 
NUMERO_DEUNA = "09XXXXXXXX" 

# --- 🔗 CONFIGURACIÓN TÉCNICA ---
st.set_page_config(page_title="Portal Conductores", page_icon="🚖", layout="centered")
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwzOVH8c8f9WEoE4OJOTIccz_EgrOpZ8ySURTVRwi0bnQhFnWVdgfX1W8ivTIu5dFfs/exec"

# --- 🛠️ FUNCIONES ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

def enviar_datos(datos):
    try:
        params = urllib.parse.urlencode(datos)
        url_final = f"{URL_SCRIPT}?{params}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371 
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) * R

# --- 📱 INTERFAZ ---
st.title("🚖 Portal de Socios")

if 'usuario_activo' not in st.session_state: st.session_state.usuario_activo = False

if st.session_state.usuario_activo:
    # --- PANEL DEL CONDUCTOR LOGUEADO ---
    df_fresh = cargar_datos("CHOFERES")
    u = st.session_state.datos_usuario
    fila = df_fresh[(df_fresh['Nombre'] == u['Nombre']) & (df_fresh['Apellido'] == u['Apellido'])]
    
    # Mapeo de columnas según tu Excel (18 columnas)
    foto_url = str(fila.iloc[0, 11]) if not fila.empty else "" # Columna 11: Foto_Perfil
    estado_actual = str(fila.iloc[0, 8]) if not fila.empty else "OCUPADO" # Columna 8: Estado
    km_acumulados = float(fila.iloc[0, 16]) if not fila.empty else 0.0 # Columna 16: KM_ACUMULADOS
    deuda_actual = float(fila.iloc[0, 17]) if not fila.empty else 0.0 # Columna 17: DEUDA
    bloqueado = deuda_actual >= DEUDA_MAXIMA

    # Mostrar Foto de Perfil
    if "http" in foto_url:
        st.markdown(f'<div style="text-align:center;"><img src="{foto_url}" style="width:120px;border-radius:50%;border:4px solid #25D366;"></div>', unsafe_allow_html=True)

    st.success(f"✅ Socio: **{u['Nombre']} {u['Apellido']}**")

    if bloqueado:
        st.error(f"⛔ CUENTA BLOQUEADA POR DEUDA: ${deuda_actual:.2f}")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f'''<a href="{LINK_PAYPAL}" target="_blank" style="text-decoration:none;"><div style="background-color:#003087;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">🔵 PAYPAL</div></a>''', unsafe_allow_html=True)
        with col_p2:
            if st.button("📱 MOSTRAR QR DEUNA", use_container_width=True):
                if os.path.exists("qr_deuna.png"):
                    with open("qr_deuna.png", "rb") as f:
                        data = base64.b64encode(f.read()).decode()
                    st.markdown(f'<img src="data:image/png;base64,{data}" width="100%">', unsafe_allow_html=True)
                else: st.error("No se encontró 'qr_deuna.png'")
        
        if st.button("🔄 YA PAGUÉ, REVISAR MI SALDO", type="primary", use_container_width=True):
            st.rerun()
    else:
        # --- MÉTRICAS Y CONTADOR ---
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("🛣️ KM Totales", f"{km_acumulados:.2f} km")
        col_m2.metric("💸 Deuda Actual", f"${deuda_actual:.2f}")
        
        st.write("📊 Límite de Crédito:")
        st.progress(min(deuda_actual/DEUDA_MAXIMA, 1.0))

        # --- CONTROLES DE ESTADO ---
        st.subheader(f"🚦 ESTADO ACTUAL: {estado_actual}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🟢 PONERME LIBRE", use_container_width=True):
                enviar_datos({"accion": "actualizar_estado", "nombre": u['Nombre'], "apellido": u['Apellido'], "estado": "LIBRE"})
                st.rerun()
        with c2:
            if st.button("🔴 PONERME OCUPADO", use_container_width=True):
                enviar_datos({"accion": "actualizar_estado", "nombre": u['Nombre'], "apellido": u['Apellido'], "estado": "OCUPADO"})
                st.rerun()

    if st.button("🔒 CERRAR SESIÓN"):
        st.session_state.usuario_activo = False
        st.rerun()

else:
    # --- LOGIN Y REGISTRO (Restaurado con Tabs e Iconos) ---
    tab_log, tab_reg = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])
    
    with tab_log:
        l_nom = st.text_input("Nombre")
        l_ape = st.text_input("Apellido")
        l_pass = st.text_input("Contraseña", type="password")
        if st.button("ENTRAR", type="primary"):
            df = cargar_datos("CHOFERES")
            match = df[(df['Nombre'].astype(str).str.upper() == l_nom.upper()) & (df['Apellido'].astype(str).str.upper() == l_ape.upper())]
            if not match.empty and str(match.iloc[0]['Clave']) == l_pass:
                st.session_state.usuario_activo = True
                st.session_state.datos_usuario = match.iloc[0].to_dict()
                st.rerun()
            else: st.error("Datos incorrectos")

    with tab_reg:
        with st.form("registro_form"):
            st.subheader("Registro de Nuevos Socios")
            r_nom = st.text_input("Nombres *")
            r_ape = st.text_input("Apellidos *")
            r_ced = st.text_input("Cédula/ID *")
            r_ema = st.text_input("Email *")
            r_dir = st.text_input("Dirección *")
            col_p, col_n = st.columns([1, 2])
            r_pais = col_p.selectbox("País", ["+593 (Ecuador)", "+57 (Colombia)", "+51 (Perú)", "Otro"])
            r_telf = col_n.text_input("WhatsApp (Sin código) *")
            r_pla = st.text_input("Placa *")
            r_tipo = st.selectbox("Tipo de Vehículo", ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"])
            r_pass1 = st.text_input("Contraseña *", type="password")
            
            if st.form_submit_button("✅ COMPLETAR REGISTRO"):
                p_limpio = r_pais.split(" ")[0].replace("+", "")
                tel_final = p_limpio + ''.join(filter(str.isdigit, r_telf))
                enviar_datos({
                    "accion": "registrar_conductor", "nombre": r_nom, "apellido": r_ape, 
                    "cedula": r_ced, "email": r_ema, "direccion": r_dir, "telefono": tel_final, 
                    "placa": r_pla, "clave": r_pass1, "pais": r_pais, "tipo": r_tipo
                })
                st.success("¡Registro enviado! Ahora ingresa en la pestaña correspondiente.")
