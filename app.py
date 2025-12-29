import streamlit as st
import pandas as pd
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse
import urllib.request
import random
import math

# --- ⚙️ CONFIGURACIÓN ---
st.set_page_config(page_title="TAXI SEGURO", page_icon="🚖", layout="centered")

# 🆔 CONEXIÓN TÉCNICA
SHEET_ID = "1l3XXIoAggDd2K9PWnEw-7SDlONbtUvpYVw3UYD_9hus"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwzOVH8c8f9WEoE4OJOTIccz_EgrOpZ8ySURTVRwi0bnQhFnWVdgfX1W8ivTIu5dFfs/exec"
EMAIL_CONTACTO = "taxi-seguro-world@hotmail.com"

# Coordenadas base (Coca, Ecuador)
LAT_BASE = -0.466657
LON_BASE = -76.989635

# --- 🌍 DICCIONARIO DE TRADUCCIONES (7 IDIOMAS - NIVEL 2) ---
TRADUCCIONES = {
    "Español": {
        "bienvenida": "🚖 TAXI SEGURO",
        "subtitulo": "🌎 SERVICIO GLOBAL",
        "paso1": "📡 PASO 1: ACTIVAR UBICACIÓN",
        "paso2": "📝 PASO 2: DATOS DEL VIAJE",
        "gps_ok": "✅ GPS ACTIVADO",
        "gps_off": "📍 Por favor activa tu GPS.",
        "nombre": "Tu Nombre:",
        "pregunta": "¿Qué necesitas?",
        "boton": "🚖 SOLICITAR UNIDAD",
        "error": "⚠️ Nombre, Teléfono y Referencia son obligatorios.",
        "buscando": "🔄 Buscando la unidad más cercana...",
        "encontrado": "✅ ¡Unidad Encontrada! Conductor: ",
        "no_libre": "❌ No hay conductores 'LIBRES' cerca de ti.",
        "footer_ayuda": "¿Necesitas ayuda?",
        "whatsapp": "📲 ENVIAR UBICACIÓN"
    },
    "English": {
        "bienvenida": "🚖 SECURE TAXI",
        "subtitulo": "🌎 GLOBAL SERVICE",
        "paso1": "📡 STEP 1: ENABLE LOCATION",
        "paso2": "📝 STEP 2: TRIP DETAILS",
        "gps_ok": "✅ GPS ENABLED",
        "gps_off": "📍 Please enable your GPS.",
        "nombre": "Your Name:",
        "pregunta": "What do you need?",
        "boton": "🚖 REQUEST RIDE",
        "error": "⚠️ Name, Phone, and Reference are required.",
        "buscando": "🔄 Looking for the nearest unit...",
        "encontrado": "✅ Unit Found! Driver: ",
        "no_libre": "❌ No 'FREE' drivers near you.",
        "footer_ayuda": "Need help?",
        "whatsapp": "📲 SEND LOCATION"
    },
    "Português": {
        "bienvenida": "🚖 TÁXI SEGURO",
        "subtitulo": "🌎 SERVIÇO GLOBAL",
        "paso1": "📡 PASSO 1: ATIVAR LOCALIZAÇÃO",
        "paso2": "📝 PASSO 2: DADOS DA VIAGEM",
        "gps_ok": "✅ GPS ATIVADO",
        "gps_off": "📍 Por favor, ative seu GPS.",
        "nombre": "Seu Nome:",
        "pregunta": "O que você precisa?",
        "boton": "🚖 SOLICITAR UNIDADE",
        "error": "⚠️ Nome, Telefone e Referência são obrigatórios.",
        "buscando": "🔄 Procurando a unidade mais próxima...",
        "encontrado": "✅ Unidade Encontrada! Motorista: ",
        "no_libre": "❌ Não há motoristas 'LIVRES' perto de você.",
        "footer_ayuda": "Precisa de ajuda?",
        "whatsapp": "📲 ENVIAR LOCALIZAÇÃO"
    },
    "Français": {
        "bienvenida": "🚖 TAXI SÉCURISÉ",
        "subtitulo": "🌎 SERVICE GLOBAL",
        "paso1": "📡 ÉTAPE 1 : ACTIVER LA LOCALISATION",
        "paso2": "📝 ÉTAPE 2 : DÉTAILS DU VOYAGE",
        "gps_ok": "✅ GPS ACTIVÉ",
        "gps_off": "📍 Veuillez activer votre GPS.",
        "nombre": "Votre Nom :",
        "pregunta": "De quoi avez-vous besoin ?",
        "boton": "🚖 DEMANDER UNE COURSE",
        "error": "⚠️ Le nom, le téléphone et la référence sont obligatoires.",
        "buscando": "🔄 Recherche de l'unité la plus proche...",
        "encontrado": "✅ Unité Trouvée ! Chauffeur : ",
        "no_libre": "❌ Aucun chauffeur 'LIBRE' à proximité.",
        "footer_ayuda": "Besoin d'aide ?",
        "whatsapp": "📲 ENVOYER LA LOCALISATION"
    },
    "Italiano": {
        "bienvenida": "🚖 TAXI SICURO",
        "subtitulo": "🌎 SERVIZIO GLOBALE",
        "paso1": "📡 PASSO 1: ATTIVA POSIZIONE",
        "paso2": "📝 PASSO 2: DETTAGLI VIAGGIO",
        "gps_ok": "✅ GPS ATTIVATO",
        "gps_off": "📍 Per favore attiva il tuo GPS.",
        "nombre": "Il tuo Nome:",
        "pregunta": "Di cosa hai bisogno?",
        "boton": "🚖 RICHIEDI CORSA",
        "error": "⚠️ Nome, Telefono e Riferimento sono obbligatori.",
        "buscando": "🔄 Ricerca dell'unità più vicina...",
        "encontrado": "✅ Unità Trovata! Conducente: ",
        "no_libre": "❌ Nessun conducente 'LIBERO' nelle vicinanze.",
        "footer_ayuda": "Serve aiuto?",
        "whatsapp": "📲 INVIA POSIZIONE"
    },
    "Deutsch": {
        "bienvenida": "🚖 SICHERES TAXI",
        "subtitulo": "🌎 GLOBALER SERVICE",
        "paso1": "📡 SCHRITT 1: STANDORT AKTIVIEREN",
        "paso2": "📝 SCHRITT 2: REISEINFOS",
        "gps_ok": "✅ GPS AKTIVIERT",
        "gps_off": "📍 Bitte aktivieren Sie Ihr GPS.",
        "nombre": "Ihr Name:",
        "pregunta": "Was brauchen Sie?",
        "boton": "🚖 TAXI ANFORDERN",
        "error": "⚠️ Name, Telefon und Referenz sind erforderlich.",
        "buscando": "🔄 Suche nach der nächsten Einheit...",
        "encontrado": "✅ Einheit gefunden! Fahrer: ",
        "no_libre": "❌ Keine 'FREIEN' Fahrer in Ihrer Nähe.",
        "footer_ayuda": "Brauchen Sie Hilfe?",
        "whatsapp": "📲 STANDORT SENDEN"
    },
    "Kichwa": {
        "bienvenida": "🚖 ALLI ANTAWA",
        "subtitulo": "🌎 TUKUY LLAKTAPAK",
        "paso1": "📡 SHUK: MAYPI KASHKATA RICUCHIY",
        "paso2": "📝 ISHKAY: PURINAPAK WILLAY",
        "gps_ok": "✅ GPS LLANKACUNMI",
        "gps_off": "📍 GPS-ta pascary.",
        "nombre": "Kampa Shuti:",
        "pregunta": "Imatatak mutsurinki?",
        "boton": "🚖 ANTAWATA MAÑAY",
        "error": "⚠️ Shuti, Yupay, mañaypash mutsurikunmi.",
        "buscando": "🔄 Kuchulla antawata maskacun...",
        "encontrado": "✅ Antawa tarishca! Pushac: ",
        "no_libre": "❌ Mana tiyanchu pushaccuna.",
        "footer_ayuda": "Yanapata munankichu?",
        "whatsapp": "📲 MAYPI KASHKATA KACHAY"
    }
}

