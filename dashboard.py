import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="Fenómenos Corruptivos – Dashboard Teórico", layout="wide"
)

# Ajuste de ruta para entorno Docker o local
DATA_DIR = "/app/data" if os.path.exists("/app/data") else "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Buscar reportes generados
ARCHIVOS = [
    f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx") or f.endswith(".csv")
]

# ===============================
# HEADER
# ===============================
st.title("📉 Monitor de Fenómenos Corruptivos")
st.subheader("Implementación computacional de *The Great Corruption*")

st.markdown(f"""
Este sistema analiza **decisiones estatales legales** que, según la teoría económica del 
**Ph.D. Vicente Humberto Monteverde**, pueden generar **transferencias regresivas de ingresos**. 
No detecta delitos penales, sino la intensidad de fenómenos discrecionales.
""")

# ===============================
# CARGA Y ESTANDARIZACIÓN
# ===============================
if not ARCHIVOS:
    st.error(f"No se encontraron reportes en: {DATA_DIR}")
    st.stop()

archivo_selec = st.selectbox(
    "Seleccioná el reporte a visualizar:", sorted(ARCHIVOS, reverse=True)
)
ruta_completa = os.path.join(DATA_DIR, archivo_selec)

df = (
    pd.read_excel(ruta_completa)
    if archivo_selec.endswith(".xlsx")
    else pd.read_csv(ruta_completa)
)

# Mapeo de compatibilidad
mapeo = {
    "origen": "transferencia",
    "indice_total": "indice_fenomeno_corruptivo",
    "nivel_riesgo": "nivel_riesgo_teorico",
}
df = df.rename(columns=mapeo)

# Normalización de escala 0-10
if (
    "indice_fenomeno_corruptivo" in df.columns
    and df["indice_fenomeno_corruptivo"].max() > 10
):
    df["indice_fenomeno_corruptivo"] = (df["indice_fenomeno_corruptivo"] / 10).round(1)

# ===============================
# MÉTRICAS PRINCIPALES
# ===============================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Normas", len(df))
c2.metric(
    "Fenómenos Detectados",
    len(df[df["tipo_decision"] != "No identificado"])
    if "tipo_decision" in df.columns
    else 0,
)
c3.metric(
    "Índice Promedio",
    f"{df['indice_fenomeno_corruptivo'].mean():.1f}/10"
    if "indice_fenomeno_corruptivo" in df.columns
    else "N/D",
)
c4.metric(
    "Casos Riesgo Alto",
    len(df[df["nivel_riesgo_teorico"] == "Alto"])
    if "nivel_riesgo_teorico" in df.columns
    else 0,
)

# ===============================
# VISUALIZACIONES
# ===============================
st.divider()
col_g1, col_g2 = st.columns(2)

with col_g1:
    if "tipo_decision" in df.columns:
        st.write("### Distribución por Escenario Teórico")
        fig, ax = plt.subplots()
        df["tipo_decision"].value_counts().plot(kind="barh", ax=ax, color="skyblue")
        st.pyplot(fig)

with col_g2:
    if "nivel_riesgo_teorico" in df.columns:
        st.write("### Intensidad de Riesgo")
        fig, ax = plt.subplots()
        df["nivel_riesgo_teorico"].value_counts().plot(
            kind="pie", autopct="%1.1f%%", ax=ax, colors=["red", "orange", "green"]
        )
        ax.set_ylabel("")
        st.pyplot(fig)

# ===============================
# EXPLORADOR DE DATOS
# ===============================
st.divider()
st.header("🔍 Exploración de Decisiones Estatales")
cols_view = [
    "fecha",
    "tipo_decision",
    "transferencia",
    "indice_fenomeno_corruptivo",
    "nivel_riesgo_teorico",
    "link",
]
cols_finales = [c for c in cols_view if c in df.columns]

st.dataframe(
    df[cols_finales],
    use_container_width=True,
    column_config={
        "link": st.column_config.LinkColumn("Norma BORA"),
        "indice_fenomeno_corruptivo": st.column_config.ProgressColumn(
            "Intensidad", min_value=0, max_value=10
        ),
    },
)

# ===============================
# EXPLICACIÓN DE COLUMNAS (NUEVO)
# ===============================
st.divider()
with st.expander("📖 Glosario y Explicación de Variables"):
    st.markdown("""
    | Variable | Significado Teórico |
    | :--- | :--- |
    | **Tipo de Decisión** | Mapeo de la norma hacia los 7 escenarios de la teoría (Contratos, Tarifas, Jubilaciones, etc.). |
    | **Transferencia** | Identifica el sector que soporta el costo económico (Estado, Jubilados, Consumidores). |
    | **Índice Fenómeno** | Puntuación de 0 a 10 que mide el grado de discrecionalidad y potencial transferencia regresiva. |
    | **Nivel de Riesgo** | Evaluación cualitativa de la opacidad y el impacto social de la decisión. |
    """)

# ===============================
# FUNDAMENTO TEÓRICO (NUEVO)
# ===============================
st.header("🔬 Fundamentación Científica")
tabs = st.tabs(["Núcleo de la Teoría", "Escenarios Analizados", "Impacto Social"])

with tabs[0]:
    st.markdown("""
    **Gran Corrupción - Teoría de los Fenómenos Corruptivos** Esta teoría, formulada por el **Ph.D. Vicente Humberto Monteverde**, propone un cambio de paradigma: 
    la corrupción no solo son delitos penales (sobornos), sino decisiones **discrecionales y legales** que producen distribuciones inequitativas de ingresos.

    * **Búsqueda de Rentas (Rent Seeking):** El ingreso no se obtiene por el mercado, sino por subsidios o privilegios otorgados por el Estado.
    * **Legalidad como Escudo:** Es difícil de combatir porque ocurre dentro de la estructura normativa y ética vigente.
    """)

with tabs[1]:
    st.markdown("""
    El sistema identifica los **7 escenarios críticos** descritos en la obra original:
    1.  **Privatizaciones Subvaluadas:** Transferencia del Estado a empresas.
    2.  **Contratos Públicos Ineficientes:** Continuidad de obras sin análisis de opciones.
    3.  **Compensación por Devaluación:** Transferencia directa de consumidores a empresas.
    4.  **Aumentos Tarifarios Discrecionales:** Sin considerar el ajuste salarial de la población.
    5.  **Servicios Privados de Necesidad:** Aumentos en salud/educación sin considerar el ingreso disponible.
    6.  **Cálculo Previsional:** Transferencia de ingresos de jubilados hacia el Estado.
    7.  **Traslación Impositiva:** Cuando el Estado permite pasar impuestos corporativos al precio final del consumidor.
    """)

with tabs[2]:
    st.info(f"""
    **Referencia Académica:** Monteverde, V. H. (2020). *Great corruption – theory of corrupt phenomena*. Journal of Financial Crime.  
    🔗 [Acceder al artículo original en Emerald Insight](https://www.emerald.com/jfc/article-abstract/28/2/580/224032/Great-corruption-theory-of-corrupt-phenomena?redirectedFrom=fulltext)
    """)

st.caption(f"Última actualización del monitor: {datetime.now().strftime('%d/%m/%Y %H:%M')}")