import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import re
from datetime import datetime

# --- ⚙️ CONFIGURACIÓN DE NEGOCIO ---
DEUDA_MAXIMA = 10.00        
LINK_PAYPAL = "https://paypal.me/CAMPOVERDEJARAMILLO" 

st.set_page_config(page_title="Portal Socios", page_icon="🚖", layout="centered")
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
    # --- PANEL DEL SOCIO LOGUEADO ---
    df_fresh = cargar_datos("CHOFERES")
    u = st.session_state.datos_usuario
    fila = df_fresh[(df_fresh['Nombre'] == u['Nombre']) & (df_fresh['Apellido'] == u['Apellido'])]
    
    if not fila.empty:
        foto_raw = str(fila['Foto_Perfil'].values[0])
        estado = str(fila['Estado'].values[0])
        km = float(fila['KM_ACUMULADOS'].values[0])
        deuda = float(fila['DEUDA'].values[0])
        bloqueado = deuda >= DEUDA_MAXIMA

        # Foto de Perfil con Reparador de Enlaces de Google Drive
        if "http" in foto_raw:
            match = re.search(r'[-\w]{25,}', foto_raw)
            id_f = match.group() if match else ""
            foto_f = f"https://lh3.googleusercontent.com/u/0/d/{id_f}"
            st.markdown(f'''<div style="text-align:center;margin-bottom:20px;">
                <img src="{foto_f}" style="width:145px;height:145px;border-radius:50%;object-fit:cover;border:5px solid #25D366;box-shadow:0 4px 12px rgba(0,0,0,0.3);">
            </div>''', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;font-size:80px;margin-bottom:20px;">👤</div>', unsafe_allow_html=True)

        st.success(f"✅ Socio: **{u['Nombre']} {u['Apellido']}**")

        # Métricas y Deuda
        c1, c2 = st.columns(2)
        c1.metric("🛣️ KM Totales", f"{km:.2f} km")
        c2.metric("💸 Deuda Actual", f"${deuda:.2f}")
        st.progress(min(deuda/DEUDA_MAXIMA, 1.0))

        if bloqueado:
            st.error(f"⛔ CUENTA BLOQUEADA POR DEUDA: ${deuda:.2f}")
            st.markdown(f'<a href="{LINK_PAYPAL}" target="_blank" style="text-decoration:none;"><div style="background-color:#003087;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">🔵 PAGAR CON PAYPAL</div></a>', unsafe_allow_html=True)
        
        # Botones de Estado
        st.subheader(f"🚦 ESTADO ACTUAL: {estado}")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🟢 PONERME LIBRE", use_container_width=True):
                enviar_datos({"accion": "actualizar_estado", "nombre": u['Nombre'], "apellido": u['Apellido'], "estado": "LIBRE"})
                st.rerun()
        with col_b2:
            if st.button("🔴 PONERME OCUPADO", use_container_width=True):
                enviar_datos({"accion": "actualizar_estado", "nombre": u['Nombre'], "apellido": u['Apellido'], "estado": "OCUPADO"})
                st.rerun()

    if st.button("🔒 CERRAR SESIÓN"):
        st.session_state.usuario_activo = False
        st.rerun()

else:
    # --- LOGIN Y REGISTRO ---
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
        
        # --- RECUPERACIÓN POR EMAIL (NUEVA FUNCIÓN) ---
        st.divider()
        st.subheader("¿Olvidaste tus datos?")
        email_recuperar = st.text_input("Ingresa tu correo electrónico registrado:")
        if st.button("📩 ENVIAR MIS CREDENCIALES AL EMAIL"):
            if email_recuperar:
                res = enviar_datos({
                    "accion": "recuperar_por_email_directo",
                    "email": email_recuperar
                })
                st.info("Si el correo existe, recibirás tu usuario y clave en breve.")
            else:
                st.warning("Escribe tu correo electrónico para procesar la recuperación.")

    with tab_reg:
        # REGISTRO COMPLETO (RESTAURADO SIN ERRORES)
        with st.form("registro_socio"):
            st.subheader("Formulario de Registro de Socio")
            col1, col2 = st.columns(2)
            r_nom = col1.text_input("Nombres *")
            r_ape = col2.text_input("Apellidos *")
            
            r_ced = st.text_input("Cédula / Pasaporte *")
            r_email = st.text_input("Correo Electrónico (Para recibir tus accesos) *")
            r_dir = st.text_input("Dirección Domicilio *")
            
            col_p, col_n = st.columns([1.5, 3])
            r_pais = col_p.selectbox("País", ["+593 (Ecuador)", "+57 (Colombia)", "+51 (Perú)", "Otro"])
            r_telf = col_n.text_input("Número WhatsApp (Sin código) *")
            
            col3, col4 = st.columns(2)
            r_pla = col3.text_input("Placa del Vehículo *")
            r_tipo = col4.selectbox("Tipo de Vehículo", ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔", "Moto 🏍️"])
            
            r_pass = st.text_input("Crea tu Contraseña de Acceso *", type="password")
            
            if st.form_submit_button("✅ COMPLETAR REGISTRO"):
                if r_nom and r_ape and r_email and r_pass and r_telf:
                    # Formatear el teléfono
                    prefijo = r_pais.split(" ")[0].replace("+", "")
                    telefono_limpio = ''.join(filter(str.isdigit, r_telf))
                    tel_final = prefijo + telefono_limpio
                    
                    # Enviar todos los datos para las 18 columnas
                    res = enviar_datos({
                        "accion": "registrar_conductor",
                        "nombre": r_nom,
                        "apellido": r_ape,
                        "cedula": r_ced,
                        "email": r_email,
                        "direccion": r_dir,
                        "telefono": tel_final,
                        "placa": r_pla,
                        "tipo": r_tipo,
                        "clave": r_pass
                    })
                    st.success(f"¡Registro enviado con éxito! Revisa tu bandeja de entrada en: {r_email}")
                else:
                    st.error("⚠️ Debes completar todos los campos marcados con asterisco (*)")