# --- 🎨 ESTILOS CSS ---
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; text-align: center; color: #000; margin-bottom: 0; }
    .sub-title { font-size: 25px; font-weight: bold; text-align: center; color: #E91E63; margin-top: -10px; margin-bottom: 20px; }
    .step-header { font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; color: #333; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; font-size: 18px; border-radius: 10px; }
    .id-badge { background-color: #F0F2F6; padding: 5px 15px; border-radius: 20px; border: 1px solid #CCC; font-weight: bold; color: #555; display: inline-block; margin-bottom: 10px; }
    .footer { text-align: center; color: #888; font-size: 14px; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    .footer a { color: #E91E63; text-decoration: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- FÓRMULA DISTANCIA ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- FUNCIONES DE DATOS ---
def cargar_datos(hoja):
    try:
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={hoja}&cb={cache_buster}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

def enviar_datos_a_sheets(datos):
    try:
        params = urllib.parse.urlencode(datos)
        url_final = f"{URL_SCRIPT}?{params}"
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e: return f"Error: {e}"

def formatear_internacional(prefijo, numero):
    if not numero: return ""
    n = ''.join(filter(str.isdigit, str(numero).split(".")[0].strip()))
    p = str(prefijo).split(" ")[0].replace("+", "").strip()
    if n.startswith(p): return n 
    if n.startswith("0"): n = n[1:]
    return p + n

def obtener_chofer_mas_cercano(lat_cliente, lon_cliente):
    df_choferes = cargar_datos("CHOFERES")
    df_ubicaciones = cargar_datos("UBICACIONES")
    if df_choferes.empty or df_ubicaciones.empty: return None, None, None
    
    libres = df_choferes[df_choferes['Estado'].astype(str).str.strip().str.upper() == 'LIBRE']
    if libres.empty: return None, None, None
            
    mejor_chofer, menor_distancia = None, float('inf')
    for index, chofer in libres.iterrows():
        nombre_completo = f"{chofer['Nombre']} {chofer['Apellido']}"
        ubi = df_ubicaciones[df_ubicaciones['Conductor'] == nombre_completo]
        if not ubi.empty:
            lat_chof, lon_chof = float(ubi.iloc[-1]['Latitud']), float(ubi.iloc[-1]['Longitud'])
            dist = calcular_distancia(lat_cliente, lon_cliente, lat_chof, lon_chof)
            if dist < menor_distancia:
                menor_distancia, mejor_chofer = dist, chofer
    
    if mejor_chofer is not None:
        telf = ''.join(filter(str.isdigit, str(mejor_chofer['Telefono'])))
        if (len(telf) == 9 or len(telf) == 10) and telf.startswith("0"): telf = "593" + telf[1:]
        foto = str(mejor_chofer['FOTO_PENDIENTE']) if 'FOTO_PENDIENTE' in mejor_chofer else ""
        return f"{mejor_chofer['Nombre']} {mejor_chofer['Apellido']}", telf, foto
    return None, None, None

# --- 📱 INTERFAZ PRINCIPAL ---

# Selector de Idioma (Nivel 2)
st.sidebar.markdown("### 🌐 Language / Idioma")
idioma_sel = st.sidebar.selectbox("Select Language", list(TRADUCCIONES.keys()))
t = TRADUCCIONES[idioma_sel]

st.markdown(f'<div class="main-title">{t["bienvenida"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{t["subtitulo"]}</div>', unsafe_allow_html=True)
st.sidebar.info("👋 Conductores:\nPortal de Socios en el menú.")

st.divider()

# Paso 1: GPS
st.markdown(f'<div class="step-header">{t["paso1"]}</div>', unsafe_allow_html=True)
loc = get_geolocation()
lat_actual, lon_actual = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (LAT_BASE, LON_BASE)

if loc: st.success(t["gps_ok"])
else: st.info(t["gps_off"])

# Paso 2: Formulario
st.markdown(f'<div class="step-header">{t["paso2"]}</div>', unsafe_allow_html=True)
with st.form("form_pedido"):
    nombre_cli = st.text_input(t["nombre"])
    prefijo_pais = st.selectbox("País / Country", ["+593 (Ecuador)", "+57 (Colombia)", "+51 (Perú)", "+52 (México)", "+34 (España)", "+1 (USA)", "Otro"])
    celular_cli = st.text_input("WhatsApp (No code)")
    ref_cli = st.text_input("Referencia:")
    tipo_veh = st.selectbox(t["pregunta"], ["Taxi 🚖", "Camioneta 🛻", "Ejecutivo 🚔"])
    enviar = st.form_submit_button(t["boton"])

if enviar:
    if not nombre_cli or not ref_cli or not celular_cli:
        st.error(t["error"])
    else:
        tel_final_cli = formatear_internacional(prefijo_pais, celular_cli)
        with st.spinner(t["buscando"]):
            chof, t_chof, foto_chof = obtener_chofer_mas_cercano(lat_actual, lon_actual)
            id_v = f"TX-{random.randint(1000, 9999)}"
            
            enviar_datos_a_sheets({
                "accion": "registrar_pedido", "cliente": nombre_cli, "telefono_cli": tel_final_cli, 
                "referencia": ref_cli, "conductor": chof if chof else "OCUPADOS", 
                "mapa": f"https://www.google.com/maps?q={lat_actual},{lon_actual}", "id_viaje": id_v
            })
            
            if chof:
                st.balloons()
                st.success(f"{t['encontrado']} **{chof}**")
                if foto_chof and "http" in foto_chof:
                    st.markdown(f'<div style="text-align:center;"><img src="{foto_chof}" style="width:120px;border-radius:50%;border:4px solid #25D366;"></div>', unsafe_allow_html=True)
                
                msg = f"🚖 *PEDIDO*\n🆔 *ID:* {id_v}\n👤 Cliente: {nombre_cli}\n🗺️ Mapa: https://www.google.com/maps?q={lat_actual},{lon_actual}"
                link_wa = f"https://api.whatsapp.com/send?phone={t_chof}&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link_wa}" target="_blank" style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-align:center;display:block;text-decoration:none;font-weight:bold;font-size:20px;">{t["whatsapp"]}</a>', unsafe_allow_html=True)
            else: st.error(t["no_libre"])

# Footer
st.markdown(f"""<div class="footer"><p>{t['footer_ayuda']}</p><p>📧 <a href="mailto:{EMAIL_CONTACTO}">{EMAIL_CONTACTO}</a></p><p>© 2025 Taxi Seguro</p></div>""", unsafe_allow_html=True)
