import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from analisis import analizar_boletin

# 1. CONFIGURACIÓN DE RUTAS
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# ==========================================
# PASO 1 Y 2: SCRAPER DE COMPRAR.GOB.AR
# ==========================================
def extraer_licitaciones():
    """
    Función requerida por main.py para el análisis en vivo.
    Extrae procesos vigentes del portal Comprar.gob.ar.
    """
    print("Conectando con Comprar.gob.ar...")
    url = "https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")

        # Localización de la tabla de procesos
        tabla = soup.find("table", {"id": "ctl00_CPH1_GridLicitaciones"})
        if not tabla:
            tabla = soup.find("table")

        rows = tabla.find_all("tr")
        datos = []

        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) > 3:
                # Mapeo de columnas: Nro, Detalle, Tipo
                nro_proceso = cols[1].text.strip()
                detalle_texto = cols[2].text.strip()
                tipo_proceso = cols[3].text.strip()

                link_tag = cols[2].find("a")
                link_completo = (
                    "https://comprar.gob.ar" + link_tag["href"] if link_tag else url
                )

                datos.append(
                    {
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                        "nro_proceso": nro_proceso,
                        "detalle": detalle_texto,
                        "tipo_proceso": tipo_proceso,
                        "link": link_completo,
                        "fuente": "Scraper Automático Comprar",
                    }
                )

        print(f"Éxito: Se extrajeron {len(datos)} procesos del portal.")
        return pd.DataFrame(datos)

    except Exception as e:
        print(f"Error en Scraping: {e}")
        return pd.DataFrame()


# ==========================================
# PASO 3: ANÁLISIS Y GENERACIÓN DE REPORTE
# ==========================================
def ejecutar_robot():
    """
    Función principal ejecutada por GitHub Actions o Docker Compose.
    """
    start_time = datetime.now()
    print(f"--- INICIO PROCESO DIARIO: {start_time.strftime('%Y-%m-%d %H:%M')} ---")

    # Ejecución de Pasos 1 y 2
    df_portal = extraer_licitaciones()

    if df_portal.empty:
        print("No se obtuvieron datos. Generando entrada de control.")
        df_portal = pd.DataFrame(
            [
                {
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "detalle": "Sin datos detectados en el portal (Verificar conexión)",
                    "link": "n/a",
                    "tipo_proceso": "n/a",
                }
            ]
        )

    # Ejecución de Paso 3: Aplicación de Matriz XAI (Genera el Excel con Glosario)
    print("Aplicando Matriz de Análisis XAI (Ph.D. Monteverde)...")
    df_final, path_excel, _ = analizar_boletin(df_portal)

    if path_excel:
        print(f"✅ REPORTE GENERADO EXITOSAMENTE: {path_excel}")
    else:
        print("❌ Error crítico: No se pudo generar el archivo Excel.")

if __name__ == "__main__":
    ejecutar_robot()