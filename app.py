import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Panel de Conductor", layout="wide")
st.title("🚖 Portal de Conductores")

# --- CONEXIÓN CON GOOGLE SHEETS ---
# Busca la conexión definida en secrets.toml
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para cargar datos frescos
def cargar_datos():
    # Leemos las dos hojas por su nombre exacto
    # 'VIAJES' es la Hoja 1 renombrada, 'CHOFERES' es la hoja de conductores
    df_viajes = conn.read(worksheet="VIAJES", ttl=5) 
    df_choferes = conn.read(worksheet="CHOFERES", ttl=5)
    return df_viajes, df_choferes

try:
    df_viajes, df_choferes = cargar_datos()
except Exception as e:
    st.error("Error conectando con la hoja. Revisa tu archivo secrets.toml")
    st.stop()

# --- BARRA LATERAL: LOGIN ---
st.sidebar.header("Identificación")
# Creamos una lista de nombres únicos de la hoja CHOFERES
lista_nombres = df_choferes["Nombre"].dropna().unique()
chofer_seleccionado = st.sidebar.selectbox("Selecciona tu Nombre", lista_nombres)

if chofer_seleccionado:
    # --- FILTRAR DATOS DEL CHOFER ELEGIDO ---
    # Buscamos la fila exacta del chofer en la hoja CHOFERES
    info_chofer = df_choferes[df_choferes["Nombre"] == chofer_seleccionado].iloc[0]
    
    # Buscamos solo los viajes asignados a este chofer en la hoja VIAJES
    # Usamos la columna 'Conductor Asignado' que creaste
    mis_viajes = df_viajes[df_viajes["Conductor Asignado"] == chofer_seleccionado]

    # --- CÁLCULOS (Lógica de Negocio) ---
    
    # 1. Calcular días desde el registro
    try:
        fecha_registro = pd.to_datetime(info_chofer["Fecha_Registro"], dayfirst=True)
        dias_trabajando = (datetime.now() - fecha_registro).days
    except:
        dias_trabajando = 0 # Si hay error en la fecha o está vacía

    # 2. Verificar Vencimiento
    vencimiento_str = str(info_chofer["Vencimiento_Suscripcion"])
    
    # --- MOSTRAR INFORMACIÓN EN PANTALLA ---
    
    st.subheader(f"Bienvenido, {chofer_seleccionado}")
    
    # Tarjetas de resumen (Métricas)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📅 Días Activo", f"{dias_trabajando} días")
    
    with col2:
        st.metric("🚗 Viajes Totales", len(mis_viajes))
        
    with col3:
        st.metric("💲 Vencimiento Pago", vencimiento_str)
        # Alerta visual si la fecha ya pasó (Lógica simple)
        try:
            fecha_venc = pd.to_datetime(vencimiento_str)
            if fecha_venc < datetime.now():
                st.error("⚠️ PAGO ATRASADO")
            else:
                st.success("✅ AL DÍA")
        except:
            st.info("Fecha no válida")

    st.markdown("---")
    
    # Tabla de Historial de Viajes
    st.write("### 📜 Tu Historial de Carreras")
    
    if not mis_viajes.empty:
        # Seleccionamos solo las columnas útiles para mostrar
        # Ajusta los nombres si cambian en tu Excel
        columnas_a_mostrar = ["Fecha", "Nombre del cliente", "Referencia", "Estado"]
        
        # Filtramos para que no de error si falta alguna columna
        cols_validas = [c for c in columnas_a_mostrar if c in mis_viajes.columns]
        
        st.dataframe(mis_viajes[cols_validas], use_container_width=True)
    else:
        st.info("Aún no tienes viajes registrados en el sistema.")

    # Botón para recargar datos manualmente
    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()
