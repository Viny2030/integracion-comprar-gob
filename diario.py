import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from analisis import analizar_boletin

# CONFIGURACIÓN DE RUTAS
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def extraer_licitaciones():
    print("Conectando con Comprar.gob.ar...")
    url = "https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Buscamos cualquier tabla si el ID específico falla
        tabla = soup.find("table", {"id": "ctl00_CPH1_GridLicitaciones"}) or soup.find("table")
        if not tabla:
            return pd.DataFrame()

        rows = tabla.find_all("tr")
        datos = []
        
        for row in rows[1:]: 
            cols = row.find_all("td")
            if len(cols) > 3:
                # Ajuste de índices para asegurar captura de datos
                nro_proceso = cols[1].get_text(strip=True)
                detalle_texto = cols[2].get_text(strip=True)
                tipo_proceso = cols[3].get_text(strip=True)
                
                link_tag = cols[2].find("a")
                link_completo = "https://comprar.gob.ar" + link_tag["href"] if link_tag else url
                
                datos.append({
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "nro_proceso": nro_proceso,
                    "detalle": detalle_texto,
                    "tipo_proceso": tipo_proceso,
                    "link": link_completo,
                    "fuente": "Comprar.gob.ar"
                })
        
        return pd.DataFrame(datos)
    except Exception as e:
        print(f"Error en Scraping: {e}")
        return pd.DataFrame()

def ejecutar_robot():
    df_portal = extraer_licitaciones()
    
    if df_portal.empty:
        # Si falla el scraper, creamos una fila de control para no romper el dashboard
        df_portal = pd.DataFrame([{"fecha": datetime.now().strftime("%Y-%m-%d"), "detalle": "Sin datos detectados", "link": "n/a"}])

    # PROCESAMIENTO CON TU MATRIZ TEÓRICA
    df_final, path_excel, _ = analizar_boletin(df_portal)
    print(f"✅ Proceso terminado. Reporte en: {path_excel}")

if __name__ == "__main__":
    ejecutar_robot()
