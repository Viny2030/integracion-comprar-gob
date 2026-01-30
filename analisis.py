import pandas as pd
import os
import unicodedata
from datetime import datetime

# Directorio de datos compatible con Docker y local
DATA_DIR = "/app/data" if os.path.exists("/app") else os.path.join(os.getcwd(), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# MATRIZ TEÓRICA - Ph.D. Vicente Humberto Monteverde [cite: 53, 149]
MATRIZ_TEORICA = {
    "Privatización / Concesión": {"keywords": ["concesion", "privatizacion", "venta de pliegos", "subvaluacion"], "transferencia": "Estado a Privados", "peso": 9.0},
    "Obra Pública / Contratos": {"keywords": ["obra publica", "licitacion", "contratacion directa", "sobreprecio", "redeterminacion"], "transferencia": "Estado a Empresas", "peso": 8.5},
    "Tarifas Servicios Públicos": {"keywords": ["cuadro tarifario", "aumento de tarifa", "revision tarifaria", "peaje"], "transferencia": "Usuarios a Concesionarias", "peso": 7.5},
    "Precios de Consumo Regulados": {"keywords": ["precios justos", "canasta basica", "viveres", "alimento"], "transferencia": "Consumidores a Productores", "peso": 6.5},
    "Salarios y Paritarias": {"keywords": ["paritaria", "salario minimo", "ajuste salarial", "convenio colectivo"], "transferencia": "Asalariados a Empleadores", "peso": 5.5},
    "Jubilaciones / Pensiones": {"keywords": ["movilidad jubilatoria", "haber minimo", "anses", "ajuste previsional"], "transferencia": "Jubilados al Estado", "peso": 10.0},
    "Traslado de Impuestos": {"keywords": ["iva", "ingresos brutos", "doble imposicion", "presion tributaria"], "transferencia": "Contribuyentes al Estado", "peso": 9.5},
}

REGLAS_CLASIFICACION = MATRIZ_TEORICA

def limpiar_texto_curado(texto):
    if not isinstance(texto, str): return ""
    texto = texto.lower()
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")

def analizar_boletin(df):
    if df.empty: return df, None, pd.DataFrame()
    df = df.copy()
    df["texto_clean"] = df["detalle"].apply(limpiar_texto_curado)
    df["tipo_decision"] = "No identificado"
    df["transferencia"] = "No identificado"
    df["indice_fenomeno_corruptivo"] = 0.0

    for categoria, info in MATRIZ_TEORICA.items():
        mask = df["texto_clean"].str.contains("|".join(info["keywords"]), na=False)
        df.loc[mask, "tipo_decision"] = categoria
        df.loc[mask, "transferencia"] = info["transferencia"]
        df.loc[mask, "indice_fenomeno_corruptivo"] = info["peso"]

    def evaluar_riesgo(score):
        if score >= 8: return "Alto"
        if score >= 5: return "Medio"
        return "Bajo"

    df["nivel_riesgo_teorico"] = df["indice_fenomeno_corruptivo"].apply(evaluar_riesgo)
    fecha_str = datetime.now().strftime("%Y%m%d")
    path = os.path.join(DATA_DIR, f"reporte_fenomenos_{fecha_str}.xlsx")
    df.to_excel(path, index=False)
    return df, path, pd.DataFrame()
