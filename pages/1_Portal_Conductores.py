import urllib.request
import urllib.parse

# --- FUNCIÓN PARA CONECTAR CON EL EXCEL ---
def actualizar_estado_en_sheets(nombre, nuevo_estado):
    try:
        # Enviamos el nombre y el estado a tu Google Apps Script
        params = {
            "accion": "actualizar_estado",
            "nombre": nombre,
            "estado": nuevo_estado
        }
        query_string = urllib.parse.urlencode(params)
        url_final = f"{URL_SCRIPT}?{query_string}"
        
        with urllib.request.urlopen(url_final) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

# --- DENTRO DEL PANEL DE SOCIO CONECTADO ---
if st.session_state.conectado:
    st.success(f"Socio: **{st.session_state.usuario}**")
    b1, b2 = st.columns(2)
    
    # Al dar clic, ahora sí se envía la orden al Excel
    if b1.button("🟢 ESTOY LIBRE", use_container_width=True):
        with st.spinner("Actualizando en Excel..."):
            resultado = actualizar_estado_en_sheets(st.session_state.usuario, "LIBRE")
            if "OK" in resultado:
                st.session_state.mi_estado = "LIBRE"
                st.toast("✅ Actualizado en Google Sheets")
            else:
                st.error("No se pudo actualizar el Excel")

    if b2.button("🔴 ESTOY OCUPADO", use_container_width=True):
        with st.spinner("Actualizando en Excel..."):
            resultado = actualizar_estado_en_sheets(st.session_state.usuario, "OCUPADO")
            if "OK" in resultado:
                st.session_state.mi_estado = "OCUPADO"
                st.toast("✅ Marcado como Ocupado")
