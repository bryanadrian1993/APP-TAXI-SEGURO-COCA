import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import re
from datetime import datetime

# --- ⚙️ CONFIGURACIÓN FIJA (NO TOCAR) ---
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwmdasUK1xYWaJjk-ytEAjepFazngTZ91qxhsuN0VZ0OgQmmjyZnD6nOnCNuwIL3HjD/exec"

def cargar_datos(hoja):
    try:
        # Cache buster para ver cambios en tiempo real
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={datetime.now().strftime('%H%M%S')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

def enviar_datos(datos):
    try:
        params = urllib.parse.urlencode(datos)
        with urllib.request.urlopen(f"{URL_SCRIPT}?{params}") as response:
            return response.read().decode('utf-8')
    except: return "Error"

# --- 📱 INTERFAZ VISUAL (RESPECTO A TUS FOTOS) ---
st.title("🚖 Portal de Socios")

if 'usuario_activo' not in st.session_state:
    st.session_state.usuario_activo = False

if st.session_state.usuario_activo:
    # --- PANEL INTERNO (KM, DEUDA, FOTO) ---
    df = cargar_datos("CHOFERES")
    u = st.session_state.datos_usuario
    fila = df[(df['Nombre'] == u['Nombre']) & (df['Apellido'] == u['Apellido'])]
    
    if not fila.empty:
        # Extraer datos reales
        foto_raw = str(fila['Foto_Perfil'].values[0])
        km = float(fila['KM_ACUMULADOS'].values[0])
        deuda = float(fila['DEUDA'].values[0])
        estado = str(fila['Estado'].values[0])
        
        # Mostrar Foto con reparador de Drive
        if "http" in foto_raw:
            id_f = re.search(r'[-\w]{25,}', foto_raw).group() if re.search(r'[-\w]{25,}', foto_raw) else ""
            st.markdown(f'<div style="text-align:center;"><img src="https://lh3.googleusercontent.com/u/0/d/{id_f}" style="width:145px;border-radius:50%;border:5px solid #25D366;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;font-size:80px;">👤</div>', unsafe_allow_html=True)
        
        st.success(f"✅ Socio: **{u['Nombre']} {u['Apellido']}**")
        
        c1, c2 = st.columns(2)
        c1.metric("🛣️ KM Totales", f"{km:.2f} km")
        c2.metric("💸 Deuda Actual", f"${deuda:.2f}")

        # Botones de Estado
        st.subheader(f"🚦 ESTADO: {estado}")
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("🟢 LIBRE", use_container_width=True):
            enviar_datos({"accion": "actualizar_estado", "nombre": u['Nombre'], "apellido": u['Apellido'], "estado": "LIBRE"})
            st.rerun()
        if col_b2.button("🔴 OCUPADO", use_container_width=True):
            enviar_datos({"accion": "actualizar_estado", "nombre": u['Nombre'], "apellido": u['Apellido'], "estado": "OCUPADO"})
            st.rerun()

    if st.button("🔒 CERRAR SESIÓN"):
        st.session_state.usuario_activo = False
        st.rerun()

else:
    # --- LOGIN Y REGISTRO (DISEÑO EXACTO A TUS FOTOS) ---
    tab1, tab2 = st.tabs(["🔐 INGRESAR", "📝 REGISTRARME"])
    
    with tab1:
        ln = st.text_input("Nombre")
        la = st.text_input("Apellido")
        lp = st.text_input("Contraseña", type="password")
        if st.button("ENTRAR", type="primary"):
            df_l = cargar_datos("CHOFERES")
            # Comparación segura
            match = df_l[(df_l['Nombre'].astype(str).str.upper() == ln.upper()) & (df_l['Apellido'].astype(str).str.upper() == la.upper())]
            if not match.empty and str(match.iloc[0]['Clave']) == lp:
                st.session_state.usuario_activo = True
                st.session_state.datos_usuario = match.iloc[0].to_dict()
                st.rerun()
            else: st.error("Datos incorrectos")
        
        # SECCIÓN NUEVA DE RECUPERACIÓN (DEBAJO DE TODO)
        st.divider()
        st.subheader("📩 Recuperar mi cuenta")
        mail_rec = st.text_input("Ingresa tu correo registrado")
        if st.button("Enviar mis credenciales al email"):
            if mail_rec:
                res = enviar_datos({"accion": "recuperar_por_email_directo", "email": mail_rec})
                if "ENVIADO" in res: st.success("¡Listo! Revisa tu correo (y la carpeta de Spam).")
                else: st.error("El correo no existe en nuestro sistema.")

    with tab2:
        # Formulario de Registro idéntico a tu foto
        with st.form("reg_socio"):
            st.subheader("Nuevo Registro")
            rn = st.text_input("Nombres *")
            ra = st.text_input("Apellidos *")
            re_m = st.text_input("Correo Electrónico *")
            rk = st.text_input("Contraseña *", type="password")
            
            # Botón estilo tu foto
            if st.form_submit_button("✅ REGISTRARME"):
                if rn and re_m and rk:
                    # Envío respetando las 18 columnas en el Apps Script
                    enviar_datos({"accion": "registrar_conductor", "nombre": rn, "apellido": ra, "email": re_m, "clave": rk})
                    st.success("¡Registro completado! Ya puedes ingresar.")
                else: st.error("Completa los campos con *")
