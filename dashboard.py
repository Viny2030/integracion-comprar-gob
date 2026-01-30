import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# ===============================
# CONFIGURACIÓN Y ESTILO
# ===============================
st.set_page_config(page_title="Monitor de Gran Corrupción", layout="wide")

# Rutas compatibles con Docker y Local
DATA_DIR = "/app/data" if os.path.exists("/app/data") else "data"


# ===============================
# TRATAMIENTO DE DATOS (COMPATIBILIDAD SEGURA)
# ===============================
def cargar_y_limpiar(ruta):
    df = pd.read_excel(ruta)

    # Mapeo de nombres antiguos a nuevos para compatibilidad histórica
    mapeo = {
        "indice_total": "indice_fenomeno_corruptivo",
        "nivel_riesgo": "nivel_riesgo_teorico",
        "origen": "transferencia",
    }

    # RENOMBRADO SEGURO: Solo renombra si el nombre viejo existe y el nuevo NO
    # Esto evita el DuplicateError en archivos nuevos (como el del 30/1)
    for viejo, nuevo in mapeo.items():
        if viejo in df.columns and nuevo not in df.columns:
            df = df.rename(columns={viejo: nuevo})

    # SEGURIDAD EXTRA: Eliminar cualquier columna duplicada que venga del origen
    df = df.loc[:, ~df.columns.duplicated()]

    # Asegurar que existan las columnas críticas para que el dashboard no falle
    if "indice_fenomeno_corruptivo" not in df.columns:
        df["indice_fenomeno_corruptivo"] = 0.0
    if "tipo_decision" not in df.columns:
        df["tipo_decision"] = "No identificado"

    return df


# ===============================
# SIDEBAR Y SELECCIÓN DE REPORTES
# ===============================
st.sidebar.header("⚙️ Configuración")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]

if not archivos:
    st.error(
        "No se encontraron datos en la carpeta /data. Ejecute 'diario.py' primero."
    )
    st.stop()

# Ordenamos descendente para que el más nuevo (30/01/2026) aparezca primero
archivo_selec = st.sidebar.selectbox(
    "Seleccionar Reporte Diario", sorted(archivos, reverse=True)
)
ruta_completa = os.path.join(DATA_DIR, archivo_selec)
df = cargar_y_limpiar(ruta_completa)

# ===============================
# HEADER Y MÉTRICAS PRINCIPALES
# ===============================
st.title("⚖️ Monitor de Fenómenos Corruptivos Legales")
st.markdown(
    f"### Implementación de la Teoría del **Ph.D. Vicente Humberto Monteverde** [cite: 3]"
)

# Filtrar solo casos identificados para las métricas de riesgo
df_detectados = df[df["tipo_decision"] != "No identificado"]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Normas Analizadas", len(df))
m2.metric("Fenómenos Detectados", len(df_detectados))
m3.metric("Riesgo Máximo", f"{df['indice_fenomeno_corruptivo'].max()}/10")
# Extraer fecha del nombre del archivo (ej: reporte_fenomenos_20260130.xlsx)
fecha_label = archivo_selec.split("_")[-1].split(".")[0]
m4.metric("Fecha del Reporte", fecha_label)

st.divider()

# ===============================
# VISUALIZACIÓN INTERACTIVA (PLOTLY)
# ===============================
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.write("### 📊 Intensidad por Escenario Teórico")
    if not df_detectados.empty:
        fig_bar = px.bar(
            df_detectados,
            x="indice_fenomeno_corruptivo",
            y="tipo_decision",
            color="nivel_riesgo_teorico",
            orientation="h",
            color_discrete_map={
                "Alto": "#EF553B",  # Rojo
                "Medio": "#FECB52",  # Naranja
                "Bajo": "#636EFA",  # Azul
            },
            labels={
                "indice_fenomeno_corruptivo": "Índice de Intensidad (0-10)",
                "tipo_decision": "Escenario de la Teoría",
            },
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No hay fenómenos detectados para graficar en este reporte.")

with col_g2:
    st.write("### 💸 Sectores de Transferencia Regresiva")
    if not df_detectados.empty:
        fig_pie = px.pie(
            df_detectados,
            names="transferencia",
            hole=0.4,
            title="Distribución de Impacto Económico",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ===============================
# AUDITORÍA DETALLADA (TABLA)
# ===============================
st.write("### 🔍 Explorador de Decisiones Estatales (BORA/Comprar)")
cols_visibles = [
    "fecha",
    "tipo_decision",
    "transferencia",
    "indice_fenomeno_corruptivo",
    "nivel_riesgo_teorico",
    "link",
]
# Seleccionamos solo las columnas que existan para evitar errores de vista
df_display = df[[c for c in cols_visibles if c in df.columns]]

st.dataframe(
    df_display,
    use_container_width=True,
    column_config={
        "link": st.column_config.LinkColumn("Norma Original"),
        "indice_fenomeno_corruptivo": st.column_config.ProgressColumn(
            "Intensidad", min_value=0, max_value=10
        ),
    },
)

# ===============================
# FUNDAMENTO CIENTÍFICO (Citas académicas)
# ===============================
st.divider()
with st.expander("🔬 Fundamento Científico y Matriz XAI", expanded=False):
    st.markdown(f"""
    #### Núcleo de la Teoría
    La corrupción muta y se diversifica, volviéndose **legal** a través de decisiones discrecionales del Estado[cite: 17]. 
    Estos **fenómenos corruptivos** se basan en la legalidad pero producen situaciones de desigualdad económica e injusticia[cite: 19, 53].

    #### Los 7 Escenarios Críticos Analizados[cite: 148]:
    1. **Privatizaciones Subvaluadas**: Transferencia de patrimonio estatal a privados[cite: 158].
    2. **Contratos Públicos**: Continuidad de obras ineficientes o con sobreprecios[cite: 162, 164].
    3. **Tarifas y Devaluación**: Compensaciones discrecionales a concesionarias[cite: 167].
    4. **Servicios Públicos**: Ajustes tarifarios sin considerar el ingreso salarial[cite: 172].
    5. **Salud y Educación**: Aumentos autorizados en servicios básicos privados[cite: 175].
    6. **Cálculo Previsional**: Transferencia de ingresos de jubilados hacia el Estado (**Peso 10.0**)[cite: 179].
    7. **Traslación Impositiva**: Transferencia de impuestos empresariales a los consumidores[cite: 181].
    """)
    st.info(
        "Referencia Académica: Monteverde, V. H. (2020). Great corruption – theory of corrupt phenomena. Journal of Financial Crime. [cite: 11, 193]"
    )

st.caption(f"Sistema validado - Ph.D. Vicente Humberto Monteverde | Ejecución: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ===============================
# DESCARGA DEL ARTÍCULO ORIGINAL
# ===============================
st.divider()
articulo_path = "articulo_monteverde_español.docx"
if os.path.exists(articulo_path):
    with open(articulo_path, "rb") as file:
        st.download_button(
            label="📄 Descargar Artículo Original (Monteverde, 2020)",
            data=file,
            file_name="articulo_monteverde_español.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
else:
    st.warning("El artículo no está disponible en el directorio principal")
