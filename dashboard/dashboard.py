import streamlit as st
import requests
import os

st.set_page_config(page_title="Wakanda Control Center", layout="wide", page_icon="🏙️")

st.title("🏙️ Wakanda Smart City - Panel de Control")
st.markdown("**Conectado vía API Gateway (Entrada Unificada)**")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway_api:8080")

SERVICES = {
    "trafico":   f"{GATEWAY_URL}/gestion_trafico",
    "energia":   f"{GATEWAY_URL}/gestion_energia",
    "agua":      f"{GATEWAY_URL}/gestion_agua",
    "residuos":  f"{GATEWAY_URL}/gestion_residuos",
    "seguridad": f"{GATEWAY_URL}/seguridad_vigilancia"
}


tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚦 Tráfico", "⚡ Energía", "💧 Agua", "♻️ Residuos", "🛡️ Seguridad"])

with tab1:
    st.header("Gestión de Tráfico")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Estado Intersecciones")
        if st.button("🔄 Consultar Estado (GET)"):
            try:
                r = requests.get(f"{SERVICES['trafico']}/traffic/status")
                if r.status_code == 200:
                    st.success("Conexión OK vía Gateway")
                    st.json(r.json())
                else:
                    st.error(f"Error {r.status_code}: {r.text}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

    with col2:
        st.subheader("Control de Semáforos")
        with st.form("traffic_adjust"):
            st.write("Ajustar tiempos de semáforo (POST)")
            interseccion_id = st.number_input("ID Intersección", 1, 10, 1)
            tiempo_verde = st.slider("Tiempo en Verde (s)", 10, 120, 45)

            if st.form_submit_button("Aplicar Cambios"):
                payload = {
                    "intersection_id": interseccion_id,
                    "id": interseccion_id,
                    "green_duration": tiempo_verde,
                    "duration": tiempo_verde
                }
                try:
                    r = requests.post(f"{SERVICES['trafico']}/traffic/adjust", json=payload)
                    st.info(f"Respuesta: {r.status_code}")
                    st.json(r.json())
                except Exception as e:
                    st.error(f"Error: {e}")

with tab2:
    st.header("Red Eléctrica (Smart Grid)")

    if st.button("⚡ Consultar Grid (GET)"):
        try:
            r = requests.get(f"{SERVICES['energia']}/energy/grid")
            st.json(r.json())
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    st.subheader("Reportar Consumo (Medidores)")
    with st.form("energy_report"):
        medidor = st.text_input("ID Medidor", "M-500")
        kwh = st.number_input("Consumo (kWh)", 0.0, 1000.0, 150.5)
        if st.form_submit_button("Enviar Lectura"):
            try:
                r = requests.post(f"{SERVICES['energia']}/energy/report",
                                  json={"meter_id": medidor, "consumption": kwh})
                st.success("Lectura enviada")
                st.json(r.json())
            except Exception as e:
                st.error(f"Error: {e}")

with tab3:
    st.header("Gestión Hídrica")
    st.info("Sistema de detección de fugas activo")

    zona = st.selectbox("Zona Afectada", ["Norte", "Sur", "Centro", "Puerto"])
    if st.button("🚨 Reportar Fuga (POST)"):
        try:
            r = requests.post(f"{SERVICES['agua']}/water/leak_alert",
                              json={"zone": zona, "severity": "high"})
            st.warning(f"Alerta enviada para zona {zona}")
            st.json(r.json())
        except Exception as e:
            st.error(f"Error: {e}")


with tab4:
    st.header("Recogida de Residuos")
    if st.button("🗑️ Estado Contenedores (GET)"):
        try:
            r = requests.get(f"{SERVICES['residuos']}/waste/containers")
            data = r.json()

            st.write("📦 Datos recibidos del camión:")

            if isinstance(data, list):
                st.success(f"Se han detectado {len(data)} contenedores.")
                st.table(data)
            else:
                st.json(data)

        except Exception as e:
            st.error(f"Error procesando datos: {e}")

with tab5:
    st.header("Vigilancia y Seguridad")
    col1, col2 = st.columns(2)

    with col1:
        st.write("Últimos Eventos")
        if st.button("Actualizar Eventos"):
            try:
                r = requests.get(f"{SERVICES['seguridad']}/security/events")
                st.table(r.json())
            except:
                st.warning("No se pudo conectar con Seguridad")

    with col2:
        st.error("Panel de Emergencia")
        if st.button("📢 ALERTA GENERAL"):
            try:
                r = requests.post(f"{SERVICES['seguridad']}/security/alert",
                                  json={"type": "GENERAL", "location": "ALL"})
                st.toast("¡Alerta General Enviada!")
                st.json(r.json())
            except Exception as e:
                st.error(f"Error: {e}")