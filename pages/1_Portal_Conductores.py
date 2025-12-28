import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal Conductores", page_icon="🚕", layout="wide")
st.title("🚖 PORTAL DEL CONDUCTOR")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # ttl=2 hace que los datos se actualicen casi al instante
    try:
        choferes = conn.read(worksheet="CHOFERES", ttl=2)
        viajes = conn.read(worksheet="VIAJES", ttl=2)
        return choferes, viajes
    except:
        st.error("⚠️ Error: No se pudo conectar con la hoja de cálculo.")
        return pd.DataFrame(), pd.DataFrame()

df_choferes, df_viajes = cargar_datos()

# --- LOGIN (SELECCIÓN DE NOMBRE) ---
st.markdown("### Identifícate")
if not df_choferes.empty and "Nombre" in df_choferes.columns:
    lista_nombres = df_choferes["Nombre"].dropna().unique()
    chofer_seleccionado = st.selectbox("Selecciona tu nombre:", lista_nombres)
else:
    st.warning("No se encontraron choferes registrados.")
    st.stop()

# --- MOSTRAR INFORMACIÓN DEL CHOFER ---
if chofer_seleccionado:
    # 1. Obtener fila del chofer
    datos_chofer = df_choferes[df_choferes["Nombre"] == chofer_seleccionado].iloc[0]
    
    # 2. Obtener viajes de este chofer (buscando en la columna 'Conductor Asignado')
    if "Conductor Asignado" in df_viajes.columns:
        mis_viajes = df_viajes[df_viajes["Conductor Asignado"] == chofer_seleccionado]
    else:
        mis_viajes = pd.DataFrame()

    # 3. Calcular Días Trabajados
    dias_trabajados = 0
    try:
        fecha_registro = pd.to_datetime(datos_chofer["Fecha_Registro"], dayfirst=True)
        dias_trabajados = (datetime.now() - fecha_registro).days
    except:
        pass # Si falla la fecha, se queda en 0

    # 4. Verificar Estado de Suscripción
    vencimiento = str(datos_chofer.get("Vencimiento_Suscripcion", "Sin fecha"))
    estado_texto = "✅ AL DÍA"
    color_delta = "normal"
    
    try:
        fecha_venc = pd.to_datetime(vencimiento)
        if fecha_venc < datetime.now():
            estado_texto = "❌ VENCIDO - DEBES PAGAR $1"
            color_delta = "inverse" # Se pone rojo
    except:
        pass

    # --- PANTALLA PRINCIPAL (DASHBOARD) ---
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    col1.metric("📅 Días Activo", f"{dias_trabajados} días")
    col2.metric("🚗 Viajes Realizados", len(mis_viajes))
    col3.metric("💲 Estado Suscripción", estado_texto, delta_color=color_delta)
    
    st.caption(f"Tu suscripción vence el: {vencimiento}")

    st.divider()
    
    st.subheader(f"📜 Historial de Viajes de {chofer_seleccionado}")
    
    if not mis_viajes.empty:
        # Seleccionamos columnas útiles para mostrar
        columnas_posibles = ["Fecha", "Referencia", "Monto_Pago", "Estado"]
        columnas_finales = [c for c in columnas_posibles if c in mis_viajes.columns]
        
        st.dataframe(mis_viajes[columnas_finales], use_container_width=True)
    else:
        st.info("No tienes viajes asignados todavía.")

    # Botón para refrescar
    if st.button("🔄 Actualizar mis datos"):
        st.cache_data.clear()
        st.rerun()
