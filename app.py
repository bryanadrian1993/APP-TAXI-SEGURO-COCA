@@ -1,62 +1,45 @@
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from streamlit_js_eval import get_geolocation
from datetime import datetime
from datetime import datetime, timedelta
import urllib.parse
import math

# --- 1. CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚖", layout="centered")
# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="TAXI SEGURO COCA", page_icon="🚖", layout="centered")

# 📍 COORDENADAS BASE (Coca)
# --- TUS DATOS ---
LAT_TAXI_BASE = -0.466657
LON_TAXI_BASE = -76.989635
NUMERO_ADMIN = "593962384356" # Tu número
PASSWORD_ADMIN = "admin123"   # 🔒 CONTRASEÑA DEL JEFE

# 📱 NÚMERO DEL TAXISTA (FIJO)
NUMERO_TAXISTA = "593962384356"

# --- 2. ESTILOS VISUALES ---
# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000; }
    .wa-btn {
        background-color: #25D366 !important; color: white !important;
        padding: 20px; border-radius: 15px; text-align: center;
        display: block; text-decoration: none; font-weight: bold;
        font-size: 20px; margin-top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .precio-box {
        background-color: #FFF9C4; padding: 20px; border-radius: 10px;
        border: 2px solid #FBC02D; text-align: center; margin-bottom: 20px;
    }
    .datos-banco {
        background-color: #F3F3F3; padding: 15px; border-radius: 10px;
        border-left: 5px solid #1E88E5; font-size: 14px; margin-bottom: 15px;
    }
    .exito-msg {
        background-color: #E8F5E9; color: #1B5E20; padding: 20px;
        border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px;
    }
    .aviso-foto {
        background-color: #FFF3E0; color: #E65100; padding: 10px;
        border-radius: 5px; font-size: 14px; margin-top: 10px; border: 1px solid #FFB74D;
    }
    .wa-btn { background-color: #25D366 !important; color: white !important; padding: 15px; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; }
    .precio-box { background-color: #FFF9C4; padding: 20px; border-radius: 10px; border: 2px solid #FBC02D; text-align: center; margin-bottom: 20px; }
    .exito-msg { background-color: #E8F5E9; color: #1B5E20; padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A SHEETS ---
def conectar_sheets():
# --- CONEXIÓN BASE DE DATOS ---
def conectar_sheets(hoja_nombre):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("BD_TAXI_PRUEBAS").get_worksheet(0)
    except: return None
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("BD_TAXI_PRUEBAS").worksheet(hoja_nombre)
    except Exception as e:
        return None

# --- 4. CÁLCULO DE DISTANCIA ---
# --- FUNCIONES AUXILIARES ---
def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
@@ -65,144 +48,206 @@ def calcular_distancia_km(lat1, lon1, lat2, lon2):
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- 5. GESTIÓN DE ESTADOS ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'datos_pedido' not in st.session_state: st.session_state.datos_pedido = {}

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center;'>🚖 TAXI SEGURO</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>📍 COCA</h3>", unsafe_allow_html=True)
st.write("---")

# === PASO 1: GPS Y FORMULARIO ===
if st.session_state.paso == 1:
    st.write("🛰️ **PASO 1: ACTIVAR UBICACIÓN**")
    loc = get_geolocation()
    lat, lon = LAT_TAXI_BASE, LON_TAXI_BASE
    distancia = 0.0
    gps_activo = False
    mapa_link = "No detectado"

    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        mapa_link = f"https://www.google.com/maps?q={lat},{lon}"
        distancia = calcular_distancia_km(LAT_TAXI_BASE, LON_TAXI_BASE, lat, lon)
        gps_activo = True
        st.success("✅ GPS ACTIVADO")
    else:
        st.warning("⚠️ Esperando señal GPS...")

    with st.form("form_inicial"):
        st.write("📝 **PASO 2: DATOS DEL VIAJE**")
        nombre = st.text_input("Nombre del cliente:")
        celular = st.text_input("Número de WhatsApp:")
        referencia = st.text_input("Referencia exacta:")
        tipo = st.selectbox("Tipo de unidad:", ["Taxi 🚖", "Camioneta 🛻", "Moto 📦"])
        
        if st.form_submit_button("REGISTRAR PEDIDO"):
            if not nombre or not celular or not referencia:
                st.error("❌ Llena todos los campos.")
            elif not gps_activo:
                st.error("⚠️ Activa tu GPS.")
            else:
                costo = round(distancia * 0.75, 2)
                if costo < 1.50: costo = 1.50
                st.session_state.datos_pedido = {
                    "nombre": nombre, "celular": celular, "referencia": referencia,
                    "tipo": tipo, "mapa": mapa_link, "distancia": distancia, "costo": costo
                }
                st.session_state.paso = 2
                st.rerun()

# === PASO 2: CONFIRMAR ===
elif st.session_state.paso == 2:
    d = st.session_state.datos_pedido
    st.write("💰 **CONFIRMACIÓN DE TARIFA**")
    st.markdown(f"""
    <div class="precio-box">
        <div class="precio-titulo">Costo estimado</div>
        <div class="precio-valor">${d['costo']}</div>
        <small>{round(d['distancia'], 2)} km</small>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    if c1.button("✅ ACEPTAR", use_container_width=True):
        st.session_state.paso = 3
        st.rerun()
    if c2.button("❌ CANCELAR", use_container_width=True):
        st.session_state.paso = 1
        st.rerun()

# === PASO 3: PAGO (MODO MANUAL) ===
elif st.session_state.paso == 3:
    st.write("💳 **MÉTODO DE PAGO**")
    pago = st.radio("Elige:", ("Efectivo", "Transferencia Bancaria", "Código QR DEUNA"))
# ==============================================================================
# 🚖 INTERFAZ PRINCIPAL (MENÚ)
# ==============================================================================
modo = st.sidebar.selectbox("Modo de Uso:", ["🚖 PEDIR TAXI (Cliente)", "👮‍♂️ ADMINISTRACIÓN (Dueño)"])

# ==============================================================================
# MODO 1: CLIENTE (PEDIR TAXI)
# ==============================================================================
if modo == "🚖 PEDIR TAXI (Cliente)":
    st.markdown("<h1 style='text-align:center;'>🚖 TAXI SEGURO</h1>", unsafe_allow_html=True)

    archivo_subido = None
    if pago == "Transferencia Bancaria":
        st.markdown("""
        <div class="datos-banco">
            <b>🏦 DATOS BANCARIOS:</b><br>
            <b>Banco:</b> PICHINCHA (Ahorros)<br>
            <b>Nº:</b> 2202072013<br>
            <b>Titular:</b> BRYAN ADRIAN CAMPOVERDE JARAMILLO<br>
            <b>CI:</b> 2200377071<br>
            <b>Email:</b> adrian-verdi@outlook.es
    if 'paso' not in st.session_state: st.session_state.paso = 1
    if 'datos' not in st.session_state: st.session_state.datos = {}

    # PASO 1: GPS y Datos
    if st.session_state.paso == 1:
        st.info("📍 Activa tu ubicación para calcular la tarifa exacta.")
        loc = get_geolocation()
        lat, lon = LAT_TAXI_BASE, LON_TAXI_BASE
        distancia = 0.0
        gps_ok = False
        mapa = "No detectado"

        if loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            mapa = f"https://www.google.com/maps?q={lat},{lon}"
            distancia = calcular_distancia_km(LAT_TAXI_BASE, LON_TAXI_BASE, lat, lon)
            gps_ok = True
            st.success("✅ GPS Detectado")

        with st.form("form_cliente"):
            nombre = st.text_input("Tu Nombre:")
            celular = st.text_input("Tu WhatsApp:")
            ref = st.text_input("Referencia Exacta:")
            tipo = st.selectbox("Unidad:", ["Taxi 🚖", "Camioneta 🛻"])
            
            if st.form_submit_button("COTIZAR VIAJE"):
                if not nombre or not celular or not ref:
                    st.error("Faltan datos")
                elif not gps_ok:
                    st.warning("⚠️ Esperando GPS... (Si no carga, intenta de nuevo)")
                else:
                    costo = round(distancia * 0.75, 2)
                    if costo < 1.50: costo = 1.50
                    st.session_state.datos = {
                        "nombre": nombre, "celular": celular, "ref": ref, "tipo": tipo,
                        "mapa": mapa, "dist": distancia, "costo": costo
                    }
                    st.session_state.paso = 2
                    st.rerun()

    # PASO 2: Confirmar Precio
    elif st.session_state.paso == 2:
        d = st.session_state.datos
        st.markdown(f"""
        <div class="precio-box">
            <h3>Costo Estimado</h3>
            <h1>${d['costo']}</h1>
            <p>Distancia: {round(d['dist'], 2)} km</p>
        </div>""", unsafe_allow_html=True)

        # Mantenemos esto visualmente para que el cliente sepa que debe tener el comprobante
        st.info("💡 Ten lista tu captura de pantalla para enviarla por WhatsApp al conductor.")

    if st.button("FINALIZAR VIAJE", use_container_width=True):
        st.session_state.datos_pedido['pago'] = pago
        st.session_state.paso = 4
        st.rerun()

# === PASO 4: FIN Y WHATSAPP ===
elif st.session_state.paso == 4:
    d = st.session_state.datos_pedido
    tiempo = math.ceil((d['distancia'] * 2.5) + 3)
        c1, c2 = st.columns(2)
        if c1.button("✅ ACEPTAR"): st.session_state.paso = 3; st.rerun()
        if c2.button("❌ CANCELAR"): st.session_state.paso = 1; st.rerun()

    # PASO 3: Pago
    elif st.session_state.paso == 3:
        st.write("💳 **Selecciona Pago:**")
        pago = st.radio("", ["Efectivo", "Transferencia", "QR Deuna"])
        
        if pago != "Efectivo":
            st.info("ℹ️ Al finalizar, enviarás el comprobante por WhatsApp.")
            
        if st.button("FINALIZAR PEDIDO", use_container_width=True):
            st.session_state.datos['pago'] = pago
            # Guardar en Sheets
            hoja = conectar_sheets("Hoja 1")
            if hoja:
                fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                fila = [fecha, st.session_state.datos['nombre'], st.session_state.datos['celular'], 
                        st.session_state.datos['tipo'], st.session_state.datos['ref'], 
                        st.session_state.datos['mapa'], f"PENDIENTE - {pago} - ${st.session_state.datos['costo']}"]
                try: hoja.append_row(fila)
                except: pass
            
            st.session_state.paso = 4
            st.rerun()

    # PASO 4: WhatsApp
    elif st.session_state.paso == 4:
        d = st.session_state.datos
        st.balloons()
        st.markdown('<div class="exito-msg">✅ SOLICITUD PROCESADA</div>', unsafe_allow_html=True)
        
        msg = (f"🚕 *PEDIDO NUEVO*\n👤 {d['nombre']}\n📱 {d['celular']}\n📍 {d['ref']}\n"
               f"💵 ${d['costo']} ({d['pago']})\n🗺️ {d['mapa']}")
        
        if d['pago'] != "Efectivo":
            msg += "\n\n📸 *ADJUNTO EL COMPROBANTE AQUÍ*"
            st.warning("⚠️ Recuerda adjuntar la foto del pago en el chat.")

        link = f"https://wa.me/{NUMERO_ADMIN}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<br><a href="{link}" class="wa-btn" target="_blank">📲 ENVIAR AL OPERADOR</a>', unsafe_allow_html=True)
        
        if st.button("🔄 Nuevo Viaje"):
            st.session_state.paso = 1
            st.rerun()

# ==============================================================================
# MODO 2: ADMINISTRACIÓN (TU PANEL)
# ==============================================================================
elif modo == "👮‍♂️ ADMINISTRACIÓN (Dueño)":
    st.header("👮‍♂️ ACCESO RESTRINGIDO")
    pwd = st.text_input("Contraseña:", type="password")

    # Guardar en Sheets (Datos básicos sin link de foto, pues no hay nube)
    hoja = conectar_sheets()
    if hoja:
    if pwd == PASSWORD_ADMIN:
        st.success("🔓 Acceso Concedido")
        
        # --- CARGA DE DATOS ---
        try:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            estado = f"PENDIENTE - {d['pago']} - ${d['costo']}"
            fila = [fecha, d['nombre'], d['celular'], d['tipo'], d['referencia'], d['mapa'], estado]
            hoja.append_row(fila)
        except: pass

    st.markdown(f"""
    <div class="exito-msg">
        ✅ PETICIÓN PROCESADA<br>LLEGAREMOS EN {tiempo} MINUTOS APROX.
    </div>""", unsafe_allow_html=True)
    
    # Mensaje WhatsApp Optimizado
    mensaje = (
        f"🚖 *PEDIDO CONFIRMADO*\n"
        f"👤 {d['nombre']} | 📱 {d['celular']}\n"
        f"💵 Costo: ${d['costo']} ({d['pago']})\n"
        f"🚖 Unidad: {d['tipo']}\n"
        f"🏠 Ref: {d['referencia']}\n"
        f"📍 Mapa: {d['mapa']}"
    )
    
    # Instrucción clara si es transferencia
    if d['pago'] == "Transferencia Bancaria":
        mensaje += "\n\n📸 *OJO:* EL CLIENTE ENVIARÁ EL COMPROBANTE DE PAGO EN ESTE CHAT."
        st.markdown("""
        <div class="aviso-foto">
            ⚠️ <b>IMPORTANTE:</b> Al presionar el botón verde se abrirá WhatsApp.<br>
            Por favor, <b>ADJUNTA LA FOTO DEL COMPROBANTE</b> en el chat.
        </div>
        """, unsafe_allow_html=True)

    link_wa = f"https://wa.me/{NUMERO_TAXISTA}?text={urllib.parse.quote(mensaje)}"
    st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR AL TAXISTA</a>', unsafe_allow_html=True)
            hoja_pedidos = conectar_sheets("Hoja 1")
            hoja_choferes = conectar_sheets("CHOFERES")
            df_pedidos = pd.DataFrame(hoja_pedidos.get_all_records())
            df_choferes = pd.DataFrame(hoja_choferes.get_all_records())
        except:
            st.error("⚠️ Error: No encuentro las hojas 'Hoja 1' o 'CHOFERES' en tu Excel.")
            st.stop()

        tabs = st.tabs(["📊 MONITOR", "📡 DESPACHO", "💰 SUSCRIPCIONES"])

        # --- TAB 1: MONITOR ---
        with tabs[0]:
            st.subheader("Estado de la Flota")
            if not df_choferes.empty:
                hoy_str = datetime.now().strftime("%Y-%m-%d")
                
                # Definir función para colorear
                def color_fila(row):
                    fecha = str(row['Vence_Suscripcion'])
                    estado = str(row['Estado'])
                    if fecha < hoy_str:
                        return ['background-color: #ffcdd2'] * len(row) # Rojo (Vencido)
                    elif estado == "LIBRE":
                        return ['background-color: #c8e6c9'] * len(row) # Verde (Libre)
                    else:
                        return [''] * len(row)

                st.dataframe(df_choferes.style.apply(color_fila, axis=1))
            else:
                st.warning("No hay choferes.")

        # --- TAB 2: DESPACHO ---
        with tabs[1]:
            st.subheader("Asignar Carreras")
            
            # Filtro: Solo pagados y libres
            hoy_str = datetime.now().strftime("%Y-%m-%d")
            habilitados = df_choferes[
                (df_choferes['Vence_Suscripcion'] >= hoy_str) & 
                (df_choferes['Estado'] == 'LIBRE')
            ] if not df_choferes.empty else pd.DataFrame()

            c1, c2 = st.columns(2)
            with c1:
                st.write("📦 **Pedidos Pendientes**")
                if not df_pedidos.empty:
                    st.dataframe(df_pedidos.tail(5).iloc[::-1], hide_index=True)
            with c2:
                st.write("✅ **Choferes Habilitados**")
                if not habilitados.empty:
                    st.table(habilitados[['Nombre', 'Telefono']])
                else:
                    st.error("Nadie disponible.")

            if not df_pedidos.empty and not habilitados.empty:
                idx = st.selectbox("Elegir Pedido:", df_pedidos.index[::-1])
                chof = st.selectbox("Elegir Chofer:", habilitados['Nombre'])
                
                if st.button("🚀 DESPACHAR"):
                    p = df_pedidos.loc[idx]
                    c = habilitados[habilitados['Nombre'] == chof].iloc[0]
                    texto = f"🚕 *CARRERA ASIGNADA*\n👤 {p['Nombre del cliente']}\n📞 {p['Telefono']}\n📍 {p['Referencia']}\n💵 Cobrar: {p['Estado']}"
                    link_d = f"https://wa.me/{c['Telefono']}?text={urllib.parse.quote(texto)}"
                    st.markdown(f'<a href="{link_d}" class="wa-btn" target="_blank">ENVIAR A {chof}</a>', unsafe_allow_html=True)

        # --- TAB 3: PAGOS ---
        with tabs[2]:
            st.subheader("Registrar Pago ($1)")
            if not df_choferes.empty:
                pagador = st.selectbox("Chofer:", df_choferes['Nombre'].unique())
                dias = st.number_input("Días:", 1, 30, 1)
                
                if st.button("💰 REGISTRAR PAGO"):
                    hoy = datetime.now().date()
                    # Encontrar fila del chofer
                    fila = df_choferes[df_choferes['Nombre'] == pagador].index[0] + 2
                    nueva_fecha = hoy + timedelta(days=dias)
                    hoja_choferes.update_cell(fila, 4, nueva_fecha.strftime("%Y-%m-%d"))
                    st.success("Pago registrado. Recarga la página.")

    st.write("")
    if st.button("🔄 Nuevo Pedido"):
        st.session_state.paso = 1
        st.rerun()
    elif pwd:
        st.error("Contraseña incorrecta")
