import streamlit as st

# Configuración de la pestaña
st.set_page_config(page_title="Portal Conductores", page_icon="🚖")

# Título con estilo
st.markdown("<h1 style='text-align: center;'>🔐 ACCESO DE CONDUCTORES</h1>", unsafe_allow_html=True)
st.divider()

# --- INICIALIZACIÓN DE VARIABLES DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'nombre_usuario' not in st.session_state:
    st.session_state.nombre_usuario = ""
if 'estado_actual' not in st.session_state:
    st.session_state.estado_actual = "DESCONECTADO"

# --- FORMULARIO DE INGRESO ---
if not st.session_state.autenticado:
    with st.container(border=True):
        st.subheader("Identifíquese para trabajar")
        nombre = st.text_input("👤 Nombre del Conductor (como se registró):")
        clave = st.text_input("🔑 Clave de Acceso:", type="password")
        
        if st.button("INGRESAR AL PORTAL", use_container_width=True):
            if nombre and clave:
                # Aquí validamos el ingreso
                st.session_state.autenticado = True
                st.session_state.nombre_usuario = nombre
                st.rerun()
            else:
                st.error("❌ Por favor ingrese su Nombre y Clave")

# --- PANEL DE CONTROL DEL CONDUCTOR ---
else:
    st.success(f"✅ Conectado como: **{st.session_state.nombre_usuario}**")
    
    st.markdown("### 📍 SELECCIONE SU DISPONIBILIDAD")
    st.write("Indique si está listo para recibir pedidos:")

    # Botones de estado con colores y tamaño completo
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🟢 ESTOY LIBRE", use_container_width=True):
            st.session_state.estado_actual = "LIBRE"
            st.toast("Cambiado a LIBRE")

    with col2:
        if st.button("🔴 ESTOY OCUPADO", use_container_width=True):
            st.session_state.estado_actual = "OCUPADO"
            st.toast("Cambiado a OCUPADO")

    st.divider()

    # --- INDICADOR VISUAL DE ESTADO ---
    if st.session_state.estado_actual == "LIBRE":
        st.markdown(f"""
            <div style="background-color: #28a745; padding: 30px; border-radius: 15px; text-align: center; color: white;">
                <h1 style="margin:0;">ESTADO: LIBRE</h1>
                <p style="font-size: 20px;">Los clientes pueden ver que estás disponible.</p>
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.estado_actual == "OCUPADO":
        st.markdown(f"""
            <div style="background-color: #dc3545; padding: 30px; border-radius: 15px; text-align: center; color: white;">
                <h1 style="margin:0;">ESTADO: OCUPADO</h1>
                <p style="font-size: 20px;">Aviso activo: CONDUCTORES OCUPADOS.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
