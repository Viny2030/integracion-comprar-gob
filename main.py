import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from analisis import analizar_boletin, MATRIZ_TEORICA

# ===============================
# 1. CONFIGURACIÓN UI
# ===============================
st.set_page_config(page_title="Monitor de Fenómenos Corruptivos", layout="wide")

DATA_DIR = "data" if os.path.exists("data") else "/app/data"
DOC_FILE = "articulo_monteverde_español.docx"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# ===============================
# 2. FUNCIONES DE APOYO (SCRAPER)
# ===============================
def extraer_datos_comprar_gob():
    url = "https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10="
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        # Intenta localizar la tabla de licitaciones
        tabla = soup.find("table", {"id": "ctl00_CPH1_GridLicitaciones"})
        if not tabla:
            tabla = soup.find("table")

        if not tabla:
            return pd.DataFrame()

        rows = tabla.find_all("tr")
        datos = []
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) > 2:
                detalle_texto = cols[2].text.strip()
                link_tag = cols[2].find("a")
                link_aviso = (
                    "https://comprar.gob.ar" + link_tag["href"] if link_tag else url
                )

                datos.append(
                    {
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                        "detalle": detalle_texto,
                        "link": link_aviso,
                    }
                )
        return pd.DataFrame(datos)
    except Exception as e:
        st.error(f"Error de conexión con el portal: {e}")
        return pd.DataFrame()


# ===============================
# 3. HEADER Y ESTRUCTURA DE PESTAÑAS
# ===============================
st.title("📉 Monitor de Fenómenos Corruptivos")
st.subheader("Implementación de *The Great Corruption* - Ph.D. Monteverde")

# DEFINICIÓN ÚNICA DE PESTAÑAS
tab_monitor, tab_analisis, tab_documentacion = st.tabs(
    [
        "📊 Monitor Histórico",
        "🚀 Análisis Comprar.gob.ar",
        "📄 Documentación Científica",
    ]
)

# --- PESTAÑA 1: MONITOR ---
with tab_monitor:
    st.header("Visualización de Reportes")
    archivos = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]

    if not archivos:
        st.info("No se encontraron reportes en /data.")
    else:
        archivo_selec = st.selectbox(
            "Seleccioná un reporte:", sorted(archivos, reverse=True)
        )
        ruta = os.path.join(DATA_DIR, archivo_selec)

        try:
            xl = pd.ExcelFile(ruta)
            df = xl.parse(xl.sheet_names[0])
            df.columns = df.columns.astype(str).str.strip().str.lower()

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Normas", len(df))

            if "tipo_decision" in df.columns:
                df_id = df[df["tipo_decision"].str.lower() != "no identificado"]
                m2.metric("Fenómenos Detectados", len(df_id))

                if "indice_total" in df.columns:
                    df["indice_total"] = pd.to_numeric(
                        df["indice_total"], errors="coerce"
                    ).fillna(0)
                    m3.metric(
                        "Intensidad Promedio", f"{int(df['indice_total'].mean())}%"
                    )
                else:
                    m3.metric("Índice", "N/D")

                st.dataframe(df, use_container_width=True)

            st.divider()
            col_g, col_m = st.columns(2)
            with col_g:
                st.subheader("📖 Glosario")
                if "Glosario" in xl.sheet_names:
                    st.table(xl.parse("Glosario"))
                else:
                    st.caption("Glosario de respaldo (Archivo antiguo):")
                    st.table(
                        pd.DataFrame(
                            {
                                "Variable": ["tipo_decision", "transferencia"],
                                "Definición": ["Categoría teórica", "Sector afectado"],
                            }
                        )
                    )
            with col_m:
                st.subheader("🔬 Marco Teórico")
                resumen = [
                    {"Escenario": k, "Mecanismo": v["mecanismo"]}
                    for k, v in MATRIZ_TEORICA.items()
                ]
                st.table(pd.DataFrame(resumen))

        except Exception as e:
            st.error(f"Error: {e}")

# --- PESTAÑA 2: SCRAPER ---
with tab_analisis:
    st.header("🔗 Conexión Real: Comprar.gob.ar")
    st.markdown(
        "Este botón extrae licitaciones vigentes y las clasifica según la matriz de algoritmos."
    )

    if st.button("🚀 Scraper: Analizar Licitaciones en Vivo"):
        with st.spinner("Extrayendo datos del portal de compras..."):
            df_portal = extraer_datos_comprar_gob()

            if not df_portal.empty:
                st.write(f"Se encontraron **{len(df_portal)}** procesos para analizar.")
                df_res, path_excel, _ = analizar_boletin(df_portal)

                if path_excel:
                    st.success(
                        f"Análisis completado. Archivo: {os.path.basename(path_excel)}"
                    )
                    st.dataframe(df_res)
            else:
                st.warning(
                    "No se capturaron datos. El portal puede estar caído o requiere validación de sesión."
                )

# --- PESTAÑA 3: DOCUMENTACIÓN ---
with tab_documentacion:
    st.header("Fundamentación Académica")
    st.markdown("""
    El sistema identifica transferencias regresivas basadas en los 7 escenarios de la Gran Corrupción:
    - Privatizaciones y Concesiones.
    - Contratos de Obra Pública.
    - Tarifas y Servicios.
    - Cálculo Previsional, etc.
    """)

    if os.path.exists(DOC_FILE):
        with open(DOC_FILE, "rb") as f:
            st.download_button(
                label="📥 Descargar Artículo Ph.D. Monteverde (ES)",
                data=f,
                file_name=DOC_FILE,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    else:
        st.error(f"Archivo {DOC_FILE} no encontrado en la raíz.")