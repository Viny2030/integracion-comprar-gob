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

# PESTAÑAS DE NAVEGACIÓN EN SIDEBAR
st.sidebar.divider()
st.sidebar.subheader("📑 Navegación")
pagina = st.sidebar.radio(
    "Seleccione una sección:",
    ["📊 Dashboard Principal", "📖 Instructivo de Uso"],
    label_visibility="collapsed",
)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]

# ===============================
# PÁGINA DE INSTRUCTIVO
# ===============================
if pagina == "📖 Instructivo de Uso":
    st.title("📖 Instructivo de Uso del Dashboard")
    st.markdown("### Guía completa para utilizar el Monitor de Fenómenos Corruptivos")

    st.divider()

    col_inst1, col_inst2 = st.columns([2, 1])

    with col_inst1:
        st.markdown("""
        ## 📘 Contenido del Instructivo

        Este documento incluye información detallada sobre:

        ✅ **Introducción a la Teoría de Monteverde**  
        Conceptos fundamentales sobre fenómenos corruptivos legales

        ✅ **Requisitos Previos**  
        Software y dependencias necesarias para ejecutar el sistema

        ✅ **Estructura de Archivos**  
        Organización del proyecto y ubicación de datos

        ✅ **Guía de Ejecución**  
        Pasos detallados para iniciar el dashboard

        ✅ **Componentes del Dashboard**  
        Explicación de cada sección y gráfico

        ✅ **Los 7 Escenarios Corruptivos**  
        Descripción detallada de cada escenario según la teoría

        ✅ **Interpretación de Resultados**  
        Cómo leer y entender los análisis generados

        ✅ **Recursos Adicionales**  
        Referencias y material complementario
        """)

    with col_inst2:
        st.info("""
        **📄 Formato:**  
        Microsoft Word (.docx)

        **📏 Páginas:**  
        Documento completo de múltiples páginas

        **🎯 Público:**  
        Usuarios técnicos y no técnicos

        **📅 Actualización:**  
        Versión vigente
        """)

    st.divider()

    # Botón de descarga del instructivo
    instructivo_path = "instructivo_dashboard.docx"
    if os.path.exists(instructivo_path):
        with open(instructivo_path, "rb") as file:
            st.download_button(
                label="⬇️ DESCARGAR INSTRUCTIVO COMPLETO (Word)",
                data=file,
                file_name="Instructivo_Monitor_Fenomenos_Corruptivos.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
    else:
        st.warning("⚠️ El instructivo no está disponible. Contacte al administrador.")

    st.divider()

    st.markdown("""
    ### 🎥 Vista Previa Rápida

    #### 1️⃣ Ejecutar el Dashboard
    ```bash
    streamlit run dashboard.py
    ```

    #### 2️⃣ Seleccionar Reporte Diario
    Use el selector en la barra lateral para elegir el archivo de análisis.

    #### 3️⃣ Explorar Análisis
    Navegue por las diferentes secciones para obtener insights detallados.

    #### 4️⃣ Descargar Datos
    Exporte reportes y el artículo académico original.
    """)

    st.success(
        "💡 **Consejo**: Descargue el instructivo completo para tener toda la información disponible offline."
    )

    # Detener ejecución aquí para no mostrar el resto del dashboard
    st.stop()

# ===============================
# DASHBOARD PRINCIPAL (solo si NO está en página de instructivo)
# ===============================

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

st.caption(
    f"Sistema validado - Ph.D. Vicente Humberto Monteverde | Ejecución: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
)

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

# ===============================
# ANÁLISIS AVANZADOS - TEORÍA MONTEVERDE
# ===============================
st.divider()
st.markdown("## 📈 Análisis Avanzados de Fenómenos Corruptivos")

# ===============================
# 1. ANÁLISIS TEMPORAL DE ACUMULACIÓN
# ===============================
st.write("### ⏱️ Análisis de Acumulación Temporal de Fenómenos")
col_temp1, col_temp2 = st.columns(2)

with col_temp1:
    if not df_detectados.empty:
        # Agrupar por tipo de decisión y contar
        acumulacion = (
            df_detectados.groupby("tipo_decision").size().reset_index(name="cantidad")
        )
        acumulacion = acumulacion.sort_values("cantidad", ascending=False)

        fig_acum = px.bar(
            acumulacion,
            x="cantidad",
            y="tipo_decision",
            orientation="h",
            title="Frecuencia de Fenómenos por Escenario Teórico",
            labels={"cantidad": "Cantidad de Casos", "tipo_decision": "Escenario"},
            color="cantidad",
            color_continuous_scale="Reds",
        )
        st.plotly_chart(fig_acum, use_container_width=True)
    else:
        st.info("No hay datos para analizar acumulación temporal")

with col_temp2:
    if not df_detectados.empty:
        # Calcular intensidad promedio por escenario
        intensidad_prom = (
            df_detectados.groupby("tipo_decision")["indice_fenomeno_corruptivo"]
            .mean()
            .reset_index()
        )
        intensidad_prom = intensidad_prom.sort_values(
            "indice_fenomeno_corruptivo", ascending=False
        )

        fig_int = px.bar(
            intensidad_prom,
            x="indice_fenomeno_corruptivo",
            y="tipo_decision",
            orientation="h",
            title="Intensidad Promedio por Escenario",
            labels={
                "indice_fenomeno_corruptivo": "Intensidad Promedio",
                "tipo_decision": "Escenario",
            },
            color="indice_fenomeno_corruptivo",
            color_continuous_scale="Oranges",
        )
        st.plotly_chart(fig_int, use_container_width=True)

# ===============================
# 2. MATRIZ DE RIESGO Y TRANSFERENCIA
# ===============================
st.write("### 🎯 Matriz de Riesgo: Intensidad vs Transferencia Económica")

if not df_detectados.empty:
    # Crear matriz de riesgo
    col_matriz1, col_matriz2 = st.columns([2, 1])

    with col_matriz1:
        fig_scatter = px.scatter(
            df_detectados,
            x="indice_fenomeno_corruptivo",
            y="transferencia",
            color="nivel_riesgo_teorico",
            size="indice_fenomeno_corruptivo",
            hover_data=["tipo_decision"],
            color_discrete_map={
                "Alto": "#EF553B",
                "Medio": "#FECB52",
                "Bajo": "#636EFA",
            },
            title="Distribución de Fenómenos: Intensidad vs Dirección de Transferencia",
            labels={
                "indice_fenomeno_corruptivo": "Índice de Intensidad",
                "transferencia": "Dirección de Transferencia Económica",
            },
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_matriz2:
        st.markdown("#### 📊 Estadísticas de Transferencia")

        # Calcular estadísticas por dirección de transferencia
        for transferencia in df_detectados["transferencia"].unique():
            df_trans = df_detectados[df_detectados["transferencia"] == transferencia]
            st.markdown(f"**{transferencia}:**")
            st.metric("Casos Detectados", len(df_trans), delta=None)
            st.metric(
                "Intensidad Promedio",
                f"{df_trans['indice_fenomeno_corruptivo'].mean():.1f}/10",
                delta=None,
            )
            st.divider()

# ===============================
# 3. ANÁLISIS DE CONCENTRACIÓN DE RIESGO
# ===============================
st.write("### 🔥 Concentración de Riesgo por Nivel Teórico")

if not df_detectados.empty:
    col_conc1, col_conc2, col_conc3 = st.columns(3)

    # Calcular métricas por nivel de riesgo
    riesgo_stats = (
        df_detectados.groupby("nivel_riesgo_teorico")
        .agg({"indice_fenomeno_corruptivo": ["count", "mean", "sum"]})
        .reset_index()
    )

    riesgo_stats.columns = ["nivel_riesgo", "cantidad", "promedio", "total_acumulado"]

    with col_conc1:
        if "Alto" in riesgo_stats["nivel_riesgo"].values:
            alto = riesgo_stats[riesgo_stats["nivel_riesgo"] == "Alto"].iloc[0]
            st.metric(
                "🔴 Riesgo ALTO",
                f"{int(alto['cantidad'])} casos",
                delta=f"Intensidad: {alto['promedio']:.1f}",
            )
        else:
            st.metric("🔴 Riesgo ALTO", "0 casos")

    with col_conc2:
        if "Medio" in riesgo_stats["nivel_riesgo"].values:
            medio = riesgo_stats[riesgo_stats["nivel_riesgo"] == "Medio"].iloc[0]
            st.metric(
                "🟡 Riesgo MEDIO",
                f"{int(medio['cantidad'])} casos",
                delta=f"Intensidad: {medio['promedio']:.1f}",
            )
        else:
            st.metric("🟡 Riesgo MEDIO", "0 casos")

    with col_conc3:
        if "Bajo" in riesgo_stats["nivel_riesgo"].values:
            bajo = riesgo_stats[riesgo_stats["nivel_riesgo"] == "Bajo"].iloc[0]
            st.metric(
                "🔵 Riesgo BAJO",
                f"{int(bajo['cantidad'])} casos",
                delta=f"Intensidad: {bajo['promedio']:.1f}",
            )
        else:
            st.metric("🔵 Riesgo BAJO", "0 casos")

# ===============================
# 4. ÍNDICE DE CONCENTRACIÓN CORRUPTIVA (ICC)
# ===============================
st.write("### 📉 Índice de Concentración Corruptiva (ICC)")
st.markdown("""
El **ICC** mide la concentración de fenómenos corruptivos en escenarios específicos.
Un ICC alto indica que pocos escenarios concentran la mayoría de los casos detectados.
""")

if not df_detectados.empty:
    col_icc1, col_icc2 = st.columns([3, 1])

    with col_icc1:
        # Calcular ICC usando concentración
        casos_por_escenario = (
            df_detectados.groupby("tipo_decision").size().sort_values(ascending=False)
        )
        total_casos = len(df_detectados)

        # Calcular porcentaje acumulado
        pct_acumulado = (casos_por_escenario.cumsum() / total_casos * 100).reset_index()
        pct_acumulado.columns = ["tipo_decision", "porcentaje_acumulado"]
        pct_acumulado["numero_escenario"] = range(1, len(pct_acumulado) + 1)

        fig_icc = px.line(
            pct_acumulado,
            x="numero_escenario",
            y="porcentaje_acumulado",
            markers=True,
            title="Curva de Concentración de Fenómenos (Pareto)",
            labels={
                "numero_escenario": "Número de Escenarios",
                "porcentaje_acumulado": "% Acumulado de Casos",
            },
        )

        # Agregar línea de referencia (distribución uniforme)
        fig_icc.add_shape(
            type="line",
            x0=0,
            y0=0,
            x1=len(casos_por_escenario),
            y1=100,
            line=dict(color="red", dash="dash"),
            name="Distribución Uniforme",
        )

        st.plotly_chart(fig_icc, use_container_width=True)

    with col_icc2:
        st.markdown("#### 📊 Interpretación")

        # Calcular si sigue el principio 80-20
        if len(casos_por_escenario) > 0:
            top_escenarios = casos_por_escenario.head(
                max(1, len(casos_por_escenario) // 5)
            )
            concentracion_top = top_escenarios.sum() / total_casos * 100

            st.metric(
                "Concentración Top 20%",
                f"{concentracion_top:.1f}%",
                delta="del total de casos",
            )

            if concentracion_top >= 80:
                st.error(
                    "⚠️ **ALTA CONCENTRACIÓN**: Pocos escenarios concentran la mayoría de fenómenos"
                )
            elif concentracion_top >= 60:
                st.warning(
                    "⚡ **CONCENTRACIÓN MODERADA**: Distribución desigual de fenómenos"
                )
            else:
                st.success(
                    "✅ **BAJA CONCENTRACIÓN**: Fenómenos distribuidos entre escenarios"
                )

# ===============================
# 5. RECOMENDACIONES SEGÚN TEORÍA
# ===============================
st.write("### 💡 Recomendaciones Basadas en la Teoría de Monteverde")

if not df_detectados.empty:
    st.markdown("""
    Basándose en los fenómenos detectados en este reporte diario, se identifican las siguientes áreas de atención prioritaria:
    """)

    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        st.markdown("#### 🎯 Escenarios de Mayor Riesgo")
        # Top 3 escenarios por intensidad promedio
        top_riesgo = (
            df_detectados.groupby("tipo_decision")["indice_fenomeno_corruptivo"]
            .mean()
            .sort_values(ascending=False)
            .head(3)
        )

        for i, (escenario, intensidad) in enumerate(top_riesgo.items(), 1):
            st.markdown(
                f"{i}. **{escenario}**: Intensidad promedio {intensidad:.1f}/10"
            )

    with col_rec2:
        st.markdown("#### 📊 Direcciones de Transferencia")
        # Distribución de transferencias
        trans_dist = df_detectados["transferencia"].value_counts()

        for transferencia, cantidad in trans_dist.items():
            porcentaje = (cantidad / len(df_detectados) * 100)
            st.markdown(f"• **{transferencia}**: {cantidad} casos ({porcentaje:.1f}%)")

    st.info("""
    **Según la teoría de Monteverde**, estos fenómenos corruptivos son **legales** pero generan 
    **transferencias regresivas de ingresos**, afectando la distribución económica y la equidad social. 
    La detección temprana permite visibilizar estas decisiones discrecionales del Estado.
    """)