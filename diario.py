import os
import shutil
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from analisis import analizar_boletin

# ==========================================
# CONFIGURACIÓN DE RUTAS CON ARCHIVADO MENSUAL
# ==========================================
DATA_DIR = "data"

def obtener_directorio_mes_actual():
    """
    Crea y retorna el directorio del mes actual en formato YYYY-MM
    Ejemplo: data/2026-02/
    """
    ahora = datetime.now()
    mes_carpeta = ahora.strftime("%Y-%m")
    ruta_mes = os.path.join(DATA_DIR, mes_carpeta)

    if not os.path.exists(ruta_mes):
        os.makedirs(ruta_mes)
        print(f"📁 Creada nueva carpeta mensual: {ruta_mes}")

    return ruta_mes

# Asegurar que el directorio base existe
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ==========================================
# PASO 1 Y 2: SCRAPER DE COMPRAR.GOB.AR
# ==========================================
def extraer_licitaciones():
    print("🔍 Conectando con Comprar.gob.ar...")
    url = "https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")

        # Intentar localizar la tabla principal
        tabla = soup.find("table", {"id": "ctl00_CPH1_GridLicitaciones"})
        if not tabla:
            tabla = soup.find("table")

        if not tabla:
            print("❌ No se encontró la tabla de licitaciones.")
            return pd.DataFrame()

        rows = tabla.find_all("tr")
        datos = []

        for row in rows[1:]:  # Omitir encabezado
            cols = row.find_all("td")
            if len(cols) > 4:
                nro_proceso = cols[1].text.strip()
                detalle_texto = cols[2].text.strip()
                tipo_proceso = cols[3].text.strip()
                fecha_apertura = cols[4].text.strip()

                link_tag = cols[2].find("a")
                link_completo = "https://comprar.gob.ar" + link_tag["href"] if link_tag else url

                datos.append({
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "nro_proceso": nro_proceso,
                    "detalle": detalle_texto,
                    "tipo_proceso": tipo_proceso,
                    "fecha_apertura": fecha_apertura,
                    "link": link_completo,
                    "fuente": "Scraper Automático Comprar",
                })

        print(f"✅ Éxito: Se extrajeron {len(datos)} procesos del portal.")
        return pd.DataFrame(datos)

    except Exception as e:
        print(f"❌ Error en Scraping: {e}")
        return pd.DataFrame()

# ==========================================
# PASO 3: ANÁLISIS Y GENERACIÓN DE REPORTE
# ==========================================
def ejecutar_robot():
    start_time = datetime.now()
    print(f"\n--- INICIO PROCESO DIARIO: {start_time.strftime('%Y-%m-%d %H:%M')} ---")

    directorio_mes = obtener_directorio_mes_actual()
    df_portal = extraer_licitaciones()

    if df_portal.empty:
        print("⚠️ No se obtuvieron datos. Generando registro de control vacío.")
        df_portal = pd.DataFrame([{
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "detalle": "Sin datos detectados en el portal",
            "link": "n/a",
            "tipo_proceso": "n/a",
            "fecha_apertura": "n/a",
        }])
    else:
        df_portal["detalle"] = df_portal["detalle"].fillna("Sin descripción")

    print("🧠 Aplicando Matriz de Análisis XAI (Ph.D. Monteverde)...")

    # Intentar enviar los datos al análisis con manejo de archivado inteligente
    try:
        # Intento 1: Análisis con carpeta de destino (Requiere actualización en analisis.py)
        df_final, path_excel, _ = analizar_boletin(df_portal, directorio_mes)
    except TypeError:
        # Intento 2: Fallback si analisis.py no acepta el segundo parámetro
        print("⚠️ Nota: Usando modo compatibilidad (analisis.py antiguo).")
        df_final, path_excel, _ = analizar_boletin(df_portal)

        # Si el archivo quedó en 'data/' raíz, moverlo a la carpeta del mes
        if path_excel and os.path.exists(path_excel):
            nombre_archivo = os.path.basename(path_excel)
            nueva_ruta = os.path.join(directorio_mes, nombre_archivo)
            shutil.move(path_excel, nueva_ruta)
            path_excel = nueva_ruta
            print(f"📦 Archivo organizado en: {path_excel}")

    # Resultados Finales
    if path_excel and os.path.exists(path_excel):
        print(f"\n✨ REPORTE GENERADO: {path_excel}")
        if "indice_total" in df_final.columns:
            top_riesgo = df_final.sort_values(by="indice_total", ascending=False).head(3)
            print("\n🚨 ALERTAS DE MAYOR RIESGO DETECTADAS:")
            print(top_riesgo[["detalle", "indice_total"]])
    else:
        print("❌ Error crítico: El reporte no pudo ser generado.")

    print(f"\n⏱️ Tiempo total: {(datetime.now() - start_time).seconds} segundos.")
    print("--- FIN DEL PROCESO ---")

if __name__ == "__main__":
    ejecutar_robot()
