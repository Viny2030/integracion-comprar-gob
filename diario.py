import os
import pandas as pd
import requests
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
    mes_carpeta = ahora.strftime("%Y-%m")  # Formato: 2026-02
    ruta_mes = os.path.join(DATA_DIR, mes_carpeta)

    # Crear la estructura de directorios si no existe
    if not os.path.exists(ruta_mes):
        os.makedirs(ruta_mes)
        print(f"📁 Creada nueva carpeta mensual: {ruta_mes}")

    return ruta_mes


# Crear directorio base si no existe
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# ==========================================
# PASO 1 Y 2: SCRAPER DE COMPRAR.GOB.AR
# ==========================================
def extraer_licitaciones():
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
            if len(cols) > 3:  # Verificamos que tenga suficientes columnas
                # Mapeo de columnas basado en la estructura del portal
                nro_proceso = cols[1].text.strip()
                detalle_texto = cols[2].text.strip()
                tipo_proceso = cols[3].text.strip()  # Captura Licitación/Contratación

                link_tag = cols[2].find("a")
                link_completo = (
                    "https://comprar.gob.ar" + link_tag["href"] if link_tag else url
                )

                datos.append(
                    {
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                        "nro_proceso": nro_proceso,
                        "detalle": detalle_texto,
                        "tipo_proceso": tipo_proceso,  # Columna clave para la matriz
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
    start_time = datetime.now()
    print(f"--- INICIO PROCESO DIARIO: {start_time.strftime('%Y-%m-%d %H:%M')} ---")

    # Obtener el directorio del mes actual para archivado automático
    directorio_mes = obtener_directorio_mes_actual()
    print(f"📂 Directorio de almacenamiento: {directorio_mes}")

    # Ejecución de Pasos 1 y 2: Recolección
    df_portal = extraer_licitaciones()

    if df_portal.empty:
        print("No se obtuvieron datos. Generando reporte de control vacío.")
        df_portal = pd.DataFrame(
            [
                {
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "detalle": "Sin datos detectados en el portal",
                    "link": "n/a",
                    "tipo_proceso": "n/a",
                }
            ]
        )

    # Ejecución de Paso 3: Cruce y Análisis con Matriz XAI
    # Aquí es donde se aplican los 7 escenarios de la Gran Corrupción
    print("Aplicando Matriz de Análisis XAI (Ph.D. Monteverde)...")

    # Aseguramos que la columna detalle no tenga nulos para el análisis
    df_portal["detalle"] = df_portal["detalle"].fillna("Sin descripción")

    # MODIFICACIÓN: Pasar el directorio del mes a analizar_boletin
    # Si analisis.py no acepta este parámetro, ver instrucciones más abajo
    try:
        df_final, path_excel, _ = analizar_boletin(df_portal, directorio_mes)
    except TypeError:
        # Si analizar_boletin no acepta directorio_destino, usar versión antigua
        print(
            "⚠️ NOTA: analisis.py necesita actualización para soportar archivado mensual"
        )
        print("   Guardando temporalmente en carpeta raíz de data/")
        df_final, path_excel, _ = analizar_boletin(df_portal)

        # Mover el archivo generado al directorio del mes
        if path_excel and os.path.exists(path_excel):
            import shutil

            nombre_archivo = os.path.basename(path_excel)
            nueva_ruta = os.path.join(directorio_mes, nombre_archivo)
            shutil.move(path_excel, nueva_ruta)
            path_excel = nueva_ruta
            print(f"📦 Archivo movido a: {path_excel}")

    if path_excel:
        print(f"✅ REPORTE GENERADO EXITOSAMENTE: {path_excel}")
        # Opcional: imprimir los 3 casos con mayor índice detectados
        if "indice_total" in df_final.columns:
            top_riesgo = df_final.sort_values(by="indice_total", ascending=False).head(
                3
            )
            print("Top Alertas detectadas:")
            print(top_riesgo[["detalle", "indice_total"]])
    else:
        print("❌ Error al generar el reporte final.")

    # Información del archivado
    print(f"📦 Reporte archivado en: {directorio_mes}")
    print(f"⏱️ Tiempo de ejecución: {(datetime.now() - start_time).seconds} segundos")


if __name__ == "__main__":
    ejecutar_robot()


# ==========================================
# INSTRUCCIONES PARA ACTUALIZAR analisis.py
# ==========================================
"""
MODIFICACIÓN NECESARIA EN analisis.py:

Buscar la función analizar_boletin y modificarla así:

ANTES:
------
def analizar_boletin(df):
    ...
    nombre_archivo = f"reporte_fenomenos_{datetime.now().strftime('%Y%m%d')}.xlsx"
    path_excel = os.path.join("data", nombre_archivo)
    ...
    return df_final, path_excel, timestamp

DESPUÉS:
--------
def analizar_boletin(df, directorio_destino="data"):
    ...
    nombre_archivo = f"reporte_fenomenos_{datetime.now().strftime('%Y%m%d')}.xlsx"
    path_excel = os.path.join(directorio_destino, nombre_archivo)  # <-- CAMBIO AQUÍ
    ...
    return df_final, path_excel, timestamp

SOLO SE CAMBIA:
1. Agregar parámetro: directorio_destino="data"
2. Usar ese parámetro en lugar de "data" hardcodeado

Si NO puedes modificar analisis.py, el código actual de diario.py tiene
un fallback que moverá automáticamente el archivo al directorio correcto.
"""