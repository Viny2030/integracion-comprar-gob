import os
import pandas as pd
from datetime import datetime

# 1. Configuración de ruta robusta
# Si existe la carpeta /app/data (entorno Docker), la usa.
# Si no, usa 'data' en el directorio actual.
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def ejecutar_raspado_bora():
    """
    Obtención de datos enfocada en las áreas críticas
    de la teoría de fraude y corrupción.
    """
    print(f"Iniciando proceso para el día: {datetime.now().strftime('%Y-%m-%d')}")

    # Simulación de datos (Aquí puedes integrar tu lógica de BeautifulSoup/Selenium)
    # Se enfoca en Secciones Críticas según tu investigación
    data = [
        {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "seccion": "Sección Segunda",
            "detalle": "ADJUDICACIÓN DIRECTA: Análisis de posibles irregularidades en contrataciones.",
            "link": "https://www.boletinoficial.gob.ar/seccion/segunda",
        },
        {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "seccion": "Sección Primera",
            "detalle": "NORMATIVA: Nuevas regulaciones tarifarias detectadas.",
            "link": "https://www.boletinoficial.gob.ar/seccion/primera",
        },
    ]

    df = pd.DataFrame(data)

    # 2. Definición de nombre de archivo consistente
    # Usamos el formato 'reporte_fenomenos_YYYYMMDD.xlsx' para que coincida con tus archivos previos
    file_name = f"reporte_fenomenos_{datetime.now().strftime('%Y%m%d')}.xlsx"
    path_completo = os.path.join(DATA_DIR, file_name)

    # 3. Guardado en formato Excel (.xlsx)
    # Importante: Esto requiere la librería 'openpyxl' (ya incluida en tu YAML)
    try:
        df.to_excel(path_completo, index=False)
        print(f"Éxito: Archivo generado en {path_completo}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

    return df

if __name__ == "__main__":
    ejecutar_raspado_bora()