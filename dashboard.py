import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Monitor de Gran Corrupción", layout="wide")
DATA_DIR = "/app/data" if os.path.exists("/app/data") else "data"

st.title("📊 Monitor de Fenómenos Corruptivos Legales")
st.markdown("### Basado en la teoría del Ph.D. Vicente Humberto Monteverde [cite: 3]")

archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]
if not archivos:
    st.error("No hay datos. Corre primero 'diario.py'")
    st.stop()

archivo_selec = st.sidebar.selectbox("Reporte Diario", sorted(archivos, reverse=True))
df = pd.read_excel(os.path.join(DATA_DIR, archivo_selec))

# Métricas
m1, m2, m3 = st.columns(3)
m1.metric("Casos Analizados", len(df))
m2.metric("Riesgo Máximo", f"{df['indice_fenomeno_corruptivo'].max()}/10")
m3.metric("Fecha", datetime.now().strftime("%d/%m/%Y"))

st.write("### 🔍 Auditoría de Decisiones Estatales")
st.dataframe(df[["fecha", "tipo_decision", "transferencia", "indice_fenomeno_corruptivo", "nivel_riesgo_teorico", "link"]], use_container_width=True)

with st.expander("🔬 Fundamento Científico"):
    st.write("La teoría sostiene que la corrupción muta hacia formas legales mediante decisiones discrecionales del Estado[cite: 17, 20].")
    st.write("* **Impacto Social**: Redistribuciones inequitativas a favor de grupos de interés[cite: 8, 147].")
