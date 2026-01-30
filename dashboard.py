import streamlit as st
import pandas as pd
import plotly.express as px # Usamos plotly para mejores gráficos
import os
from datetime import datetime

st.set_page_config(page_title="Monitor de Gran Corrupción", layout="wide")

# Rutas compatibles con Docker
DATA_DIR = "/app/data" if os.path.exists("/app/data") else "data"

st.title("⚖️ Monitor de Fenómenos Corruptivos Legales")
st.subheader("Implementación de la Teoría del Ph.D. Vicente Humberto Monteverde")

# CARGA DE DATOS
archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]
if not archivos:
    st.error("No se encontraron reportes. Ejecutá primero 'diario.py'")
    st.stop()

archivo_selec = st.sidebar.selectbox("Seleccioná un Reporte", sorted(archivos, reverse=True))
df = pd.read_excel(os.path.join(DATA_DIR, archivo_selec))

# MÉTRICAS IMPACTANTES
df_detectados = df[df["tipo_decision"] != "No identificado"]
m1, m2, m3 = st.columns(3)
m1.metric("Total Normas Analizadas", len(df))
m2.metric("Fenómenos Detectados", len(df_detectados))
m3.metric("Riesgo Máximo Detectado", f"{df['indice_fenomeno_corruptivo'].max()}/10")

# GRÁFICOS DINÁMICOS
col_izq, col_der = st.columns(2)

with col_izq:
    st.write("### 📊 Escenarios de la Gran Corrupción")
    fig = px.bar(df_detectados, y="tipo_decision", color="nivel_riesgo_teorico", 
                 orientation='h', title="Distribución por Escenario")
    st.plotly_chart(fig, use_container_width=True)

with col_der:
    st.write("### 💸 Sectores Afectados (Transferencia)")
    fig_pie = px.pie(df_detectados, names="transferencia", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# TABLA DE AUDITORÍA
st.header("🔍 Detalle de Decisiones Estatales")
st.dataframe(df_detectados, use_container_width=True)

# FUNDAMENTO TEÓRICO [cite: 3, 8, 19]
with st.expander("📖 Glosario y Marco Científico"):
    st.markdown("""
    **La Gran Corrupción** no son solo sobornos; son decisiones **legales y discrecionales** que redistribuyen el ingreso de forma inequitativa[cite: 17, 19].
    * **Jubilados al Estado:** Reducción del gasto mediante erosión de ingresos pasivos.
    * **Contratos Públicos:** Sobreprecios basados en la 'legalidad' de la continuación de contratos[cite: 162].
    """)
