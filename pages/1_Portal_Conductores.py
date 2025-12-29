import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import base64
import os
import math
from datetime import datetime

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
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip() # Limpiar espacios en nombres de columnas
        return df
    except: return pd.DataFrame()

def enviar_datos(datos):
    try:
        params = urllib.parse.urlencode(datos)
        url_final = f"{URL_SCRIPT}?{params}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

# --- 📱 INTERFAZ ---
st.title("🚖 Portal de Socios")

if 'usuario_activo' not in st.session_state: st.session_state.usuario_activo = False

if st.session_state.usuario_activo:
    # --- PANEL DEL CONDUCTOR LOGUEADO ---
    df_fresh = cargar_datos("CHOFERES")
    u = st.session_state.datos_usuario
    fila = df_fresh[(df_fresh['Nombre'] == u['Nombre']) & (df_fresh['Apellido'] == u['Apellido'])]
    
    if not fila.empty:
        # Recuperar datos por nombre de columna (seguro) o posición (respaldo)
        try:
            foto_url = str(fila['Foto_Perfil'].values[0])
            estado_actual = str(fila['Estado'].values[0])
            km_acumulados = float(fila['KM_ACUMULADOS'].values[0])
            deuda_actual = float(fila['DEUDA'].values[0])
        except:
            foto_url = str(fila.iloc[0, 11]) # Columna 12
            estado_actual = str(fila.iloc[0, 8]) # Columna 9
            km_acumulados = float(fila.iloc[0, 16]) # Columna 17
            deuda_actual = float(fila.iloc[0, 17]) # Columna 18
            
        bloqueado = deuda_actual >= DEUDA_MAXIMA

        # 1. MOSTRAR FOTO DE PERFIL (DISEÑO ORIGINAL)
        if "http" in foto_url and foto_url != "nan":
            foto_visible = foto_url.replace("open?id=", "uc?export=view&id=")
            st.markdown(f'''
                <div style="text-align:center; margin-bottom: 20px;">
                    <img src="{foto_visible}" style="width:130px; height:130px; border-radius:50%; object-fit:cover; border:5px solid #25D366; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center; font-size:60px; margin-bottom:20px;">👤</div>', unsafe_allow_html=True)

        st.success(f"✅ Socio: **{u['Nombre']} {u['Apellido']}**")

        if bloqueado:
            st.error(f"⛔ CUENTA BLOQUEADA POR DEUDA: ${deuda_actual:.2f}")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown(f'''<a href="{LINK_PAYPAL}" target="_blank" style="text-decoration:none;"><div style="background-color:#003087;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">🔵 PAYPAL</div></a>''', unsafe_allow_html=True)
            with col_p2:
                if st.button("📱 MOSTRAR QR DEUNA", use_container_width=True):
                    img_path = "qr_deuna.png"
                    if not os.path.exists(img_path): img_path = os.path.join("pages", "qr_deuna.png")
                    
                    if os.path.exists(img_path):
                        with open(img_path, "rb") as f:
                            data = base64.b64encode(f.read()).decode()
                        st.markdown(f'<img src="data:image/png;base64,{data}" width="100%">', unsafe_allow_html=True)
                    else: st.error("Archivo 'qr_deuna.png' no encontrado.")
            
            st.button("🔄 YA PAGUÉ, REVISAR MI SALDO", type="primary", use_container_width=True)
        else:
            # --- MÉTRICAS Y CONTADOR RESTAURADOS ---
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("🛣️ KM Totales", f"{km_acumulados:.2f} km")
            col_m2.metric("💸 Deuda Actual", f"${deuda_actual:.2f}")
            
            st.write("📊 Límite de Crédito ($10.00):")
            st.progress(min(deuda_actual/DEUDA_MAXIMA, 1.0))

            # Controles de Estado
            st.subheader(f"🚦 ESTADO: {estado_actual}")
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
    # --- PANTALLA INICIAL (Login y Registro) ---
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
            r_nom = st.text_input("Nombre *")
            r_ape = st.text_input("Apellido *")
            r_ced = st.text_input("Cédula/ID *")
            
            # WhatsApp con Selector de País (Añadido)
            st.write("WhatsApp:")
            col_p, col_n = st.columns([1.5, 3])
            r_pais = col_p.selectbox("País", [
                "+593 (Ecuador)", "+57 (Colombia)", "+51 (Perú)", "+1 (USA/Canada)", 
                "+34 (España)", "+44 (UK)", "+55 (Brasil)", "+33 (Francia)", 
                "+39 (Italia)", "+49 (Alemania)", "+86 (China)", "+81 (Japón)", "+7 (Rusia)", "Otro"
            ])
            r_telf = col_n.text_input("Número (Sin código) *")
            
            r_pla = st.text_input("Placa *")
            r_pass = st.text_input("Crea tu Contraseña *", type="password")
            
            if st.form_submit_button("✅ COMPLETAR REGISTRO"):
                if r_nom and r_telf and r_pass:
                    prefijo = r_pais.split(" ")[0].replace("+", "")
                    num_limpio = ''.join(filter(str.isdigit, r_telf))
                    if num_limpio.startswith("0"): num_limpio = num_limpio[1:]
                    tel_final = prefijo + num_limpio
                    
                    enviar_datos({
                        "accion": "registrar_conductor", "nombre": r_nom, "apellido": r_ape, 
                        "cedula": r_ced, "telefono": tel_final, "placa": r_pla, "clave": r_pass,
                        "pais": r_pais
                    })
                    st.success("¡Registro enviado! Ya puedes ingresar.")
