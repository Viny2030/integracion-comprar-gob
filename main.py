import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import logging
import time
import analisis  # <--- Importamos el otro script

# --- CONFIGURACIÓN ---
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Definimos las secciones que queremos scrapear
SECCIONES_INTERES = ["primera", "tercera"]
FECHA_OBJETIVO = datetime.now().strftime("%Y%m%d")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}

KEYWORDS_TEORIA = [
    "tarifas", "concesión", "privatización", "subsidio",
    "deuda pública", "fideicomiso", "ajuste", "jubilaciones",
    "impuesto", "exención", "obra pública", "licitación",
    "redeterminación de precios", "compra directa", "adjudicación"
]


def obtener_boletin(url):
    logging.info(f"Conectando con BORA: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Error de conexión: {e}")
        return None


def parsear_normas(html, seccion_nombre):
    # Guardamos debug específico por sección
    debug_path = os.path.join(DATA_DIR, f"debug_page_{seccion_nombre}.html")
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write(html)
    logging.info(f"🔍 HTML de '{seccion_nombre}' guardado en {debug_path}")

    soup = BeautifulSoup(html, "html.parser")
    normas_list = []

    links = soup.find_all("a", href=True)
    logging.info(f"   -> Se encontraron {len(links)} enlaces en {seccion_nombre}.")

    for link in links:
        href = link.get("href", "")
        # Filtramos por tipos de enlaces comunes en 1ra y 3ra sección
        if "DetalleNorma" in href or "detalleAviso" in href:
            try:
                detalle = link.get_text(strip=True)
                full_link = (
                    f"https://www.boletinoficial.gob.ar{href}"
                    if href.startswith("/")
                    else href
                )
                posible_fenomeno = any(kw in detalle.lower() for kw in KEYWORDS_TEORIA)

                normas_list.append(
                    {
                        "Fecha": FECHA_OBJETIVO,
                        "Seccion": seccion_nombre,
                        "Organismo": "Ver Detalle",
                        "Detalle": detalle,
                        "Link": full_link,
                        "Alerta": posible_fenomeno,
                    }
                )
            except:
                continue

    return normas_list


if __name__ == "__main__":
    datos_totales = []

    # --- BUCLE PRINCIPAL POR SECCIONES ---
    for seccion in SECCIONES_INTERES:
        url_seccion = f"https://www.boletinoficial.gob.ar/seccion/{seccion}/{FECHA_OBJETIVO}"

        html = obtener_boletin(url_seccion)

        if html:
            nuevos_datos = parsear_normas(html, seccion)
            datos_totales.extend(nuevos_datos)
            logging.info(f"   -> Extraídos {len(nuevos_datos)} registros de {seccion}.")
        else:
            logging.error(f"Fallo al obtener sección: {seccion}")

        # Pausa de cortesía entre secciones
        time.sleep(2)

    # --- GUARDADO Y ANÁLISIS ---
    if datos_totales:
        df = pd.DataFrame(datos_totales)
        filename = f"bora_{FECHA_OBJETIVO}.csv"
        filepath = os.path.join(DATA_DIR, filename)

        # Guardamos utf-8-sig para que Excel abra bien los acentos
        df.to_csv(filepath, index=False, encoding="utf-8-sig")

        logging.info(f"✅ CSV TOTAL generado correctamente con {len(df)} filas: {filepath}")

        # --- EL PUENTE MÁGICO ---
        logging.info("🚀 Ejecutando análisis automático...")
        try:
            analisis.analizar_boletin()
        except Exception as e:
            logging.error(f"Error durante el análisis: {e}")
    else:
        logging.warning("⚠️ No se encontraron datos en ninguna sección.")