import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time

# IMPORTAMOS TU CEREBRO CENTRAL
# Esto evita tener las reglas escritas dos veces.
# Si actualizas analisis.py, el robot se actualiza solo.
import analisis
from analisis import REGLAS_CLASIFICACION

# Configuración
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-419,es;q=0.9",
    "Connection": "keep-alive",
}

# --- LÓGICA DE CLASIFICACIÓN (Usando reglas importadas) ---


def clasificar_decision_estatal(texto: str) -> str:
    """
    Clasifica el texto usando el diccionario maestro importado de analisis.py
    """
    texto = texto.lower()
    # Usamos REGLAS_CLASIFICACION en lugar de redefinir el diccionario aquí
    for tipo, palabras in REGLAS_CLASIFICACION.items():
        if any(p in texto for p in palabras):
            return tipo
    return "No identificado"


def obtener_boletin(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        return response.text if response.status_code == 200 else None
    except Exception as e:
        print(f"Error conectando a {url}: {e}")
        return None


def parsear_normas(html, seccion_nombre, fecha_target):
    soup = BeautifulSoup(html, "html.parser")
    normas = []
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        # Filtros típicos del Boletín Oficial
        if any(x in href for x in ["DetalleNorma", "idNorma", "detalleAviso"]):
            detalle = link.get_text(strip=True)

            # Filtro básico de longitud para evitar ruido
            if len(detalle) > 15:
                tipo = clasificar_decision_estatal(detalle)
                normas.append(
                    {
                        "fecha": fecha_target,
                        "seccion": seccion_nombre,
                        "detalle": detalle,
                        "link": f"https://www.boletinoficial.gob.ar{href}"
                        if not href.startswith("http")
                        else href,
                        "tipo_decision": tipo,
                    }
                )
    return normas


# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print("--- INICIANDO ROBOT DIARIO (Auditoría Activada) ---")
    fecha_obj = datetime.now()
    fecha_str = fecha_obj.strftime("%Y%m%d")
    print(f"Fecha objetivo: {fecha_str}")

    registros = []
    secciones = ["primera", "tercera"]

    for seccion in secciones:
        url = f"https://www.boletinoficial.gob.ar/seccion/{seccion}/{fecha_str}"
        print(f"Escaneando: {seccion}...")
        html = obtener_boletin(url)

        if html:
            nuevos = parsear_normas(html, seccion, fecha_str)
            print(f"   -> Encontrados {len(nuevos)} items.")
            registros.extend(nuevos)
        else:
            print(f"   -> Sin respuesta del servidor para {seccion}.")
        time.sleep(2)

    if registros:
        print("\nProcesando datos con teoría 'Great Corruption' y Auditoría Ética...")
        df_raw = pd.DataFrame(registros)

        # Llamamos al módulo de análisis (que ahora limpia, audita y explica)
        df_proc, path, _ = analisis.analizar_boletin(df_raw)

        # --- MÉTRICAS DEL REPORTE ---
        fenomenos = len(df_proc[df_proc["tipo_decision"] != "No identificado"])

        # Contamos cuántas filas tienen una alerta de auditoría (que no sea "OK")
        revisiones = len(df_proc[df_proc["auditoria_estado"] != "OK"])

        print(f"\n=== RESUMEN DEL DÍA ===")
        print(f"   [+] Fenómenos Identificados: {fenomenos}")
        print(f"   [!] Casos que requieren Revisión Humana: {revisiones}")
        print(f"   [>] Reporte Excel generado: {path}")
        print("=======================")
    else:
        print("\nNo se encontraron registros relevantes hoy.")
        # -----------------------------------------------------